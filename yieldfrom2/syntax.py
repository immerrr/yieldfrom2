import inspect
import json
from ast import (AST, Assign, Attribute, Break, Call, Compare, ExceptHandler,
                 Expr, If, Is, Load, Name, Num, Raise, Store, While,
                 Yield, walk, iter_fields, PyCF_ONLY_AST)
try:
    from ast import TryExcept as Try
except ImportError:
    from ast import Try

from collections import OrderedDict as odict
import sys
from six import exec_, get_function_code, get_function_globals, PY3

from .bytecode import get_future_flags
from .utils import gen_result, gen_close

yield_from_ = lambda: None


def ast_to_str(astobj):
    return json.dumps(ast_to_dict(astobj), indent=1)


def _resolve(func, ast_obj):
    try:
        if isinstance(ast_obj, Attribute):
            next_obj = ast_obj.value
            attr = ast_obj.attr
            return getattr(_resolve(func, next_obj), attr)
        elif isinstance(ast_obj, Name):
            func_globals = get_function_globals(func)
            try:
                return func_globals[ast_obj.id]
            except KeyError:
                import builtins
                return getattr(builtins, ast_obj.id)
    except (KeyError, AttributeError):
        return None


def create_yieldfrom_ast(targets, generator):
    output = [
        Assign(
            targets=[Name(id='__yieldfrom_iter__', ctx=Store())],
            value=Call(
                func=Name(id='iter', ctx=Load()),
                args=[generator],
                keywords=[],
                starargs=None,
                kwargs=None),
        ),
        Try(
            body=[
                Assign(
                    targets=[Name(id='__yieldfrom_out__', ctx=Store())],
                    value=Call(
                        func=Name(id='next', ctx=Load()),
                        args=[Name(id='__yieldfrom_iter__', ctx=Load())],
                        keywords=[],
                        starargs=None,
                        kwargs=None))
            ],
            handlers=[
                ExceptHandler(
                    type=Name(id='StopIteration', ctx=Load()),
                    name=Name(id='__yieldfrom_err__', ctx=Store()),
                    body=[
                        Assign(
                            targets=[Name(id='__yieldfrom_result__', ctx=Store())],
                            value=Call(
                                func=Name(id='__yieldfrom_gen_result__', ctx=Load()),
                                args=[Name(id='__yieldfrom_err__', ctx=Load())],
                                keywords=[],
                                starargs=None,
                                kwargs=None
                            )
                        )
                    ]
                )
            ],
            orelse=[
                While(
                        test=Num(n=1),
                        body=[
                            Try(
                                body=[
                                    Assign(
                                        targets=[Name(id='__yieldfrom_in__', ctx=Store())],
                                        value=Yield(value=Name(id='__yieldfrom_out__', ctx=Load())))],
                                handlers=[
                                    ExceptHandler(
                                        type=Name(id='GeneratorExit', ctx=Load()),
                                        name=Name(id='__yieldfrom_err__', ctx=Store()),
                                        body=[
                                            Expr(
                                                value=Call(
                                                    func=Name(id='__yieldfrom_gen_close__', ctx=Load()),
                                                    args=[Name(id='__yieldfrom_iter__', ctx=Load())],
                                                    keywords=[],
                                                    starargs=None,
                                                    kwargs=None)),
                                            Raise(
                                                type=Name(id='__yieldfrom_err__', ctx=Load()), inst=None, tback=None)
                                        ]
                                    ),
                                    ExceptHandler(
                                        type=Name(id='BaseException', ctx=Load()),
                                        name=Name(id='__yieldfrom_err__', ctx=Store()),
                                        body=[
                                            Assign(
                                                targets=[Name(id='__yieldfrom_exc_info__', ctx=Store())],
                                                value=Call(
                                                    func=Name(id='__yieldfrom_get_exc_info__', ctx=Load()),
                                                    args=[],
                                                    keywords=[],
                                                    starargs=None,
                                                    kwargs=None)),
                                            Try(
                                                body=[
                                                    Assign(
                                                        targets=[Name(id='__yieldfrom_method__', ctx=Store())],
                                                        value=Attribute(
                                                            value=Name(id='__yieldfrom_iter__', ctx=Load()),
                                                            attr='throw', ctx=Load()))
                                                ],
                                                handlers=[
                                                    ExceptHandler(
                                                        type=Name(id='AttributeError', ctx=Load()),
                                                        name=None,
                                                        body=[
                                                    Raise(type=Name(id='__yieldfrom_err__', ctx=Load()), inst=None, tback=None)
                                                        ]
                                                    )
                                                ],
                                                orelse=[
                                                    Try(
                                                        body=[
                                                            Assign(
                                                                targets=[Name(id='__yieldfrom_out__', ctx=Store())],
                                                                value=Call(
                                                                    func=Name(id='__yieldfrom_method__', ctx=Load()),
                                                                    args=[],
                                                                    keywords=[],
                                                                    starargs=Name(id='__yieldfrom_exc_info__', ctx=Load()),
                                                                    kwargs=None
                                                                )
                                                            )
                                                        ],
                                                        handlers=[
                                                            ExceptHandler(
                                                                type=Name(id='StopIteration', ctx=Load()),
                                                                name=Name(id='__yieldfrom_err__', ctx=Store()),
                                                                body=[
                                                                    Assign(
                                                                        targets=[Name(id='__yieldfrom_result__', ctx=Store())],
                                                                        value=Call(func=Name(id='__yieldfrom_gen_result__', ctx=Load()), args=[Name(id='__yieldfrom_err__', ctx=Load())], keywords=[], starargs=None, kwargs=None)
                                                                    ),
                                                                Break()
                                                                ]
                                                            )
                                                        ],
                                                        orelse=[]
                                                    )
                                                ],
                                            )
                                        ])
                                ],
                                orelse=[
                                    Try(
                                        body=[
                                            If(test=Compare(left=Name(id='__yieldfrom_in__', ctx=Load()), ops=[Is()], comparators=[Name(id='None', ctx=Load())]),
                                               body=[
                                                   Assign(
                                                       targets=[Name(id='__yieldfrom_out__', ctx=Store())],
                                                       value=Call(
                                                           func=Name(id='next', ctx=Load()),
                                                           args=[Name(id='__yieldfrom_iter__', ctx=Load())],
                                                           keywords=[],
                                                           starargs=None,
                                                           kwargs=None
                                                       )
                                                   )
                                               ],
                                               orelse=[
                                                   Assign(
                                                       targets=[Name(id='__yieldfrom_out__', ctx=Store())],
                                                       value=Call(
                                                           func=Attribute(
                                                               value=Name(id='__yieldfrom_iter__', ctx=Load()),
                                                               attr='send',
                                                               ctx=Load()),
                                                           args=[
                                                               Name(id='__yieldfrom_in__', ctx=Load())
                                                           ],
                                                           keywords=[],
                                                           starargs=None,
                                                           kwargs=None))])
                                        ],
                                        handlers=[
                                            ExceptHandler(
                                                type=Name(id='StopIteration', ctx=Load()),
                                                name=Name(id='__yieldfrom_err__', ctx=Store()),
                                                body=[
                                                    Assign(
                                                        targets=[Name(id='__yieldfrom_result__', ctx=Store())],
                                                        value=Call(
                                                            func=Name(id='__yieldfrom_gen_result__', ctx=Load()),
                                                            args=[Name(id='__yieldfrom_err__', ctx=Load())],
                                                            keywords=[],
                                                            starargs=None,
                                                            kwargs=None)
                                                    ),
                                                    Break()])
                                        ],
                                        orelse=[])
                                ]
                            )
                        ],
                        orelse=[]
                )
            ],
        )
    ]
    if targets:
        output.append(Assign(
            targets=targets,
            value=Name(id='__yieldfrom_result__', ctx=Load())))

    for o in output:
        for node in walk(o):
            node.lineno = generator.lineno
            node.col_offset = generator.col_offset
            if PY3:
                if (isinstance(node, ExceptHandler) and
                    isinstance(node.name, Name)):
                    node.name = node.name.id
                elif isinstance(node, Try):
                    node.finalbody = []

    return output


