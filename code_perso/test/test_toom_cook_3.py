from migen import *
from toom_cook_3 import *
from random import *

taille =12

def change_input(dut):
        a = randrange(pow(2,taille))
        yield dut.a.eq(a)
        print("Set      a = 0x{:x}".format(a))

        b = randrange(pow(2,taille))
        yield dut.b.eq(b)
        print("Set      b = 0x{:x}".format(b))
        yield

def test(dut):
        for i in range(6) :
                yield from change_input(dut)
                """
                print("Get     a0 = {}".format((yield dut.a0)))
                print("Get     a1 = {}".format((yield dut.a1)))
                print("Get     a2 = {}".format((yield dut.a2)))
                print("Get     b0 = {}".format((yield dut.b0)))
                print("Get     b1 = {}".format((yield dut.b1)))
                print("Get     b2 = {}\n".format((yield dut.b2)))
                yield

                print("Get     A0 = {}".format((yield dut.A0)))
                print("Get     A1 = {}".format((yield dut.A1)))
                print("Get     A2 = {}".format((yield dut.A2)))
                print("Get     A3 = {}".format((yield dut.A3)))
                print("Get     A4 = {}".format((yield dut.A4)))

                print("Get     B0 = {}".format((yield dut.B0)))
                print("Get     B1 = {}".format((yield dut.B1)))
                print("Get     B2 = {}".format((yield dut.B2)))
                print("Get     B3 = {}".format((yield dut.B3)))
                print("Get     B4 = {}\n".format((yield dut.B4)))
                yield

                print("Get     R0 = {}".format((yield dut.R0)))
                print("Get     R1 = {}".format((yield dut.R1)))
                print("Get     R2 = {}".format((yield dut.R2)))
                print("Get     R3 = {}".format((yield dut.R3)))
                print("Get     R4 = {}\n".format((yield dut.R4)))
                yield
                
                print("Get     r0 = {}".format((yield dut.r0)))
                print("Get     r1 = {}".format((yield dut.r1)))
                print("Get     r2 = {}".format((yield dut.r2)))
                print("Get     r3 = {}".format((yield dut.r3)))
                print("Get     r4 = {}\n".format((yield dut.r4)))
                yield
                """

                yield
                yield
                yield
                yield

                print("Get     ab = 0x{:x}\n".format((yield dut.ab)))
                



def main():

        div3 = 0
        M = pow(2, 2*((taille+2)//3+3)+1)
        for x in range(1, M):
                if ((3 * x) % M == 1):
                        div3 = x
                        break
                        
        toom_cook = Toom_Cook_3(taille, div3)

        # This is a list of generators that will run in parallel
        generators = {
            "sys" : [ test(toom_cook)
                    ]
        }

        run_simulation(toom_cook, generators, clocks={"sys": 1e9/24e6}, vcd_name="sim.vcd")

if __name__ == "__main__":
    main()
