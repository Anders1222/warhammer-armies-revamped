"""Build WAR's original vector rule diagrams. Run from any working directory.

Only the standard library is required. Geometry is in design units; SVG keeps
the print output sharp at any scale. The diagrams contain no raster content.
"""
from pathlib import Path
from html import escape
import json
import math

ROOT = Path(__file__).resolve().parent
INK = '#30291f'
PAPER = '#f5f0e5'
EDGE = '#b5a58a'
GHOST = '#887b68'
BLUE = '#5c8798'
RED = '#984f56'
GOLD = '#d6b45e'
PALE_BLUE = '#dce7e8'
PALE_RED = '#ebdcdb'
STONE = '#c9c6bc'
WHITE = '#fffdf6'
MANIFEST = []


def attrs(**kw):
    return ' '.join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"'
                    for k, v in kw.items() if v is not None)


class Diagram:
    def __init__(self, number, title, w=600, h=600):
        self.number, self.title, self.w, self.h = number, title, w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
                      f'<title id="title">{escape(title)}</title>',
                      '<desc id="desc">Warhammer Armies Revamped rules diagram. Blue and red bases distinguish the opposing forces; arrowheads show facing. Dashed outlines show previous positions.</desc>',
                      f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>']
        self.rect(3, 3, w-6, h-6, PAPER, EDGE, 1.5, rx=8)
        self.line(20, 49, w-20, 49, color=EDGE, sw=1)
        self.text(w/2, 34 if number==527 else 31, title.upper(), 32 if number==527 else 18, spacing=2)

    def add(self, tag, **kw):
        self.parts.append(f'<{tag} {attrs(**kw)}/>')

    def group(self, transform):
        self.parts.append(f'<g transform="{transform}">')

    def end(self):
        self.parts.append('</g>')

    def rect(self, x, y, w, h, fill='none', stroke=INK, sw=1.8, **kw):
        self.add('rect', x=x, y=y, width=w, height=h, fill=fill, stroke=stroke, stroke_width=sw, **kw)

    def line(self, x1, y1, x2, y2, color=INK, sw=2, dash=None, arrow=False, both=False):
        self.add('line', x1=x1, y1=y1, x2=x2, y2=y2, stroke=color, stroke_width=sw,
                 stroke_dasharray=dash, marker_end='url(#arrow)' if arrow else None,
                 marker_start='url(#arrow)' if both else None)

    def path(self, d, fill='none', stroke=INK, sw=2, dash=None, arrow=False):
        self.add('path', d=d, fill=fill, stroke=stroke, stroke_width=sw, stroke_linejoin='round',
                 stroke_linecap='round', stroke_dasharray=dash, marker_end='url(#arrow)' if arrow else None)

    def circle(self, x, y, r, fill=WHITE, stroke=INK, sw=2, **kw):
        self.add('circle', cx=x, cy=y, r=r, fill=fill, stroke=stroke, stroke_width=sw, **kw)

    def text(self, x, y, s, size=26, color=INK, anchor='middle', rotate=None, spacing=None):
        self.parts.append(f'<text {attrs(x=x, y=y, fill=color, font_family="Libertinus Serif, Georgia, serif", font_size=size, text_anchor=anchor, letter_spacing=spacing, transform=f"rotate({rotate} {x} {y})" if rotate else None)}>{escape(str(s))}</text>')

    def badge(self, x, y, s):
        self.circle(x, y, 17, INK, INK, 1)
        self.text(x, y+7, s, 23, WHITE)

    def divide(self, x1, y1, x2, y2):
        self.line(x1, y1, x2, y2, EDGE, 1.5)

    def unit(self, x, y, cols, rows, side='blue', cell=36, ch=None, facing='up', angle=0,
             ghost=False, missing=(), special=None):
        ch = cell if ch is None else ch
        self.group(f'translate({x} {y}) rotate({angle})')
        fill = BLUE if side == 'blue' else RED
        for row in range(rows):
            for col in range(cols):
                if (col, row) in missing:
                    continue
                px, py = col*cell, row*ch
                self.rect(px, py, cell, ch, PAPER if ghost else fill, GHOST if ghost else INK,
                          1.3, stroke_dasharray='4 3' if ghost else None)
                if not ghost:
                    # A fine inset edge and a clear facing chevron, readable in monochrome.
                    self.line(px+3, py+ch-3, px+cell-3, py+ch-3, color=WHITE, sw=0.65)
                colr = GHOST if ghost else WHITE
                cx, cy = px+cell/2, py+ch/2
                turns = {'up':0, 'right':90, 'down':180, 'left':270}
                self.group(f'translate({cx} {cy}) rotate({turns[facing]})')
                a = min(cell, ch)
                self.path(f'M {-a*.25} {-a*.22} L 0 {-a*.37} L {a*.25} {-a*.22}', stroke=colr, sw=1.8)
                self.end()
                if special and (col,row) in special:
                    self.crown(px+cell/2, py+ch*.57, min(cell,ch)*.6)
        self.end()

    def crown(self, x, y, size=24, hollow=False):
        self.path(f'M {x-size/2} {y-size*.35} L {x-size*.23} {y-size*.05} L {x} {y-size*.48} L {x+size*.23} {y-size*.05} L {x+size/2} {y-size*.35} L {x+size*.35} {y+size*.35} L {x-size*.35} {y+size*.35} Z', WHITE if hollow else GOLD, INK, 1.2)

    def character(self, x, y, w=36, h=36, angle=0, hollow=False):
        self.group(f'translate({x} {y}) rotate({angle})')
        self.rect(0, 0, w, h, WHITE if hollow else BLUE)
        self.crown(w/2, h/2, min(w,h)*.76, hollow)
        self.end()

    def cross(self, x, y, size=20, color=INK):
        self.line(x-size/2, y-size/2, x+size/2, y+size/2, color, 3)
        self.line(x+size/2, y-size/2, x-size/2, y+size/2, color, 3)

    def highlight(self, x, y, w, h, dotted=False):
        self.rect(x-2, y-2, w+4, h+4, 'none', INK, 5)
        self.rect(x-2, y-2, w+4, h+4, 'none', WHITE, 3, stroke_dasharray='5 4' if dotted else None)

    def dimension(self, x1, y1, x2, y2, label, tx=None, ty=None):
        self.line(x1, y1, x2, y2, arrow=True, both=True)
        a = math.atan2(y2-y1, x2-x1)
        dx, dy = -math.sin(a)*7, math.cos(a)*7
        for x,y in [(x1,y1),(x2,y2)]:
            self.line(x-dx,y-dy,x+dx,y+dy,sw=1.5)
        self.text((x1+x2)/2 if tx is None else tx, (y1+y2)/2-10 if ty is None else ty, label, 30)

    def die(self, x, y, n, size=35, angle=0):
        self.group(f'translate({x} {y}) rotate({angle})')
        self.rect(0, 0, size, size, WHITE, INK, 1.8, rx=5)
        spots={1:[(1,1)],2:[(0,0),(2,2)],3:[(0,0),(1,1),(2,2)],4:[(0,0),(0,2),(2,0),(2,2)],5:[(0,0),(0,2),(1,1),(2,0),(2,2)],6:[(0,0),(0,1),(0,2),(2,0),(2,1),(2,2)]}
        if isinstance(n, int):
            for a,b in spots[n]:
                self.circle(size*(.23+.27*a),size*(.23+.27*b),size*.07,INK,INK,0)
        elif n == 'hit':
            self.circle(size/2,size/2,size*.27,'none',INK,1.5)
            self.line(size*.5,size*.12,size*.5,size*.88,sw=1.5)
            self.line(size*.12,size*.5,size*.88,size*.5,sw=1.5)
        else:
            self.line(size*.25,size*.7,size*.75,size*.3,arrow=True)
        self.end()

    def rock(self, x, y, w, h, angle=0):
        self.group(f'translate({x} {y}) rotate({angle})')
        self.path(f'M {w*.08} {h*.35} Q {w*.22} {-h*.05} {w*.55} {h*.04} Q {w*.95} {h*.12} {w*.98} {h*.6} Q {w*.88} {h*1.1} {w*.48} {h*.96} Q {-w*.04} {h*.8} {w*.08} {h*.35} Z', STONE, INK, 2)
        self.path(f'M {w*.2} {h*.48} L {w*.4} {h*.22} L {w*.66} {h*.3} M {w*.48} {h*.78} L {w*.75} {h*.67}',stroke=EDGE,sw=1.5)
        self.end()

    def cannon(self, x, y, angle=0, kind='cannon'):
        self.group(f'translate({x} {y}) rotate({angle})')
        # Muzzle faces up; wheels, carriage and barrel are original vector symbols.
        self.rect(-20,-5,40,44,EDGE,INK,2,rx=3)
        for a in [-30,22]:
            self.rect(a,2,8,34,INK,INK,1,rx=2)
            self.line(a+4,7,a+4,31,color=GOLD,sw=1)
        if kind == 'bolt':
            self.path('M -36 -16 Q 0 15 36 -16 M -36 -16 L 0 3 L 36 -16',stroke=INK,sw=3)
            self.line(0,30,0,-35,arrow=True,sw=3)
        elif kind == 'stone':
            self.rect(-24,-30,48,64,'none',INK,4)
            self.path('M -24 24 L 22 -23 M -24 -23 L 24 24',stroke=INK,sw=3)
            self.line(0,35,0,-48,sw=8)
            self.circle(0,-48,12,GOLD,INK,3)
        else:
            self.rect(-9,-50,18,66,INK,INK,2,rx=3)
            self.line(-5,-45,-5,5,color=GOLD,sw=2)
            self.rect(-12,-52,24,6,INK,INK,1)
        self.end()

    def save(self, directory=ROOT):
        self.parts.append('</svg>')
        name = f'img-{self.number:04}.svg'
        (directory/name).write_text('\n'.join(self.parts)+'\n', encoding='utf-8')
        MANIFEST.append(dict(file=name,title=self.title,width=self.w,height=self.h))