def ast_to_dict(astobj, dictclass=odict):
    def recurse(o):
        return ast_to_dict(o, dictclass=dictclass)
    if isinstance(astobj, list):
        return [recurse(x) for x in astobj]
    if isinstance(astobj, dict):
        return {k: recurse(x) for k, x in astobj.items()}
    if not isinstance(astobj, AST):
        return astobj
    d = dictclass()
    d['_class'] = astobj.__class__.__name__
    for attr in astobj._attributes:
        d[attr] = recurse(getattr(astobj, attr, '<unset>'))
    for field in astobj._fields:
        d[field] = recurse(getattr(astobj, field, '<unset>'))
    return d


def parse_func(func):
    if inspect.ismethod(func):
        func = func.im_func
    assert inspect.isfunction(func)
    code = get_function_code(func)
    lineno = code.co_firstlineno - 1
    return compile(
        '\n' * lineno + inspect.getsource(code),
        '<unknown>',
        mode='exec',
        flags=PyCF_ONLY_AST | get_future_flags(func),
        dont_inherit=True)


def recompile_func(func, astobj):
    mod_code = compile(
        astobj, inspect.getfile(func), 'exec',
        flags=get_future_flags(func),
        dont_inherit=True
    )
    out = get_function_globals(func).copy()
    out['__yieldfrom_gen_result__'] = gen_result
    out['__yieldfrom_gen_close__'] = gen_close
    out['__yieldfrom_get_exc_info__'] = sys.exc_info
    exec_(mod_code, out)
    return out[astobj.body[0].name]


def expand_yield_from_in_list(func, body):
    """body may be a body of func's descendant node."""
    num_replacements = 0
    i = 0
    while i < len(body):
        stmt = body[i]
        if (isinstance(stmt, Expr) and
            isinstance(stmt.value, Call) and
            _resolve(func, stmt.value.func) is yield_from_):
            replacement = create_yieldfrom_ast(
                targets=None,
                generator=stmt.value.args[0])
            body[i:i+1] = replacement
            i += len(replacement)
            num_replacements += 1

        elif (isinstance(stmt, Assign) and
              isinstance(stmt.value, Call) and
              _resolve(func, stmt.value.func) is yield_from_):
            replacement = create_yieldfrom_ast(
                targets=stmt.targets,
                generator=stmt.value.args[0])
            body[i:i+1] = replacement
            i += len(replacement)
            num_replacements += 1
        else:
            i += 1
    return num_replacements


def expand_yield_from(func):
    mod = parse_func(func)
    func_ast = mod.body[0]
    # print json.dumps(ast_to_dict(mod), indent=1)

    func_ast.decorator_list = [
        expr for expr in getattr(func_ast.decorator_list, 'decorator_list', [])
        if _resolve(func, expr) is not expand_yield_from]

    num_replacements = 0
    for node in walk(func_ast):
        for name, field in iter_fields(node):
            if isinstance(field, list):
                num_replacements += expand_yield_from_in_list(
                    func, field)

    if num_replacements > 0:
        return recompile_func(func, mod)
    else:
        return func
