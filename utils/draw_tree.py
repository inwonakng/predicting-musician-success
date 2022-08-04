from ete3 import Tree,TreeStyle,TextFace,add_face_to_node,RectFace,NodeStyle
import numpy as np
import pandas as pd
colors = {
    1: '#1e90ff', # true is blue
    0: '#000000',
    -1: '#ff0000', #false is red
}
names = {
    1:'Yes',
    0:'',
    -1:'No',
}
def style_node(node,direction):
    style = NodeStyle()
    style["fgcolor"] = "#0f0f0f"
    style["size"] = 1
    # color = "#ff0000" if direction == 1 else '#1e90ff'            
    # style["vt_line_color"] = colors[direction]
    style["hz_line_color"] = colors[direction]
    style["vt_line_width"] = 4
    # style["vt_line_color"] = colors[direction]

    style["hz_line_width"] = 4
    # style["vt_line_type"] = 0 # 0 solid, 1 dashed, 2 dotted
    # style["hz_line_type"] = 0
    node.set_style(style)
    
    if direction:
        F = TextFace(names[direction],tight_text=True)
        F.margin_bottom = 5
        F.margin_left=60
        
        node.add_face(F,column=0,position='branch-top')
    # add_face_to_node(F,,column=0,position='branch-top')


def xgb(model,condition):
    tree = model.get_booster().trees_to_dataframe()
    gain_top3_thres = tree.Gain.sort_values(ascending=False).values[2]
    treedraw = Tree(format=3)
    root = tree.ID.values[0]
    stack = [(root,treedraw,0)]
    # display(tree)

    while stack:
        idx,t,direction = stack.pop(0)
        feat,spli,yeschild,nochild,pred = tree[tree.ID==idx][['Feature','Split','Yes','No','Gain']].values[0]
        
        if not np.isnan(spli):       
            newt = t.add_child(name=f'{feat} < {spli:.4f} top3: {int(pred >= gain_top3_thres)}')
            style_node(newt,direction)
            stack+=[(yeschild,newt,1),(nochild,newt,-1)]
        else:
            
            newt = t.add_child(name=f'{pred:.4f}')
            style_node(newt,direction)
    
    def my_layout(node):
        shortname = node.name
        if '<' in shortname:
            f,rest = shortname.split('<')
            thresh,is_gain_top3 = rest.split(' top3: ')
            
            val = f'{float(thresh):.2f}'
            if 'Followers' in shortname: 
            #     f = 'Follower Count'
                val = int(float(thresh))
            
            if 'Last Release' in shortname or 'First Release' in shortname:
                val = str(pd.to_datetime(float(thresh)).date())
                
            if 'Career Length' in shortname:
                val = f'{pd.to_timedelta(float(thresh)).days//30} months'
                
            if 'Num Release' in shortname or 'Edges' in shortname:
                val = int(float(thresh))
                
            # if 'Rank' in shortname:
            #     val = f'{float(thresh):.0e}'
            shortname = f'{f} <= {val} \n'
            # if 'Network Rank' in shortname: 
            #     print('----')
            #     print(shortname)
            #     print('----')
            if 'Network Rank  <= 0.00' in shortname:
                print('huh')
                shortname = 'Network Rank = 0 \n'
            F = TextFace(f'   {shortname}  ', tight_text=True,bold=bool(int(is_gain_top3)))

            add_face_to_node(F, node, column=0, position="branch-right")
            
        elif shortname:
            coloredname = ''
            color = ''
            pred = float(shortname)
            if pred < -.5:
                coloredname = 'Very unlikely'
                color = '#ff0000'
            elif pred < -.2:
                coloredname = 'Unlikely'
                color='#ff6363'
            elif pred < 0:
                coloredname = 'Slightly unlikely'
                color='#ff9e9e'
            elif pred < .2:
                coloredname = 'Slightly likely'
                color='#6565f0'
            elif pred < .5:
                coloredname = 'Likely'
                color='#3333f5'
            else:
                coloredname = 'Very likely'
                color='#0000ff'
            # F = RectFace(10,6,'#ffffff','#000000',label=node.name,tight_text=True)
            
            F = TextFace(f'  {coloredname}', tight_text=True,fgcolor=color)
            add_face_to_node(F, node, column=0, position="branch-right")
            
            F = TextFace(f' {condition}', tight_text=True)
            add_face_to_node(F, node, column=1, position="branch-right")
        
    ts = TreeStyle()
    ts.branch_vertical_margin = 50
    ts.show_leaf_name = False
    ts.show_branch_length=False
            
    ts.layout_fn = my_layout

    return treedraw,ts