def arcs(d, x, y, w, h, labels=True):
    for sx,sy,dx,dy in [(x,y,-1,-1),(x+w,y,1,-1),(x,y+h,-1,1),(x+w,y+h,1,1)]:
        t=min(sx-25 if dx<0 else d.w-25-sx, sy-65 if dy<0 else d.h-25-sy)
        d.line(sx,sy,sx+dx*t,sy+dy*t,dash='8 7',color=GHOST)
    if labels:
        d.text(d.w/2,150,'Forward',31)
        d.text(d.w/2,d.h-90,'Rear',31)
        d.text(83,d.h/2+12,'Flank',29,rotate=-90)
        d.text(d.w-83,d.h/2+12,'Flank',29,rotate=90)


def movement():
    d=Diagram(424,'Measuring distances')
    d.unit(60,95,5,4,'red',36,facing='down')
    d.unit(235,410,5,4,cell=36)
    d.unit(442,228,1,1,'red',78,facing='down',angle=28)
    d.dimension(228,247,228,399,'6″',185,332)
    d.dimension(427,333,389,398,'3″',463,389)
    d.save()

    d=Diagram(434,'Templates and scatter')
    d.unit(70,88,5,5,'red',34)
    d.circle(179,149,58); d.circle(179,149,9,INK)
    d.die(290,175,'hit',45); d.die(470,104,1,43); d.die(510,181,3,43,-12)
    d.unit(70,342,5,5,'red',34)
    d.circle(179,396,58,'none',INK,2,stroke_dasharray='6 4')
    d.circle(303,365,58); d.circle(303,365,9,INK)
    d.line(179,396,303,365,arrow=True,sw=3)
    d.die(290,467,'arrow',43,-13); d.die(504,400,2,43); d.die(504,503,4,43)
    d.save()

    d=Diagram(437,'Forming a unit')
    for x,y,miss,ok in [(55,115,(),True),(330,115,((4,2),),True),(55,358,((0,1),(0,2)),False),(330,358,((4,1),),False)]:
        d.unit(x,y,5,3,cell=37,missing=miss)
        if ok:
            d.path(f'M {x+60} {y+145} l 12 12 l 27 -30',stroke=BLUE,sw=6)
        else:
            d.cross(x+85,y+144,25,RED)
    d.save()
    for number,title,c,r,cell in [(439,'A model’s facing',1,1,44),(441,'A unit’s facing',5,3,36)]:
        d=Diagram(number,title)
        x,y=(600-c*cell)/2,(600-r*cell)/2+20
        arcs(d,x,y,c*cell,r*cell); d.unit(x,y,c,r,cell=cell); d.save()

    d=Diagram(454,'Moving straight ahead')
    d.unit(60,345,4,5,cell=36,facing='right',ghost=True)
    d.unit(385,345,4,5,cell=36,facing='right')
    d.dimension(204,295,529,295,'4″',366,273)
    for x in [204,285.25,366.5,447.75,529]: d.line(x,295,x,311,color=EDGE)
    d.line(204,320,204,540,dash='4 5',color=EDGE)
    d.line(529,320,529,540,dash='4 5',color=EDGE)
    d.save()

    d=Diagram(455,'Wheeling',600,1200)
    d.rock(-30,155,236,340)
    for x,y,a,g in [(304,920,30,True),(304,920,-20,True),(285,670,0,True),(285,670,28,True),(285,390,0,True),(285,390,-30,False)]:
        d.unit(x,y,5,2,cell=39,ch=78,angle=a,ghost=g)
        d.circle(x,y,5,GOLD,INK,1)
    d.path('M 230 1090 Q 148 1035 213 955',arrow=True)
    d.path('M 485 808 Q 574 748 508 671',arrow=True)
    d.path('M 501 433 Q 600 370 519 292',arrow=True)
    d.line(332,857,345,810,arrow=True)
    d.line(395,618,395,539,arrow=True)
    d.save()

    d=Diagram(457,'Turn, redress ranks, reform',1200,600)
    d.unit(160,110,5,4,cell=36)
    d.unit(176,370,4,5,cell=36,angle=-15,facing='right'); d.badge(410,425,'A')
    d.unit(670,180,10,2,cell=36); d.badge(1080,215,'B')
    d.unit(670,418,10,2,cell=36,angle=-15,facing='down'); d.badge(1080,422,'C')
    d.save()

    d=Diagram(461,'Fleeing a charge',1200,600)
    d.divide(600,50,600,580)
    for off in [0,600]:
        d.unit(off+70,330,4,5,'red',32,facing='right')
        d.line(off+198,360,off+476,209,dash='5 6',color=EDGE)
    d.unit(310,210,5,2,cell=34,angle=60)
    d.path('M 290 214 C 240 266 266 343 335 318',arrow=True)
    d.path('M 329 192 C 386 164 414 240 390 274',arrow=True)
    d.unit(899,233,5,2,cell=34,angle=60,ghost=True)
    d.unit(1060,125,5,2,cell=34,angle=60)
    d.dimension(929,193,1070,98,'6″',990,110)
    d.die(754,133,3); d.die(810,105,3)
    d.badge(540,533,'1'); d.badge(1140,533,'2'); d.save()

    d=Diagram(463,'A failed charge')
    d.unit(106,105,4,5,'red',37,facing='right',angle=16)
    d.unit(438,392,2,5,cell=35,angle=30,ghost=True,facing='left')
    d.unit(348,347,2,5,cell=35,angle=30,facing='left')
    d.dimension(403,342,341,307,'3″',353,271)
    d.die(472,143,3,42); d.die(472,209,1,42); d.save()

    for number,title,terrain in [(466,'Completing a charge',False),(470,'Charging around terrain',True)]:
        d=Diagram(number,title,1200,1200)
        d.divide(600,50,600,1180); d.divide(20,620,1180,620)
        for i,(ox,oy) in enumerate([(0,40),(600,40),(0,620),(600,620)]):
            d.parts.append(f'<defs><clipPath id="panel-{i}"><rect x="{ox+4}" y="{oy+12}" width="592" height="548"/></clipPath></defs><g clip-path="url(#panel-{i})">')
            d.badge(ox+48,oy+46,str(i+1))
            if terrain:
                d.rock(ox-25,oy+260,280,160)
                d.rock(ox+450,oy+440,98,90,18)
            if i<3: d.unit(ox+215,oy+465,5,2,cell=36)
            if i==0:
                d.unit(ox+200,oy+120,5,1,'red',42,ch=84,facing='down')
                d.text(ox+305,oy+258,'Charge!',32)
            elif i==1:
                d.unit(ox+244,oy+120,5,1,'red',42,ch=84,facing='down',ghost=True)
                d.unit(ox+244,oy+201,5,1,'red',42,ch=84,facing='down',ghost=True)
                d.unit(ox+282,oy+210,5,1,'red',42,ch=84,facing='down',angle=27)
                d.path(f'M {ox+460} {oy+201} Q {ox+540} {oy+275} {ox+451} {oy+380}',arrow=True)
                d.line(ox+235,oy+207,ox+235,oy+278,arrow=True)
                d.circle(ox+244,oy+285,5,GOLD,INK,1)
            elif i==2:
                d.unit(ox+309,oy+260,5,1,'red',42,ch=84,facing='down',ghost=True,angle=27)
                d.unit(ox+282,oy+313,5,1,'red',42,ch=84,facing='down',angle=27)
                d.line(ox+481,oy+391,ox+444,oy+463,arrow=True)
            else:
                if terrain:
                    d.unit(ox+215,oy+465,5,2,cell=36,ghost=True)
                    d.unit(ox+282,oy+313,5,1,'red',42,ch=84,facing='down',angle=27)
                    d.unit(ox+234.6,oy+383.3,5,2,cell=36,angle=27)
                    d.circle(ox+395,oy+465,5,GOLD,INK,1)
                    d.path(f'M {ox+173} {oy+529} Q {ox+137} {oy+501} {ox+185} {oy+459}',arrow=True)
                else:
                    d.unit(ox+282,oy+313,5,1,'red',42,ch=84,facing='down',ghost=True,angle=27)
                    d.unit(ox+225,oy+381,5,1,'red',42,ch=84,facing='down')
                    d.unit(ox+215,oy+465,5,2,cell=36)
                    d.path(f'M {ox+305} {oy+336} Q {ox+213} {oy+300} {ox+208} {oy+403}',arrow=True)
                    d.circle(ox+395,oy+465,5,GOLD,INK,1)
            d.end()
        d.save()

    d=Diagram(468,'Front, flank and rear charges')
    arcs(d,253,270,92.5,74,False); d.unit(253,270,5,4,cell=18.5)
    d.unit(145,139,5,1,'red',29,ch=58,facing='down',angle=-30); d.badge(312,112,'1')
    d.unit(436,73,5,4,'red',24,facing='down',angle=30); d.badge(543,249,'2')
    d.unit(382,508,5,1,'red',29,ch=58,facing='up',angle=-15); d.badge(543,470,'3')
    d.unit(104,367.5,3,5,'red',23,facing='right'); d.badge(220,516,'4')
    d.text(128,216,'Charge!',24,rotate=-30); d.text(438,255,'Charge!',24,rotate=30)
    d.text(440,483,'Charge!',24,rotate=-15); d.text(200,438,'Charge!',24,rotate=-90)
    d.save()

    d=Diagram(472,'Multiple charges',1200,600)
    d.divide(600,50,600,580)
    d.unit(100,155,5,2,'red',36,facing='down'); d.unit(399,105,5,2,'red',36,facing='down',angle=30)
    d.unit(210,424,5,2,cell=36)
    d.text(190,277,'Charge!',31); d.text(440,267,'Charge!',31,rotate=30)
    d.unit(700,150,5,2,'red',36,ghost=True); d.unit(980,105,5,2,'red',36,ghost=True,angle=30)
    d.unit(728,352,5,2,'red',36,facing='down'); d.unit(908,352,5,2,'red',36,facing='down')
    d.unit(819,424,5,2,cell=36)
    d.path('M 1040 250 Q 1090 285 1020 332',arrow=True)
    d.line(765,240,765,336,arrow=True); d.badge(547,542,'1'); d.badge(1147,542,'2'); d.save()

    d=Diagram(474,'Fleeing through terrain')
    d.unit(40,286,4,5,cell=35,ghost=True,facing='right')
    d.unit(223,286,4,5,cell=35,ghost=True,facing='right')
    for r in range(2):
        for c in range(4): d.rect(223+c*35,286+r*35,35,35,WHITE)
    d.rock(173,170,153,209,-17)
    d.unit(412,286,4,5,cell=35,facing='right',missing=((0,0),(0,1)))
    d.line(184,383,218,383,arrow=True); d.line(369,383,407,383,arrow=True)
    for x,y,n in [(373,118,1),(421,118,5),(398,170,3),(445,180,5),(496,150,5),(373,223,1),(429,227,1),(480,236,2)]: d.die(x,y,n,28)
    d.save()


