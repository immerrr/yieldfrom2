import json
import opcode
from collections import OrderedDict as odict

from six import get_function_code



import __future__
FUTURE_FLAGS = [
    __future__.CO_FUTURE_DIVISION,
    __future__.CO_FUTURE_PRINT_FUNCTION,
    __future__.CO_FUTURE_WITH_STATEMENT,
    __future__.CO_FUTURE_ABSOLUTE_IMPORT,
    __future__.CO_FUTURE_UNICODE_LITERALS
]

CO_FLAGS = {
    0x20: 'GEN',
    0x04: 'ARGS',
    0x08: 'KWARGS',
    __future__.CO_FUTURE_DIVISION: 'CO_FUTURE_DIVISION',
    __future__.CO_FUTURE_PRINT_FUNCTION: 'CO_FUTURE_PRINT_FUNCTION',
    __future__.CO_FUTURE_WITH_STATEMENT: 'CO_FUTURE_WITH_STATEMENT',
    __future__.CO_FUTURE_ABSOLUTE_IMPORT: 'CO_FUTURE_ABSOLUTE_IMPORT',
    __future__.CO_FUTURE_UNICODE_LITERALS: 'CO_FUTURE_UNICODE_LITERALS',
}


def get_future_flags(func):
    flags = 0
    for f in FUTURE_FLAGS:
        flags |= f
    return get_function_code(func).co_flags & flags


def flags_str(flags):
    return ', '.join('{1} (0x{0:x})'.format(*t) for t in CO_FLAGS.items()
                     if flags & t[0])


def code_dict(code):
    d = odict()
    d['argcount'] = code.co_argcount
    d['consts'] = code.co_consts
    d['flags'] = flags_str(code.co_flags)
    d['name'] = code.co_name
    d['stacksize'] = code.co_stacksize
    d['cellvars'] = code.co_cellvars
    d['filename'] = code.co_filename
    d['freevars'] = code.co_freevars
    d['names'] = code.co_names
    d['varnames'] = code.co_varnames
    # d['code'] = code.co_code
    d['firstlineno'] = code.co_firstlineno
    d['lnotab'] = code.co_lnotab
    d['nlocals'] = code.co_nlocals
    return d


def func_dict(func):
    d = odict()
    d['name'] = '.'.join([func.__module__, func.__name__])
    d['closure'] = func.func_closure
    d['code'] = code_dict(func.func_code)
    d['defaults'] = func.func_defaults
    return d


def disasm_code(code):
    # yield OFFSET, BYTES, OPNAME, ARGS
    code = code.co_code
    offset = 0
    n = len(code)
    while offset < n:
        oplen = 1
        op = ord(code[offset + oplen - 1])
        extended_arg = 0
        while op == opcode.EXTENDED_ARG:
            oparg = (ord(code[offset + 1]) + ord(code[offset + 2]) * 256 +
                     extended_arg)
            extended_arg = oparg * 65536
            oplen += 3
            op = ord(code[offset + oplen - 1])
        has_argument = op >= opcode.HAVE_ARGUMENT
        if has_argument:
            oplen += 2
            oparg = (ord(code[offset + 1]) + ord(code[offset + 2]) * 256 +
                     extended_arg)
        else:
            oparg = None
        opname = opcode.opname[op]
        yield offset, op, code[offset:offset+oplen], opname, oparg
        offset += oplen


def disasm_func(func):
    return list(disasm_code(get_function_code(func)))


def print_func(func):
    print(json.dumps(func_dict(func), indent=1))
