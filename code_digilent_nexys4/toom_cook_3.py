from migen import *

class Toom_Cook_3(Module):

    def __init__(self, taille, div3):


        self.a = Signal(taille)
        self.b = Signal(taille)
        self.ab = Signal(taille*2)

        a0 = Signal((taille+2)//3)
        a1 = Signal((taille+2)//3)
        a2 = Signal((taille+2)//3)
        self.comb += [
            a0.eq(self.a[:(taille+2)//3]),
            a1.eq(self.a[(taille+2)//3:2*(taille+2)//3]),
            a2.eq(self.a[2*((taille+2)//3):]),
        ]

        b0 = Signal((taille+2)//3)
        b1 = Signal((taille+2)//3)
        b2 = Signal((taille+2)//3)
        self.comb += [
            b0.eq(self.b[:(taille+2)//3]),
            b1.eq(self.b[(taille+2)//3:2*((taille+2)//3)]),
            b2.eq(self.b[2*((taille+2)//3):]),
        ]
        
        # On prend les points 0 1 -1 -2 inf

        maxi = pow(2,(taille+2)//3+3) #sert à opti la place, mais peut etre changer par un majorant
        A0 = Signal(max=maxi, min=-maxi)
        A1 = Signal(max=maxi, min=-maxi)
        A2 = Signal(max=maxi, min=-maxi)
        A3 = Signal(max=maxi, min=-maxi)
        A4 = Signal(max=maxi, min=-maxi)
        
        B0 = Signal(max=maxi, min=-maxi)
        B1 = Signal(max=maxi, min=-maxi)
        B2 = Signal(max=maxi, min=-maxi)
        B3 = Signal(max=maxi, min=-maxi)
        B4 = Signal(max=maxi, min=-maxi)

        maxi = pow(2,((taille+2)//3+3)*2)
        R0 = Signal(max=maxi, min=-maxi)
        R1 = Signal(max=maxi, min=-maxi)
        R2 = Signal(max=maxi, min=-maxi)
        R3 = Signal(max=maxi, min=-maxi)
        R4 = Signal(max=maxi, min=-maxi)

        r0 = Signal(max=maxi, min=-maxi)
        r1 = Signal(max=maxi, min=-maxi)
        r2 = Signal(max=maxi, min=-maxi)
        r3 = Signal(max=maxi, min=-maxi)
        r4 = Signal(max=maxi, min=-maxi)

        self.sync += [
            #first clock
            A0.eq(a0),
            A1.eq(a0 + a1 + a2),
            A2.eq(a0 - a1 + a2),
            A3.eq(a0 - (a1<<1) + (a2 <<2)),
            A4.eq(a2),

            B0.eq(b0),
            B1.eq(b0 + b1 + b2),
            B2.eq(b0 - b1 + b2),
            B3.eq(b0 - (b1<<1) + (b2 <<2)),
            B4.eq(b2),
  
            #second clock
            R0.eq(A0 * B0),
            R1.eq(A1 * B1),
            R2.eq(A2 * B2),
            R3.eq(A3 * B3),
            R4.eq(A4 * B4),

            #third clock
            r0.eq(R0),
            r1.eq(((3 * R0 + 2 * R1 - 6 * R2 + R3 - 12 * R4)>>1)*div3),
            r2.eq((- 2 * R0 + R1 + R2 - 2 * R4)>>1),
            r3.eq(((- 3 * R0 + R1 + 3 * R2 - R3 + 12 * R4)>>1)*div3),
            r4.eq(R4),

            #fourth clock
            self.ab.eq(r0 + (r1 << (taille+2)//3) + (r2 << 2*((taille+2)//3)) + (r3 << taille) + (r4 << 4*((taille+2)//3))),
        ]



