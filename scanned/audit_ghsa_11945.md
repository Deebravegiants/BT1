# [H] UltraJSON has a Memory Leak parsing large integers allows DoS 

## Summary
Severity: High
Advisory: GHSA-wgvc-ghv9-3pmm
CVE: CVE-2026-32874
CWE: CWE-401
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-wgvc-ghv9-3pmm
Type: github-advisory

## Affected
- PyPI: `ujson` — affected >=5.4.0 <5.12.0

## Details
#### Summary

ujson 5.4.0 to 5.11.0 inclusive contain an accumulating memory leak in JSON parsing _large_ (outside of the range [-2^63, 2^64 - 1]) integers.

#### Exploitability

Any service that calls `ujson.load()`/`ujson.loads()`/`ujson.decode()` on untrusted inputs is affected and vulnerable to denial of service attacks.

#### Details

The leaked memory is a copy of the string form of the integer plus an additional NULL byte. The leak occurs irrespective of whether the integer parses successfully or is rejected due to having more than `sys.get_int_max_str_digits()` digits, meaning that any sized leak per malicious JSON can be achieved provided that there is no limit on the overall size of the payload.

```python
ujson.loads(str(2 ** 64 - 1))  # No leak
ujson.loads(str(2 ** 64))  # Leaks
ujson.loads(str(10 ** sys.get_int_max_str_digits()))  # Leaks and raises ValueError
```

#### Fix

The leak is fixed in `ujson 5.12.0` (4baeb950df780092bd3c89fc702a868e99a3a1d2). There are no workarounds beyond upgrading to an unaffected version.

#### Credits

Discovered by Cameron Criswell/Skevros using Coverage-guided fuzzing (libFuzzer + AddressSanitizer)

## References
- https://github.com/ultrajson/ultrajson/security/advisories/GHSA-wgvc-ghv9-3pmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32874
- https://github.com/ultrajson/ultrajson/commit/4baeb950df780092bd3c89fc702a868e99a3a1d2
- https://github.com/ultrajson/ultrajson
- https://github.com/ultrajson/ultrajson/releases/tag/5.12.0
