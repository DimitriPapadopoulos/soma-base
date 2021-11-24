# -*- coding: utf-8 -*-
from soma.qt_gui.qt_backend import Qt




if __name__ == '__main__':
    import sys

    from soma.undefined import undefined
    from soma.controller import (
        Controller,
        field,
        List,
        Literal,
        file,
        directory,
        Union,
        Dict,
        Set
    ) 
    class MyController(Controller):
        s: str
        i: int
        ls: List[str]

    class C(Controller):
        x: field(type_=List[str])
        y: field(type_=List[str])
        z: field(type_=List[str])
        s: field(type_=str, group='string', label='the label')
        os: field(type_=str, optional=True, group='string')
        ls: field(type_=List[str], group='string')
        ols: field(type_=List[str], output=True, group='string')
        lls: field(type_=List[List[str]], label='list^2[str]', group='string')
        llls: field(type_=List[List[List[str]]], label='list^3[str]', group='string')

        i: field(type_=int, group='integer')
        oi: field(type_=int, optional=True, group='integer')
        li: field(type_=List[int], group='integer')
        oli: field(type_=List[int], output=True, group='integer')
        lli: field(type_=List[List[int]], label='list^2[int]', group='integer')
        llli: field(type_=List[List[List[int]]], label='list^3[int]', group='integer')

        n: field(type_=float, group='float')
        on: field(type_=float, optional=True, group='float')
        ln: field(type_=List[float], group='float') 
        oln: field(type_=List[float], output=True, group='float')
        lln: field(type_=List[List[float]], label='list^2[float]', group='float')
        llln: field(type_=List[List[List[float]]], label='list^3[float]', group='float')

        b: bool
        ob: field(type_=bool, output=True)
        lb: List[bool]
        olb: field(type_=List[bool], output=True)

        e: Literal['one', 'two', 'three']
        oe: field(type_=Literal['one', 'two', 'three'], output=True)
        le: List[Literal['one', 'two', 'three']]
        ole: field(type_=List[Literal['one', 'two', 'three']], output=True)
        
        f: file()
        of: file(write=True)
        lf: List[file()]
        olf: List[file(write=True)]
        
        d: directory()
        od: directory(write=True)
        ld: List[directory()]
        old: List[directory(write=True)]

        u: Union[str, List[str]]
        ou: field(type_=Union[str, List[str]], output=True)
        lu: List[Union[str, List[str]]]
        olu: field(type_=List[Union[str, List[str]]], output=True)

        m: Dict
        om: field(type_=dict, output=True)
        lm: List[dict]
        olm: field(type_=List[dict], output=True)
        mt: Dict[str, List[int]]

        l: list

        controller: field(type_=Controller, group='controller')
        list_controller: field(type_=List[Controller], group='controller')
        custom: field(type_=MyController, group='controller')
        list_custom: field(type_=List[MyController], group='controller')
        list2_custom: field(type_=List[List[MyController]], group='controller')

        Set: Set
        Set_str: Set[str]
        set: set

    app = Qt.QApplication(sys.argv)
    o = C()
    window1 = ControllerWidget(o)
    window1.show()
    window2 = ControllerWidget(o)
    window2.show()
    app.exec_()
    print('o.lli =', getattr(o, 'lli', undefined))

