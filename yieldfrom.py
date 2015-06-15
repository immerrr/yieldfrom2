from yieldfrom.syntax import expand_yield_from, yield_from_


def foobar():
    for i in xrange(3):
        try:
            yield i
        except RuntimeError as e:
            print "Caught error: %s" % e


@expand_yield_from
def yieldfrom_test():
    x = yield_from_(foobar())
    print "yieldfrom result: %s" % x


if __name__ == '__main__':
    it = yieldfrom_test()
    print next(it)
    for x in it:
        print x
        if x == 1:
            print it.throw(RuntimeError("hello world"))
