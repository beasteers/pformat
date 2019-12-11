import glob
import pformat as pf

def test_partial_replacement():
    assert pf.pformat('{a}/b/{c}/d/{e}', e='eee') == '{a}/b/{c}/d/eee'

def test_partial_replacement_preserving_specifiers():
    assert pf.pformat('{a:s}/b/{c!s:s}/d/{e}', e='eee') == '{a:s}/b/{c!s:s}/d/eee'

def test_partial_replacement_positional():
    assert pf.pformat('{}/b/{}/d/{}', 'aaa', 'ccc') == 'aaa/b/ccc/d/{}'

def test_partial_replacement_positional_specifiers():
    assert pf.pformat('{:s}/b/{}/d/{:s}', 'aaa', 'ccc') == 'aaa/b/ccc/d/{:s}'

def test_glob_replacement():
    assert pf.gformat('{:s}/b/{}/d/{:s}', 'aaa', 'ccc') == 'aaa/b/ccc/d/*'

def test_default_replacement():
    assert (pf.dformat(
        '{:.2f}/b/{}/d/{blah._[1]:.2f}', 1, 2, blah=3) ==
        '1.00/b/2/d/3.00')

    # assert (pf.dformat(
    #     '{:.2f}/b/{}/d/{blah._[1]:.2f}', 1) ==
    #     '1.00/b/{}/d/1')

    assert (pf.dformat(
        '{:.2f}/b/2/d/{blah._[None]:.2f}', 1, 2) ==
        '1.00/b/2/d/None')

    assert (pf.dformat(
        '{:.2f}/b/{}/d/{blah._[---]:.2f}', 1, 2) ==
        '1.00/b/2/d/---')
