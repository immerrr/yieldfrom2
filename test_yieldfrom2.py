from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


from yieldfrom2.syntax import expand_yield_from, yield_from_


def foobar():
    for i in range(3):
        try:
            yield i
        except RuntimeError as e:
            print("Caught error:", e)


@expand_yield_from
def yieldfrom_test():
    try:
        x = yield_from_(foobar())
    except Exception as err:
        print("yieldfrom exc:", err)
        yield_from_([100, 200, 300])
    else:
        print("yieldfrom result:", x)


if __name__ == '__main__':
    it = yieldfrom_test()
    for x in it:
        print(x)
        if x == 1:
            print(it.throw(RuntimeError("hello world")))
            print(it.throw(Exception("cuckoo")))
        if x == 200:
            it.close()
