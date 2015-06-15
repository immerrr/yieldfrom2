import sys

def gen_close(iterator):
    try:
        close_method = iterator.close
    except AttributeError:
        pass
    else:
        close_method()


def gen_result(stop_iteration):
    if len(stop_iteration.args) > 0:
        return stop_iteration.args[0]
    else:
        return None


def yield_from_foobar(generator):
    x = 'foobar'
    __yieldfrom_iter__ = iter(generator)
    try:
        __yieldfrom_out__ = next(__yieldfrom_iter__)
    except StopIteration as __yieldfrom_err__:
        __yieldfrom_result__ = gen_result(__yieldfrom_err__)
    else:
        while 1:
            try:
                __yieldfrom_in__ = yield __yieldfrom_out__
            except GeneratorExit as __yieldfrom_err__:
                gen_close(__yieldfrom_iter__)
                raise __yieldfrom_err__
            except BaseException as __yieldfrom_err__:
                # Propagate gen.throw() downwards.
                __yieldfrom_exc_info__ = sys.exc_info()
                try:
                    __yieldfrom_method__ = __yieldfrom_iter__.throw
                except AttributeError:
                    raise __yieldfrom_err__
                else:
                    try:
                        __yieldfrom_out__ = __yieldfrom_method__(*__yieldfrom_exc_info__)
                    except StopIteration as __yieldfrom_err__:
                        __yieldfrom_result__ = gen_result(__yieldfrom_err__)
                        break
            else:
                try:
                    if __yieldfrom_in__ is None:
                        __yieldfrom_out__ = next(__yieldfrom_iter__)
                    else:
                        __yieldfrom_out__ = __yieldfrom_iter__.send(__yieldfrom_in__)
                except StopIteration as __yieldfrom_err__:
                    __yieldfrom_result__ = gen_result(__yieldfrom_err__)
                    break
    RESULT = __yieldfrom_result__
    y = 'foobar' + str(RESULT)
    yield x, y
