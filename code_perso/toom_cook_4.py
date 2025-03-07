from migen import *

class Toom_Cook_4(Module):

    def __init__(self, taille, div3, div5):

        self.a = Signal(taille)
        self.b = Signal(taille)
        self.ab = Signal(taille*2)

        a0 = Signal((taille+3)//4)
        a1 = Signal((taille+3)//4)
        a2 = Signal((taille+3)//4)
        a3 = Signal((taille+3)//4)
        self.comb += [
            a0.eq(self.a[: (taille+3)//4]),
            a1.eq(self.a[(taille+3)//4 : 2 * ((taille+3)//4)]),
            a2.eq(self.a[2 * ((taille+3)//4) : 3 * ((taille+3)//4)]),
            a3.eq(self.a[3 * ((taille+3)//4) :]),
        ]

        b0 = Signal((taille+3)//4)
        b1 = Signal((taille+3)//4)
        b2 = Signal((taille+3)//4)
        b3 = Signal((taille+3)//4)
        self.comb += [
            b0.eq(self.b[: (taille+3)//4]),
            b1.eq(self.b[(taille+3)//4 : 2 * ((taille+3)//4)]),
            b2.eq(self.b[2 * ((taille+3)//4) : 3 * ((taille+3)//4)]),
            b3.eq(self.b[3 * ((taille+3)//4) :]),
        ]
        
        # On prend les points 0 1 -1 -2 2 -4 inf

        maxi = pow(2,(taille+3)//4+7) #sert à opti la place, mais peut etre changer par un majorant
        A0 = Signal(max=maxi, min=-maxi)
        A1 = Signal(max=maxi, min=-maxi)
        A2 = Signal(max=maxi, min=-maxi)
        A3 = Signal(max=maxi, min=-maxi)
        A4 = Signal(max=maxi, min=-maxi)
        A5 = Signal(max=maxi, min=-maxi)
        A6 = Signal(max=maxi, min=-maxi)

        B0 = Signal(max=maxi, min=-maxi)
        B1 = Signal(max=maxi, min=-maxi)
        B2 = Signal(max=maxi, min=-maxi)
        B3 = Signal(max=maxi, min=-maxi)
        B4 = Signal(max=maxi, min=-maxi)
        B5 = Signal(max=maxi, min=-maxi)
        B6 = Signal(max=maxi, min=-maxi)

        maxi = pow(2,((taille+3)//4+7)*2)
        R0 = Signal(max=maxi, min=-maxi)
        R1 = Signal(max=maxi, min=-maxi)
        R2 = Signal(max=maxi, min=-maxi)
        R3 = Signal(max=maxi, min=-maxi)
        R4 = Signal(max=maxi, min=-maxi)
        R5 = Signal(max=maxi, min=-maxi)
        R6 = Signal(max=maxi, min=-maxi)

        r0 = Signal(max=maxi, min=-maxi)
        r1 = Signal(max=maxi, min=-maxi)
        r2 = Signal(max=maxi, min=-maxi)
        r3 = Signal(max=maxi, min=-maxi)
        r4 = Signal(max=maxi, min=-maxi)
        r5 = Signal(max=maxi, min=-maxi)
        r6 = Signal(max=maxi, min=-maxi)

        self.sync += [
            #first clock
            A0.eq(a0),
            A1.eq(a0 + a1 + a2 + a3),
            A2.eq(a0 - a1 + a2 - a3),
            A3.eq(a0 + (a1<<1) + (a2 <<2) + (a3 <<3)),
            A4.eq(a0 - (a1<<1) + (a2 <<2) - (a3 <<3)),
            A5.eq(a0 - (a1<<2) + (a2 <<4) - (a3 <<6)),
            A6.eq(a3),

            B0.eq(b0),
            B1.eq(b0 + b1 + b2 + b3),
            B2.eq(b0 - b1 + b2 - b3),
            B3.eq(b0 + (b1<<1) + (b2 <<2) + (b3 <<3)),
            B4.eq(b0 - (b1<<1) + (b2 <<2) - (b3 <<3)),
            B5.eq(b0 - (b1<<2) + (b2 <<4) - (b3 <<6)),
            B6.eq(b3),
  
            #second clock
            R0.eq(A0 * B0),
            R1.eq(A1 * B1),
            R2.eq(A2 * B2),
            R3.eq(A3 * B3),
            R4.eq(A4 * B4),
            R5.eq(A5 * B5),
            R6.eq(A6 * B6),

            #third clock
            r0.eq(R0),
            r1.eq(((45 * R0 + 96 * R1 - 160 * R2 - 10 * R3 + 30 * R4 - R5) >> 2) * div3 * div3 * div5 + 16 * R6),
            r2.eq((((-30 * R0 - 1 * R3 - 1 * R4) >> 3) + 2 * R1 + 2 * R2) * div3 + 4 * R6),
            r3.eq((((-45 * R0 + 7 * R3  - 27 * R4  + R5) >> 4) + 4 * R2)* div3 * div3 - 20 * R6),
            r4.eq(((((6 * R0 + 1 * R3 + 1 * R4) >> 2) - 1 * R1 - 1 * R2) >> 1) * div3 - 5 * R6),
            r5.eq(((45 * R0 - 24 * R1 - 40 * R2 + 5 * R3 + 15 * R4 - R5) >> 4) * div3 * div3 * div5 + 4 * R6),
            r6.eq(R6),

            #fourth clock
            self.ab.eq(r0 + (r1 << (taille+3)//4) + (r2 << 2*((taille+3)//4)) + (r3 << 3*((taille+3)//4)) + (r4 << taille) + (r5 << 5*((taille+3)//4)) + (r6 << 6*((taille+3)//4))),
        ]



