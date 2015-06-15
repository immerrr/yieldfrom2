from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


from yieldfrom2.syntax import expand_yield_from, yield_from_, return_


def foobar():
    for i in range(3):
        try:
            x = yield i
            while x is not None:
                x = yield x
        except RuntimeError as e:
            print("Caught error:", e)
    # FIXME: should return in non-generator functions.
    return_(123)


@expand_yield_from
def yieldfrom_test():
    try:
        x = yield_from_(foobar())
        print("yieldfrom result:", x)
        yield_from_([100, 200, 300])
    except Exception as err:
        print("yieldfrom exc:", err)
        yield_from_([1000, 2000])
        yield_from_(foobar())



if __name__ == '__main__':
    it = yieldfrom_test()
    assert next(it) == 0
    assert it.send('foobar') == 'foobar'
    assert next(it) == 1
    assert it.throw(RuntimeError("hello world")) == 2
    assert next(it) == 100
    # FIXME: raises when forwarding the error to list iterator
    # assert it.throw(Exception("cuckoo")) == 1000
    # assert next(it) == 2000
    it.close()