def combat():
    d=Diagram(493,'Models in base contact',600,1190)
    d.divide(20,600,580,600)
    d.unit(195,235,5,1,'red',36,facing='down'); d.unit(123,271,9,1,cell=36)
    d.highlight(195,235,180,36); d.highlight(159,271,252,36)
    d.unit(65,800,5,1,'red',40,ch=80,facing='down')
    d.unit(265,844,5,1,'red',36,facing='down'); d.unit(195,880,5,1,cell=36)
    d.highlight(231,880,72,36); d.save()

    d=Diagram(494,'The fighting rank')
    d.unit(208,230,5,4,'red',36); d.unit(280,194,2,1,cell=36,facing='down')
    d.highlight(208,230,180,36); d.save()

    d=Diagram(496,'Supporting attacks',1200,600)
    d.divide(600,50,600,580)
    d.unit(192,210,5,3,'red',36,facing='down'); d.unit(84,318,10,2,cell=36)
    d.highlight(192,282,180,36); d.highlight(192,246,180,36,True)
    d.highlight(156,318,252,36); d.highlight(156,354,252,36,True)
    d.unit(805,266,5,2,'red',36,facing='down'); d.unit(985,230,1,5,cell=36,facing='left')
    d.highlight(949,266,36,72); d.highlight(985,230,36,144); d.save()

    d=Diagram(498,'Moving an incomplete rank',1200,600)
    for off,miss in [(0,[(2,4),(3,4),(4,4)]),(600,[(0,4),(1,4),(2,4)])]:
        d.unit(off+96,213,5,5,cell=36,missing=miss)
        d.unit(off+276,213,4,5,'red',36,facing='left')
    d.line(180,375,261,375,arrow=True,sw=3)
    d.line(526,304,618,304,arrow=True,sw=4); d.save()

    d=Diagram(499,'Fighting across a gap')
    d.unit(204,135,5,3,'red',36)
    d.unit(276,243,1,1,'red',36)
    d.unit(204,279,5,5,cell=36)
    d.highlight(204,207,72,36); d.highlight(312,207,72,36); d.highlight(276,243,36,36)
    d.highlight(204,279,180,36); d.highlight(204,315,180,36,True); d.save()

    d=Diagram(508,'Fleeing and pursuing',1200,1200)
    d.divide(600,50,600,1180); d.divide(20,620,1180,620)
    for i,(ox,oy) in enumerate([(0,50),(600,50),(0,620),(600,620)]):
        d.badge(ox+48,oy+46,str(i+1))
        d.unit(ox+80,oy+240,3,5,cell=34,facing='right',ghost=i==3)
        if i<2:
            d.unit(ox+182,oy+240,2,5,'red',34,facing='left' if i==0 else 'right')
        else:
            d.unit(ox+182,oy+240,2,5,'red',34,facing='right',ghost=True)
            d.unit(ox+452,oy+240,2,5,'red',34,facing='right')
        if i==0:
            d.text(350,350,'Flee!',34)
            for x,y,n in [(265,197,4),(318,197,5),(82,430,3),(135,430,4)]: d.die(x,y,n,35)
        if i==1:
            d.path('M 878 263 C 944 220 959 419 879 478',arrow=True)
        if i==2: d.dimension(258,oy+327,436,oy+327,'9″',347,oy+300)
        if i==3:
            d.unit(ox+304,oy+240,3,5,cell=34,facing='right')
            d.dimension(ox+182,oy+217,ox+406,oy+217,'7″',ox+294,oy+193)
    d.save()

    d=Diagram(510,'Pursuit into a new enemy',1200,600)
    d.divide(600,50,600,580)
    for off in [0,600]:
        d.unit(off+78,160,2,5,cell=34,facing='right',ghost=bool(off))
        d.unit(off+146,160,2,5,'red',34,facing='right',ghost=True)
        d.unit(off+470,160,2,5,'red',34,facing='right')
        d.unit(off+246,498,5,3,'red',34,angle=-45)
    d.line(224,235,457,235,arrow=True)
    d.unit(798,210,2,5,cell=34,facing='right',ghost=True,angle=45)
    d.unit(918,330,2,5,cell=34,facing='right',angle=45)
    d.circle(678,330,6,GOLD)
    d.line(857,269,914,326,arrow=True)
    d.badge(546,533,'1'); d.badge(1146,533,'2'); d.save()

    d=Diagram(518,'Multiple combat: before')
    d.unit(218,151,5,4,'red',36,facing='down')
    d.unit(146,295,2,5,'red',36,facing='right')
    d.unit(218,295,6,5,cell=36); d.save()

    d=Diagram(519,'Multiple combat: casualties')
    d.unit(201,128,5,4,'red',36,facing='down',missing=((0,0),(4,0)))
    d.unit(165,272,1,5,'red',36,facing='right'); d.unit(129,344,1,1,'red',36,facing='right')
    d.unit(201,272,6,4,cell=36); d.unit(273,416,1,1,cell=36)
    for x,y,side in [(227+i*47,77,'blue') for i in range(4)]+[(70,344,'blue')]+[(170+i*47,500,'red') for i in range(6)]:
        d.unit(x,y,1,1,side,32,facing='down' if side=='red' else 'up'); d.cross(x+16,y+17,21)
    d.save()

    d=Diagram(521,'Fleeing through an enemy')
    d.unit(60,235,4,5,cell=35,facing='right')
    d.unit(200,235,2,5,'red',35,facing='right',ghost=True)
    d.unit(270,235,2,5,cell=35,facing='left')
    d.unit(450,235,2,5,'red',35,facing='right',missing=((0,0),(0,4)))
    d.line(268,322,435,322,arrow=True,sw=3); d.save()

    d=Diagram(523,'Multiple combats and pursuit',600,1782)
    for i,oy in enumerate([50,630,1210]):
        if i: d.divide(20,oy,580,oy)
        d.badge(48,oy+45,str(i+1))
        y=oy+174
        d.unit(45,y,4,5,cell=35,facing='right',ghost=i==2)
        d.unit(185,y,2,5,'red',35,ghost=True,facing='right')
        d.unit(450,y,2,5,'red',35,facing='right',missing=((0,0),(0,4)))
        if i==0:
            d.unit(150,y+175,5,2,cell=35)
            d.dimension(263,y+80,433,y+80,'7″')
        elif i==1:
            d.unit(150,y+175,5,2,cell=35,ghost=True)
            d.unit(321,y+103,2,5,cell=35,facing='right',angle=-16)
            d.line(270,y+80,430,y+80,arrow=True)
            d.line(284,y+277,354,y+258,arrow=True)
            d.text(316,y+325,'6″',29)
            d.circle(238,y+209,8,'none')
        else:
            d.unit(150,y,4,5,cell=35,facing='right')
            d.unit(321,y+103,2,5,cell=35,facing='right',angle=-16)
            d.line(133,y-28,290,y-28,arrow=True)
            d.text(328,y+63,'1″',26)
    d.save()

    # This wide diagram is printed in one column. Larger labels are deliberate.
    d=Diagram(527,'Panic within 6 inches',1200,600)
    d.unit(75,160,2,5,cell=44,ch=38,facing='right')
    d.unit(530,151,5,4,'red',36,facing='down')
    d.unit(530,295,5,2,cell=36)
    for r in range(2):
        for c in range(5): d.cross(548+c*36,313+r*36,23)
    d.unit(312,444,5,3,cell=36)
    d.unit(850,464,5,3,cell=36)
    d.unit(998,157,5,3,cell=36)
    d.unit(791,275,1,1,cell=36)
    d.path('M 530 125 L 435 125 Q 303 128 303 264 L 303 444 M 710 125 Q 913 112 927 288 L 927 459 M 500 554 L 832 554',stroke=INK,dash='13 12')
    d.dimension(345,204,520,285,'6″',406,303)
    d.text(393,425,'PANIC TEST',35); d.text(936,449,'PANIC TEST',35)
    d.text(809,353,'PANIC',32); d.text(809,388,'TEST',32); d.save()

    d=Diagram(530,'A breath weapon template')
    d.unit(61,235,1,1,cell=172,ch=90,facing='right')
    d.line(233,235,424,53,dash='9 8',color=EDGE)
    d.line(233,325,457,573,dash='9 8',color=EDGE)
    d.unit(405,335,4,5,'red',32,facing='left')
    # Nine hit bases (3 by 3) with a teardrop wholly inside the forward arc.
    d.path('M 233 280 L 473 334 C 499 335 499 419 466 430 C 444 430 410 430 405 414 Z',WHITE,INK,2.5)
    for r in range(3):
        for c in range(3): d.cross(421+c*32,351+r*32,21)
    d.save()

    d=Diagram(541,'Skirmisher facing')
    arcs(d,113,221,362,202)
    for r in range(3):
        for c in range(5): d.unit(113+c*80,221+r*80,1,1,cell=34)
    d.save()

    d=Diagram(544,'Skirmishers forming up',600,842)
    d.divide(20,460,580,460)
    d.badge(48,90,'1'); d.badge(48,506,'2')
    d.unit(200,135,5,2,'red',34,facing='down')
    d.unit(200,203,5,3,cell=34,ghost=True)
    for r in range(3):
        for c in range(5):
            x,y=125+c*75,203+r*75
            d.unit(x,y,1,1,cell=30)
            tx,ty=217+c*34,220+r*34
            if abs(tx-x-15)+abs(ty-y-15)>20:
                d.line(x+15+(tx-x-15)*.28,y+15+(ty-y-15)*.28,tx,ty,arrow=True,sw=1.5)
    d.unit(200,570,5,2,'red',34,facing='down'); d.unit(200,638,5,3,cell=34); d.save()


