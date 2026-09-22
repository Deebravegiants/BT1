# [H] UltraJSON has a Memory Leak in ujson.dump() on Write Failure

## Summary
Severity: High
Advisory: GHSA-c38f-wx89-p2xg
CVE: CVE-2026-44660
CWE: CWE-401
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-c38f-wx89-p2xg
Type: github-advisory

## Affected
- PyPI: `ujson` — affected >=0 <5.12.1

## Details
### Summary

When `ujson.dump()` writes to a file-like object and the write operation raises an exception, the serialized JSON string object is not decremented, leaking memory. Each failed write operation leaks the full size of the serialized payload.

Code that uses `ujson.dumps()` rather than `ujson.dump()` or only JSON load/decode methods is unaffected.

### Details

**Vulnerability Location:**
- `src/ujson/python/objToJSON.c:913` - `objToJSONFile()` function start
- `src/ujson/python/objToJSON.c:931` - Error return on write failure
- `src/ujson/python/objToJSON.c:942` - Early return without cleanup
 
**Root Cause:**

The `objToJSONFile()` function allocates a Python string object via `ujson_dumps_internal()`, calls the file's `write()` method, and returns early if `write()` raises an exception—but never calls `Py_DECREF(string)` on the early exit path.

### PoC
```python
import gc, tracemalloc, ujson

class BadFile:
    def write(self, s):
        raise RuntimeError("boom")

obj = {"x": "A" * 200000}

def run():
    try:
        ujson.dump(obj, BadFile())
    except RuntimeError:
        pass

run()
tracemalloc.start()
gc.collect()
base = tracemalloc.get_traced_memory()[0]

for i in range(5):
    run()
    gc.collect()
    cur = tracemalloc.get_traced_memory()[0]
    print(i, cur - base)
```

### Impact

Any application that serializes data through `ujson.dump()` to an attacker-influenced file-like object that can fail can be driven into linear memory growth. An attacker can quickly use up all the memory of say a web server that sends JSON responses using `ujson.dump()` by repeatedly making requests then closing the connection mid response.

### Remediation

The missing dec-refs were added in 82af1d0ac01d09aa40c887b460d44b9d9f4bccd9. We recommend upgrading to [UltraJSON 5.12.1](https://github.com/ultrajson/ultrajson/releases/tag/5.12.1).

### Workarounds

Replacing `ujson.dump(obj, file)` with `file.write(ujson.dumps(obj))` is equivalent (contrary to popular misconception, there are no streaming benefits to using `ujson.dump()`) and will avoid the memory leak.

## References
- https://github.com/ultrajson/ultrajson/security/advisories/GHSA-c38f-wx89-p2xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44660
- https://github.com/ultrajson/ultrajson/commit/82af1d0ac01d09aa40c887b460d44b9d9f4bccd9
- https://github.com/ultrajson/ultrajson
- https://github.com/ultrajson/ultrajson/releases/tag/5.12.1
