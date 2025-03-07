#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2021 Michael T. Mayers <michael@tweakoz.com>
# SPDX-License-Identifier: BSD-2-Clause

import math

from migen import *

from litex.gen import *

from litex.build.io import CRG

from litex_boards.platforms import digilent_nexys4

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.interconnect import wishbone

from litex.soc.integration.soc import colorer
from litex.soc.cores.video import VideoVGAPHY
from liteeth.phy.rmii import LiteEthPHYRMII

from controller import *


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst          = Signal()
        self.cd_sys       = ClockDomain()
        self.cd_sys2x     = ClockDomain()
        self.cd_sys2x_dqs = ClockDomain()
        self.cd_idelay    = ClockDomain()
        self.cd_eth       = ClockDomain()
        self.cd_vga       = ClockDomain()
        # # #

        self.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset") | self.rst)
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,     2*sys_clk_freq)
        pll.create_clkout(self.cd_sys2x_dqs, 2*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay,    200e6)
        pll.create_clkout(self.cd_eth,       50e6)
        pll.create_clkout(self.cd_vga,       40e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# CellularRAM (https://media.digikey.com/PDF/Data%20Sheets/Micron%20Technology%20Inc%20PDFs/MT45W8MW16BGX.pdf)

class CellularRAM(LiteXModule):
    def __init__(self, soc, platform):

        sys_clk_freq = soc.sys_clk_freq

        addr_width = 23
        data_width = 16

        delay_for_70ns = (70e-9) / (1.0/sys_clk_freq)
        delay_for_70ns = int(math.ceil(delay_for_70ns))+1

        #print("sys_clk_freq<%g> delay_for_70ns<%g>\n"%(sys_clk_freq,delay_for_70ns))

        self.bus = wishbone.Interface(data_width=data_width,adr_width=addr_width)

        self.delaycounter = Signal(5)

        cellram = platform.request("cellularram")
        addr = cellram.addr
        data = cellram.data
        wen = cellram.wen
        oen = cellram.oen
        cen = cellram.cen
        clk = cellram.clk
        cre = cellram.cre
        adv = cellram.adv # address valid (low)
        lb = cellram.lb
        ub = cellram.ub
        ########################
        tristate_data = TSTriple(data_width)
        self.specials += tristate_data.get_tristate(data)
        ########################
        i_rst = ResetSignal("sys")
        fsm = FSM(reset_state="RESET")
        fsm = ResetInserter()(fsm)
        self.fsm = fsm
        self.sync += fsm.reset.eq(i_rst)
        ########################
        fsm.act("RESET",
            NextState("INIT"))
        ########################
        fsm.act("INIT",
            NextValue(self.delaycounter,0),
            NextValue(self.bus.ack,0),
            NextValue(cen,1),
            NextValue(adv,1),
            NextValue(lb,1),
            NextValue(ub,1),
            NextValue(clk,0),
            NextValue(cre,0),
            NextValue(tristate_data.oe,0),
            NextState("IDLE"))
        ########################
        fsm.act("IDLE",
            If(self.bus.stb & self.bus.cyc,

                NextValue(lb,~self.bus.sel[0]), 
                NextValue(ub,~self.bus.sel[1]),

                NextValue(self.delaycounter,0),
                NextValue(cen,0),
                NextValue(adv,0),
                NextValue(addr,self.bus.adr[:addr_width]),
                If(self.bus.we,
                    NextValue(wen,0),
                    NextValue(oen,1),
                    NextValue(tristate_data.oe,1),
                    NextValue(tristate_data.o,self.bus.dat_w[:data_width]),
                    NextState("WRITE")
                ).Else(
                    NextValue(wen,1),
                    NextValue(oen,0),
                    NextValue(tristate_data.oe,0),
                    NextState("READ")
                )
            )
        )
        ########################
        fsm.act("WRITE",
            NextValue(self.delaycounter,self.delaycounter+1),
            If(self.delaycounter==delay_for_70ns,
                NextValue(self.bus.ack,1),
                NextState("INIT"))
        )
        ########################
        fsm.act("READ",
            NextValue(self.delaycounter,self.delaycounter+1),
            NextValue(self.bus.dat_r,tristate_data.i[:data_width]),
            If(self.delaycounter==delay_for_70ns,
                NextValue(self.bus.ack,1),
                NextState("INIT"))
        )
        ########################

def addCellularRAM(soc, platform, name, origin):
    size = 16 * MEGABYTE
    ram_bus = wishbone.Interface(data_width=soc.bus.data_width)
    ram     = CellularRAM(soc,platform)
    soc.bus.add_slave(name, ram.bus, SoCRegion(origin=origin, size=size, mode="rw"))
    soc.check_if_exists(name)
    soc.logger.info("CELLULARRAM {} {} {}.".format(
        colorer(name),
        colorer("added", color="green"),
        soc.bus.regions[name]))
    setattr(soc.submodules, name, ram)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=75e6,
        with_led_chaser        = False,
        with_ethernet          = False,
        with_etherbone         = False,
        with_video_terminal    = False,
        with_video_framebuffer = False,
        **kwargs):
        platform = digilent_nexys4.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------_-----------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Nexys4", **kwargs)

        # Cellular RAM -------------------------------------------------------------------------------
        addCellularRAM(self,platform,"main_ram", 0x40000000)

        #Application
        taille = 42
        M = pow(2,((taille+3)//4+7)*2+1)

        div3 = 7891
        div5 = 999999999999999

        '''
        for x in range(1, M):
                if ((3 * x) % M == 1):
                        div3 = x
                
                if ((5 * x) % M == 1):
                        div5 = x

                if (div3!=0 & div5!=0):
                        break
        '''
        
        controller = Controller(taille, div3, div5)
        
        self.submodules.controller_calc = controller
        self.add_csr("controller_calc")

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.ethphy = LiteEthPHYRMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)

        # Video ------------------------------------------------------------------------------------
        if with_video_terminal or with_video_framebuffer:
            self.videophy = VideoVGAPHY(platform.request("vga"), clock_domain="vga")
            if with_video_terminal:
                self.add_video_terminal(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")
            if with_video_framebuffer:
                self.add_video_framebuffer(phy=self.videophy, timings="800x600@60Hz", clock_domain="vga")

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=digilent_nexys4.Platform, description="LiteX SoC on Nexys4.")
    parser.add_target_argument("--sys-clk-freq", default=75e6, type=float, help="System clock frequency.")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",         action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone",        action="store_true", help="Enable Etherbone support.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",        action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",            action="store_true", help="Enable SDCard support.")
    viopts = parser.target_group.add_mutually_exclusive_group()
    viopts.add_argument("--with-video-terminal",    action="store_true", help="Enable Video Terminal (VGA).")
    viopts.add_argument("--with-video-framebuffer", action="store_true", help="Enable Video Framebuffer (VGA).")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq           = args.sys_clk_freq,
        with_ethernet          = args.with_ethernet,
        with_etherbone         = args.with_etherbone,
        with_video_terminal    = args.with_video_terminal,
        with_video_framebuffer = args.with_video_framebuffer,
        **parser.soc_argdict
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