def artillery_and_characters():
    d=Diagram(553,'Charging a war machine')
    d.unit(320,220,2,5,'red',36,facing='left')
    d.cannon(288,330,40)
    for x,y,a in [(203,270,-22),(176,380,-40),(281,426,33)]: d.unit(x,y,1,1,cell=36,angle=a)
    d.save()

    d=Diagram(555,'A war machine’s line of sight')
    d.cannon(272,473,28)
    d.line(285,423,217,64,dash='8 8',color=EDGE)
    d.line(285,423,576,351,dash='8 8',color=EDGE)
    d.unit(79,156,1,1,'red',81,facing='down',angle=-15)
    d.text(125,278,'A',32)
    d.unit(442,111,5,4,'red',32,facing='down',angle=45)
    d.text(410,348,'B',32); d.save()

    d=Diagram(565,'Bolt thrower penetration',600,1782)
    for i,oy in enumerate([50,630,1210]):
        if i: d.divide(20,oy,580,oy)
        d.badge(48,oy+45,str(i+1))
        d.cannon(131,oy+245,90,'bolt')
        if i==0:
            d.unit(365,oy+108,4,5,'red',40,facing='left',angle=23)
            d.line(30,oy+491,288,oy+357,dash='8 8',color=EDGE)
            d.line(330,oy+23,365,oy+108,dash='8 8',color=EDGE)
            for j,t in enumerate(['S6','S5','S4','S3']): d.text(317+j*46,oy+404+j*16,t,29)
        else:
            d.unit(310,oy+144,5,2,'red',40,ch=80,angle=-15)
            d.line(29,oy+67,310,oy+144,dash='8 8',color=EDGE)
            d.line(310,oy+309,161,oy+525,dash='8 8',color=EDGE)
            for j,t in enumerate(['S6','S5','S4','S3','S2']): d.text(353+j*44,oy+362-j*12,t,29)
            if i==2: d.unit(213,oy+233,2,5,'red',32,facing='left',angle=9)
    d.save()

    d=Diagram(567,'A cannon’s initial shot',1200,600)
    d.divide(600,50,600,580)
    for off in [0,600]:
        d.cannon(off+181,231,131)
        d.unit(off+421,450,1,1,'red',76,facing='down',angle=45)
    d.line(216,260,421,480,dash='9 9',color=INK)
    d.circle(421,480,5,INK)
    d.line(815,256,1169,390,dash='9 9',color=INK)
    d.die(898,415,4,40); d.die(960,440,'arrow',40,-20)
    d.badge(546,541,'1'); d.badge(1146,541,'2'); d.save()

    d=Diagram(569,'Cannonball bounces',1200,600)
    d.divide(600,50,600,580)
    for off in [0,600]:
        d.cannon(off+135,216,123)
        d.line(off+174,240,off+564,454,dash='7 7',color=INK)
    d.group('translate(400 284) rotate(9)')
    d.unit(0,0,3,5,'red',34,facing='left')
    for c,r in [(0,2),(1,3),(2,3)]:
        d.rect(c*34,r*34,34,34,WHITE); d.cross(c*34+17,r*34+17,22)
    d.end()
    d.unit(935,292,1,1,'red',74,facing='down',angle=42); d.circle(939,341,5,INK)
    d.unit(965,440,5,3,'red',32,angle=-40)
    d.badge(546,541,'1'); d.badge(1146,541,'2'); d.save()

    d=Diagram(572,'A stone thrower’s template',600,1196)
    d.unit(184,180,5,4,'red',36)
    # Highlight exactly eleven affected models, including the central hit.
    hit=[(c,r) for r in range(4) for c in range(3) if (c,r)!=(2,0)]
    for c,r in hit: d.rect(184+c*36,180+r*36,36,36,WHITE)
    d.circle(202,270,76,WHITE,INK,2.5)
    for c,r in hit: d.cross(202+c*36,198+r*36,23)
    d.circle(202,270,9,INK)
    d.rock(324,561,280,247,-21)
    d.cannon(290,1017,-7,'stone')
    d.line(283,963,212,353,dash='8 8',color=INK)
    d.save()

    d=Diagram(577,'Characters joining units',600,1532)
    d.divide(20,600,580,600); d.divide(20,1190,580,1190)
    d.unit(260,180,5,3,cell=42)
    d.character(126,396,42,84,30)
    d.line(173,369,228,280,arrow=True)
    for x,y,w,h in [(40,704,84,84),(336,704,42,84),(40,960,42,42),(336,960,42,84)]:
        col=2 if x==40 else (2 if y==704 else 0)
        miss=[(c,r) for c in range(col,col+w//42) for r in range(h//42)]
        d.unit(x,y,5,3,cell=42,missing=miss)
        d.character(x+col*42,y,w,h)
    d.unit(226,1315,5,3,cell=38)
    d.character(181,1315,45,85)
    d.save()

    d=Diagram(580,'Make way!')
    d.unit(240,190,5,4,'red',34,facing='down')
    d.unit(138,326,10,2,cell=34,missing=((0,0),(3,0)))
    d.character(138,326,34,34,hollow=True); d.character(240,326,34,34)
    d.line(177,343,232,343,arrow=True,sw=2.5); d.save()

    d=Diagram(582,'Characters leaving units',1200,600)
    d.divide(600,50,600,580)
    d.unit(370,219,4,5,cell=35,facing='left',missing=((0,4),))
    d.character(370,359,35,35,hollow=True); d.character(105,359,35,35)
    d.line(361,377,152,377,arrow=True)
    d.character(705,359,35,35)
    d.unit(945,272,4,5,cell=35,ghost=True,angle=45)
    d.unit(945,272,4,5,cell=35,ghost=True)
    d.unit(803,99,4,5,cell=35,facing='left')
    d.path('M 1100 417 Q 1071 510 944 498',arrow=True)
    d.path('M 1030 235 Q 1048 75 874 77',arrow=True)
    d.badge(545,541,'1'); d.badge(1145,541,'2'); d.save()

    d=Diagram(584,'Look out, sir!')
    d.unit(239,144,5,3,cell=35)
    d.character(62,251,69,69); d.character(161,460,35,35); d.character(492,365,35,35)
    d.dimension(146,263,229,238,'3″',162,227)
    d.dimension(196,447,276,287,'7″',285,396)
    d.dimension(486,354,426,264,'3″',504,292)
    d.badge(80,374,'1'); d.badge(154,545,'2'); d.badge(503,446,'3'); d.save()


def deployment():
    # Schematic 72 by 48 inch battlefield. Ratios within each axis preserve
    # the deployment distances; the header sits outside the playing area.
    for number,title in [(601,'Battleline'),(603,'Dawn attack'),(605,'Battle for the pass'),(607,'Blood and glory'),(609,'Meeting engagement'),(611,'The watchtower')]:
        d=Diagram(number,title,900,606)
        d.group('translate(24 62)')
        w,h=852,520
        if number in [601,607]:
            edge=71 if number==601 else 106.5
            gap=130 if number==601 else 97.5
            for y,fill in [(0,PALE_RED),(h/2+gap,PALE_BLUE)]:
                d.rect(edge,y,w-2*edge,h/2-gap,fill,INK,1.5,stroke_dasharray='8 7')
            d.line(0,h/2,w,h/2,dash='24 16',color=EDGE)
            for y,label in [(77,'Side A deployment zone'),(h-48,'Side B deployment zone')]: d.text(w/2,y,label,32)
            for y in [65,h-65]:
                d.dimension(3,y,edge-3,y,'6″' if number==601 else '9″',edge/2,y+35)
                d.dimension(w-edge+3,y,w-3,y,'6″' if number==601 else '9″',w-edge/2,y+35)
            for sign in [-1,1]: d.dimension(w/2,h/2,w/2,h/2+sign*gap,'12″' if number==601 else '9″',w/2+53,h/2+sign*gap/2+9)
        elif number==603:
            for y,fill,side in [(0,PALE_RED,'A'),(390,PALE_BLUE,'B')]:
                d.rect(0,y,w,130,fill,'none')
                d.line(0,y+130 if y==0 else y,w,y+130 if y==0 else y,dash='8 7')
                for x in [213,639]: d.line(x,y,x,y+130,dash='8 7')
                d.text(w/2,y+72,f'Side {side} centre',34)
                for x,flank in [(106.5,'Right' if side=='A' else 'Left'),(745.5,'Left' if side=='A' else 'Right')]:
                    d.text(x,y+46,f'Side {side}',26); d.text(x,y+83,f'{flank} flank',26)
            d.line(0,260,w,260,dash='24 16',color=EDGE)
            for y in [159,365]:
                d.dimension(8,y,205,y,'18″',106,y+32 if y==159 else y-14)
                d.dimension(647,y,844,y,'18″',745,y+32 if y==159 else y-14)
            d.dimension(426,134,426,256,'12″',479,209)
            d.dimension(426,264,426,386,'12″',479,336)
        elif number==605:
            d.rect(0,0,284,h,PALE_RED,'none'); d.rect(568,0,284,h,PALE_BLUE,'none')
            for x in [284,568]: d.line(x,0,x,h,dash='8 7')
            d.line(426,0,426,h,dash='24 16',color=EDGE)
            for x,s in [(142,'A'),(710,'B')]:
                for y,t in [(211,f'Side {s}'),(253,'deployment'),(295,'zone')]: d.text(x,y,t,32)
            d.dimension(287,260,423,260,'12″',355,242)
            d.dimension(429,260,565,260,'12″',497,242)
        elif number==609:
            # Parallel boundaries, measured perpendicular to the centre diagonal.
            offset=94
            d.path(f'M 0 0 H {w-offset*w/h} L 0 {h-offset} Z',PALE_RED,'none')
            d.path(f'M {offset*w/h} {h} H {w} V {offset} Z',PALE_BLUE,'none')
            d.line(0,h,w,0,dash='24 16',color=EDGE)
            d.line(0,h-offset,w-offset*w/h,0,dash='8 7')
            d.line(offset*w/h,h,w,offset,dash='8 7')
            for x,y,s in [(165,97,'A'),(691,370,'B')]:
                for off,t in [(0,f'Side {s}'),(41,'deployment'),(82,'zone')]: d.text(x,y+off,t,33)
            dx,dy=42,69
            d.dimension(426-dx,260-dy,426,260,'6″',351,215)
            d.dimension(426,260,426+dx,260+dy,'6″',504,307)
        else:
            d.rect(0,0,w,130,PALE_RED,'none'); d.rect(0,390,w,130,PALE_BLUE,'none')
            for y in [130,390]: d.line(0,y,w,y,dash='8 7')
            d.line(0,260,w,260,dash='24 16',color=EDGE)
            d.text(426,77,'Side A deployment zone',34); d.text(426,470,'Side B deployment zone',34)
            d.rect(400,234,52,52,WHITE,INK,2,stroke_dasharray='5 4')
            d.rect(412,246,28,28,EDGE,INK,1.5)
            for x in [412,432]:
                for y in [246,266]: d.rect(x-3,y-3,8,8,PAPER,INK,1)
            d.dimension(426,134,426,231,'12″',480,193)
            d.dimension(426,289,426,386,'12″',480,350)
        d.rect(0,0,w,h,'none',INK,2)
        d.end(); d.save()


def main():
    movement()
    combat()
    artillery_and_characters()
    deployment()
    records=sorted(MANIFEST,key=lambda r:r['file'])
    assert len(records)==46 and len({r['file'] for r in records})==46
    (ROOT/'manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    cards='\n'.join(f'<figure><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{escape(r["title"])}"></a><figcaption>{escape(r["title"])} <small>{r["file"]}</small></figcaption></figure>' for r in records)
    (ROOT/'gallery.html').write_text('''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WAR · Rulebook diagrams</title>
<style>body{margin:0;padding:40px;background:#e8dfcf;color:#30291f;font:18px Georgia,serif}h1{font-size:32px}p{max-width:760px;line-height:1.6}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:24px}figure{margin:0;padding:16px;background:#f5f0e5;border:1px solid #b5a58a;border-radius:8px}img{display:block;width:100%;height:340px;object-fit:contain}figcaption{margin-top:15px}small{display:block;margin-top:6px;color:#786c58;font:12px monospace}a:focus{outline:3px solid #5c8798}</style>
<h1>Warhammer Armies Revamped</h1><p>46 original vector diagrams for the core rulebook. Select a diagram to inspect it at full size. Blue and red identify opposing forces; dashed bases show previous positions, and crowns identify characters.</p><main class="gallery">'''+cards+'</main></html>\n',encoding='utf-8')
    print(f'Wrote {len(records)} SVG diagrams, manifest.json and gallery.html')


if __name__ == '__main__':
    main()
