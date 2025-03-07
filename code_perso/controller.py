from migen import *
from toom_cook_2 import *
from toom_cook_3 import *
from toom_cook_4 import *

from litex.soc.interconnect.csr import AutoCSR, CSRStorage

class Controller(Module, AutoCSR):
    
    def __init__(self, taille, div3, div5):
        self.toom_cook  = CSRStorage(2,          reset=0x400000)
        self.a          = CSRStorage(taille,     reset=0x400100)
        self.b          = CSRStorage(taille,     reset=0x400200)
        self.ab         = CSRStorage(taille * 2, reset=0x400300)
        '''
        toom_2 = Toom_Cook_2(taille)
        toom_3 = Toom_Cook_3(taille,div3)
        toom_4 = Toom_Cook_4(taille,div3,div5)
        
        
        toom_2 = Toom_Cook_2(taille)
        toom_3 = Toom_Cook_2(taille)
        toom_4 = Toom_Cook_2(taille)
        

        toom_2 = Toom_Cook_3(taille,div3)
        toom_3 = Toom_Cook_3(taille,div3)
        toom_4 = Toom_Cook_3(taille,div3)
        '''

        toom_2 = Toom_Cook_4(taille,div3,div5)
        toom_3 = Toom_Cook_4(taille,div3,div5)
        toom_4 = Toom_Cook_4(taille,div3,div5)

        self.sync+=[
            If(self.toom_cook.storage==1,
            toom_2.a.eq(self.a.storage),
            toom_2.b.eq(self.b.storage)
            ).Elif(self.toom_cook.storage==2,
            toom_3.a.eq(self.a.storage),
            toom_3.b.eq(self.b.storage)
            ).Elif(self.toom_cook.storage==3,
            toom_4.a.eq(self.a.storage),
            toom_4.b.eq(self.b.storage)
            ),
        ]

        pipe1 = Signal(2)
        pipe2 = Signal(2)
        pipe3 = Signal(2)
        pipe4 = Signal(2)
        pipe5 = Signal(2)
        pipe6 = Signal(2)

        self.sync+=[
            pipe1.eq(self.toom_cook.storage),
            pipe2.eq(pipe1),
            pipe3.eq(pipe2),
            pipe4.eq(pipe3),
            pipe5.eq(pipe4),
            pipe6.eq(pipe5),

            If(pipe6==1,
            self.ab.storage.eq(toom_2.ab)
            ).Elif(pipe6==2,
            self.ab.storage.eq(toom_3.ab)
            ).Elif(pipe6==3,
            self.ab.storage.eq(toom_4.ab)
            ),
        ]



