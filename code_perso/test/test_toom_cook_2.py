from migen import *
from toom_cook_2 import *
from random import *

taille = 30840

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
                print("Get     a1 = {}".format((yield dut.a1)))
                print("Get     a2 = {}".format((yield dut.a2)))
                print("Get     b1 = {}".format((yield dut.b1)))
                print("Get     b2 = {}".format((yield dut.b2)))

                print("Get     a1b1 = {}".format((yield dut.a1b1)))
                print("Get     a2b2 = {}".format((yield dut.a2b2)))
                print("Get     a1a2 = {}".format((yield dut.a1a2)))
                print("Get     b1b2 = {}".format((yield dut.b1b2)))

                print("Get     pipe1_a1b1 = {}".format((yield dut.pipe1_a1b1)))
                print("Get     pipe1_a2b2 = {}".format((yield dut.pipe1_a2b2)))
                print("Get     pipe2_a1b2 = 0x{:x}".format((yield dut.pipe2_a1b1)))
                print("Get     pipe2_a2b2 = 0x{:x}".format((yield dut.pipe2_a2b2)))

                print("Get     temp1 = {}".format((yield dut.temp1)))
                print("Get     temp2 = 0x{:x}".format((yield dut.temp2)))
                """

                yield
                yield
                yield
                yield
                print("Get     ab = 0x{:x}\n".format((yield dut.ab)))
                



def main():
        toom_cook = Toom_Cook_2(taille)

        # This is a list of generators that will run in parallel
        generators = {
            "sys" : [ test(toom_cook)
                    ]
        }

        run_simulation(toom_cook, generators, clocks={"sys": 1e9/24e6}, vcd_name="sim.vcd")

if __name__ == "__main__":
    main()
