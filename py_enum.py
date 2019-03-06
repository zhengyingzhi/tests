from ctypes import (
    Structure,
    c_ubyte
)

def make_enum(option, *options):
    """construct a new enum object
    *options: iterable of str, the names of the fields for the enum
    """
    options = (option,) + options
    rangeob = range(len(options))
    inttype = c_ubyte

    class _enum(Structure):
        _fields_ = [(o, inttype) for o in options]

        def __iter__(self):
            return iter(rangeob)

        def __contains__(self, value):
            return 0 <= value < len(options)

        def __repr__(self):
            return '<enum: %s>' % (
                ('%d fields' % len(options))
                if len(options) > 10 else
                repr(options)
            )
    return _enum(*rangeob)
  
  status = make_enum("pending", "filled", "part_filled", "part_cancelled", "cancelled", "rejected")
  print(status.filled)
  
