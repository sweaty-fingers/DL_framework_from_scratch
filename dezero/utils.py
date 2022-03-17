import os
import subprocess

def _dot_var(v, verbose=False):
    dot_var = '{} [label="{}", color=orange, style=filled]\n'

    name = '' if v.name is None else v.name
    if verbose and v.data is not None:
        if v.name is not None:
            name += ": "
        name += str(v.shape) + ' ' + str(v.dtype)
    
    return dot_var.format(id(v), name)


def _dot_func(f):
    dot_func = '{} [label="{}", color=lightblue, style=filled, shape=box]\n'
    ret = dot_func.format(id(f), f.__class__.__name__)

    # for edge
    dot_edge = '{} -> {}\n'
    for x in f.inputs:
        ret += dot_edge.format(id(x), id(f))
    for y in f.outputs:
        ret += dot_edge.format(id(f), id(y())) #  y는 weakref

    return ret


def get_dot_graph(output, verbose=True):
    txt = ''
    funcs = []
    seen_set = set()

    def add_func(f):
        if f not in seen_set:
            funcs.append(f)
            seen_set.add(f)

    add_func(output.creator)
    txt += _dot_var(output, verbose)

    while funcs:
        func = funcs.pop()
        txt += _dot_func(func)
        for x in func.inputs:
            txt += _dot_var(x, verbose)

            if x.creator is not None:
                add_func(x.creator)

    return 'digraph g {\n' + txt + '}'


def plot_dot_graph(output, verbose=True, to_file='graph.png'):
    dot_graph = get_dot_graph(output, verbose)

    tmp_dir = os.path.join(os.path.expanduser('~'), '.dezero')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    graph_path = os.path.join(tmp_dir, 'tmp_graph.dot')

    with open(graph_path, "w") as f:
        f.write(dot_graph)
    
    extension = os.path.splitext(to_file)[1][1:] # 확장자만 남김
    cmd = f'dot {graph_path} -T {extension} -o {to_file}'
    subprocess.run(cmd, shell=True) # 파이썬에서 외부 프로그램 호출을 위한 subprocess

    # 주피터 노트북을 위한 실행
    try:
        from IPython import display
        return display.Image(filename=to_file)
    except:
        pass


def reshape_sum_backward(gy, x_shape, axis, keepdims):
    """dezero.functions.sum 의 역전파 계산을 위한 reshape

    Args:
        gy (dezero.Variable): 아웃풋의 역전파 값
        x_shape (tuple): 합을 수행하기 전 x의 shape
        axis (None or int or tuple of ints): sum을 수행한 axis
        keepdims (bool): np.sum을 수행할때 keepdims 여부

    Returns:
        dezero.Variable: reshape된 Gradient variable
    """

    ndim = len(x_shape)
    tupled_axis = axis
    if axis is None:
        tupled_axis = None
    elif not isinstance(axis, tuple):
        tupled_axis = (axis,)
    
    if not (ndim == 0 or tupled_axis is None or keepdims):
        actual_axis = [a if a >= 0 else a + ndim for a in tupled_axis] # -로 axis를 입력했을 때
        shape = list(gy.shape)
        for a in sorted(actual_axis):
            shape.insert(a, 1)
    else:
        shape = gy.shape # tupled_axis = None 일경우 broadcast
    
    gy = gy.reshape(shape)
    return gy
    


     
        
    

