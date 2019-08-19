"""MORE IPython ``%magic`` functions."""

import os
import sys
from inspect import getsourcefile, getsourcelines

import zetup
from moreshell import IPython_magic, IPython_magic_module, with_arguments
from moretools import getfunc
from path import Path
from six import reraise
from zetup import call

IPython_magic_module(__name__, ['dev'])


@IPython_magic(
    with_arguments
    ('object')
    ('-e', '--editor')
    ('-f', '--format')
)
def dev(shell, args):
    """
    Open the file containing the code for the given object.

    And jump to the location of its definition

    By taking the command from the ``--editor`` option or from the ``EDITOR``
    environment variable, and running it with an argument of the format
    ``filepath:lineno``
    """
    editor = args.editor or os.environ.get('EDITOR')
    if not editor:
        raise RuntimeError("No EDITOR environment variable defined")

    obj = eval(args.object, shell.user_ns)
    exceptions = []
    try:
        filename = getsourcefile(obj)
    except TypeError as exc:
        exceptions.append(exc)

        obj = type(obj)
        try:
            filename = getsourcefile(obj)
        except TypeError as exc:
            exceptions.append(exc)

            def getfile(base):
                try:
                    return getsourcefile(base)

                except TypeError as exc:
                    exceptions.append(exc)
                    return None

            for obj in obj.mro()[1:]:
                filename = getfile(obj)
                if filename is not None:
                    break

                else:
                    raise TypeError(
                        "Can't find any source file for given object, its "
                        "class, or base classes: {!r}"
                        .format(exceptions))

    try:
        lineno = getsourcelines(obj)[1]
    except TypeError:
        lineno = 0

    editor_arg = Path(filename).realpath()
    if lineno:
        editor_arg += ":{}".format(lineno)
    return call(editor.split() + [editor_arg])
