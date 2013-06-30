##
# This file contains tool functions for madx.pyx
#

from cern.pymad.io import tfs,tfsDict


def _fixcmd(cmd):
    '''
    Makes sure command is sane.
    '''
    if not isinstance(cmd, basestring):
        raise TypeError("ERROR: input must be a string, not "+str(type(cmd)))
    if len(cmd.strip())==0:
        return 0
    if cmd.strip()[-1]!=';':
        cmd+=';'
    # for very long commands (probably parsed in from a file)
    # we split and only run one line at the time.
    if len(cmd)>10000:
        cmd=cmd.split('\n')
    return cmd

def _get_dict(tmpfile,retdict):
    '''
     Returns a dictionary from the temporary file.
    '''
    if retdict:
        return tfsDict(tmpfile)
    return tfs(tmpfile)

def _add_range(madrange):
    if madrange:
        if isinstance(madrange, basestring):
            return 'range='+madrange+','
        elif isinstance(madrange, list):
            return 'range='+madrange[0]+'/'+madrange[1]+','
        elif isinstance(madrange, dict):
            return 'range='+madrange['first']+'/'+madrange['last']+','
        else:
            raise TypeError("Wrong range type/format")
    return ''

def _add_offsets(offsets):
    if offsets:
        return 'offsetelem="'+offsets+'",'
    return ''

def _mad_command(cmd, *args, **kwargs):
    """
    Create a MAD-X command from its name and parameter list.
    
    @param cmd [string] name of the MAD command
    @params *args [list] ordered arguments to the MAD command
    @params **kwargs [dict] unordered arguments to the MAD command

    Examples:

    >>> _mad_command('twiss', ('sequence', lhc), 'centre', dx=2, betx=3, bety=8)
    twiss, sequence=lhc, centre, betx=3, bety=3, dx=2;

    >>> _mad_command('option', echo=False)
    option, -echo;

    >>> _mad_command('constraint', ('betx', '<', 3.13), 'bety < 3.5')
    constraint, betx<3.13, bety < 3.5;

    >>> _mad_command('constraint', **{'betx<3.13':True})
    constraint, betx<3.13;

    Note that alphabetic order is enforced on kwargs, such that results are
    always reproducible.

    """
    mad = cmd
    fullargs = list(args) + sorted(kwargs.items(), key=lambda i: i[0])
    for arg in fullargs:
        if isinstance(arg, tuple):
            if len(arg) == 3:
                key, op, value = arg
            else:
                key, value = arg
                op = '='
        else:
            key = arg
            value = True

        key = str(key)
        if key.lower() == 'range':
            mad += ', ' + _add_range(value)[:-1]
        elif isinstance(value, bool):
            mad += ', ' + ('' if value else '-') + key
        else:
            mad += ', ' + key + op + str(value)
    mad += ';\n'
    return mad

def _call(fn, *params):
    args = []
    kwargs = {}
    for v in params:
        if isinstance(v, dict):
            kwargs.update(v)
        elif isinstance(v, list):
            args += v
        else:
            raise TypeError("_call accepts only lists or dicts")
    return fn(*args, **kwargs)

def _mad_command_unpack(*arglists, **kwargs):
    return _call(_mad_command, kwargs, *arglists)

