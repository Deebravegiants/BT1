# [H] Fickling has `always_check_safety()` bypass: pickle.loads and _pickle.loads remain unhooked

## Summary
Severity: High
Advisory: GHSA-wccx-j62j-r448
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-wccx-j62j-r448
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.9

## Details
# Assessment

The missing pickle entrypoints `pickle.loads`, `_pickle.loads`, and `_pickle.load` were added to the hook https://github.com/trailofbits/fickling/commit/8c24c6edabceab156cfd41f4d70b650e1cdad1f7.

# Original report

## Summary
`fickling.always_check_safety()` does not hook all pickle entry points. `pickle.loads`, `_pickle.loads`, and `_pickle.load` remain unprotected, enabling malicious payload execution despite global safety mode being enabled.

## Affected versions
`<= 0.1.8` (verified on current upstream HEAD as of 2026-03-03)

## Non-duplication check against published Fickling GHSAs
No published advisory covers hook-coverage bypass in `run_hook()`.
Existing advisories are blocklist/detection bypasses (runpy, pty, cProfile, marshal/types, builtins, network constructors, OBJ visibility, etc.), not runtime hook coverage parity.

## Root cause
`run_hook()` patches only:
- `pickle.load`
- `pickle.Unpickler`
- `_pickle.Unpickler`

It does not patch:
- `pickle.loads`
- `_pickle.load`
- `_pickle.loads`

## Reproduction (clean upstream)
```python
import io, pickle, _pickle
from unittest.mock import patch
import fickling
from fickling.exception import UnsafeFileError

class Payload:
    def __reduce__(self):
        import subprocess
        return (subprocess.Popen, (['echo','BYPASS'],))

data = pickle.dumps(Payload())
fickling.always_check_safety()

# Bypass path
with patch('subprocess.Popen') as popen_mock:
    pickle.loads(data)
    print('bypass sink called?', popen_mock.called)  # True

# Control path is blocked
with patch('subprocess.Popen') as popen_mock:
    try:
        pickle.load(io.BytesIO(data))
    except UnsafeFileError:
        pass
    print('blocked sink called?', popen_mock.called)  # False
```

Observed on vulnerable code:
- `pickle.loads` executes payload
- `pickle.load` is blocked

## Minimal patch diff
```diff
--- a/fickling/hook.py
+++ b/fickling/hook.py
@@
 def run_hook():
-    pickle.load = loader.load
+    pickle.load = loader.load
+    _pickle.load = loader.load
+    pickle.loads = loader.loads
+    _pickle.loads = loader.loads
```

## Validation after patch
- `pickle.loads`, `_pickle.loads`, and `_pickle.load` all raise `UnsafeFileError`
- sink not called in any path

Regression tests added locally:
- `test_run_hook_blocks_pickle_loads`
- `test_run_hook_blocks__pickle_load_and_loads`
  in `test/test_security_regressions_20260303.py`

## Impact
High-confidence runtime protection bypass for applications that trust `always_check_safety()` as global guard.

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-wccx-j62j-r448
- https://github.com/trailofbits/fickling/commit/8c24c6edabceab156cfd41f4d70b650e1cdad1f7
- https://github.com/trailofbits/fickling
- https://github.com/trailofbits/fickling/releases/tag/v0.1.9
