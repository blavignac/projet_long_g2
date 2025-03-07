from migen import *

class Toom_Cook_2(Module):

    def __init__(self, taille):
        self.a = Signal(taille)
        self.b = Signal(taille)
        self.ab = Signal(taille*2)

        a1 = Signal((taille+1)//2)
        a2 = Signal((taille+1)//2)
        self.comb += [
            a1.eq(self.a[:(taille+1)//2]),
            a2.eq(self.a[(taille+1)//2:]),
        ]

        b1 = Signal((taille+1)//2)
        b2 = Signal((taille+1)//2)
        self.comb += [
            b1.eq(self.b[:(taille+1)//2]),
            b2.eq(self.b[(taille+1)//2:]),
        ]

        a1b1 = Signal(taille)
        a2b2 = Signal(taille)

        pipe1_a1b1 = Signal(taille)
        pipe1_a2b2 = Signal(taille)

        pipe2_a1b1 = Signal(taille)
        pipe2_a2b2 = Signal(taille)

        a1a2 = Signal((taille+1)//2+1)
        b1b2 = Signal((taille+1)//2+1)

        temp1 = Signal(taille+2)        
        temp2 = Signal(taille)

        self.sync += [
            # first clock
            a1b1.eq(a1 * b1),
            a2b2.eq(a2 * b2),
            a1a2.eq(a1 + a2),
            b1b2.eq(b1 + b2),

            # second clock
            temp1.eq(a1a2 * b1b2),
            pipe1_a1b1.eq(a1b1),
            pipe1_a2b2.eq(a2b2),

            # third clock
            temp2.eq(temp1 - pipe1_a1b1 - pipe1_a2b2),
            pipe2_a1b1.eq(pipe1_a1b1),
            pipe2_a2b2.eq(pipe1_a2b2),

            #fourth clock
            self.ab.eq(pipe2_a1b1 + (temp2<<((taille+1)//2)) + (pipe2_a2b2<<taille)),
        ]



