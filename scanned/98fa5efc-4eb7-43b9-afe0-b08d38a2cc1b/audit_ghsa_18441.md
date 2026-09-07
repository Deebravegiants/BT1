# [H] Pillow vulnerability can cause write buffer overflow on BCn encoding

## Summary
Severity: High
Advisory: GHSA-xg8h-j46f-w952
CVE: CVE-2025-48379
CWE: CWE-122
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-07-01
Source: https://github.com/advisories/GHSA-xg8h-j46f-w952
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=11.2.0 <11.3.0

## Details
There is a heap buffer overflow when writing a sufficiently large (>64k encoded with default settings) image in the DDS format due to writing into a buffer without checking for available space. 

This only affects users who save untrusted data as a compressed DDS image. 

* Unclear how large the potential write could be. It is likely limited by process segfault, so it's not necessarily deterministic. It may be practically unbounded. 
* Unclear if there's a restriction on the bytes that could be emitted. It's likely that the only restriction is that the bytes would be emitted in chunks of 8 or 16. 

This was introduced in Pillow 11.2.0 when the feature was added.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-xg8h-j46f-w952
- https://nvd.nist.gov/vuln/detail/CVE-2025-48379
- https://github.com/python-pillow/Pillow/pull/9041
- https://github.com/python-pillow/Pillow/commit/ef98b3510e3e4f14b547762764813d7e5ca3c5a4
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2025-61.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/11.3.0
