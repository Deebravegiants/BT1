# [M] Exiv2  has a denial of service due to unbounded recursion in QuickTimeVideo::multipleEntriesDecoder

## Summary
Severity: Medium
Advisory: GHSA-crmj-qh74-2r36
CVE: CVE-2024-25112
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-17
Source: https://github.com/advisories/GHSA-crmj-qh74-2r36
Type: github-advisory

## Affected
- PyPI: `exiv2` — affected >=0.16.0 <0.16.1

## Details
### Impact
A denial-of-service was found in Exiv2 version v0.28.1: an unbounded recursion can cause Exiv2 to crash by exhausting the stack. The vulnerable function, `QuickTimeVideo::multipleEntriesDecoder`, was new in v0.28.0 (see https://github.com/Exiv2/exiv2/pull/2337), so Exiv2 versions before v0.28 are _not_ affected.  Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. The denial-of-service is triggered when Exiv2 is used to read the metadata of a crafted video file.

### Patches
The bug is fixed in version v0.28.2.

### For more information
Please see our [security policy](https://github.com/Exiv2/exiv2/security/policy) for information about Exiv2 security.

### Credit
This bug was found by [OSS-Fuzz](https://github.com/google/oss-fuzz).

## References
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-crmj-qh74-2r36
- https://nvd.nist.gov/vuln/detail/CVE-2024-25112
- https://github.com/Exiv2/exiv2/pull/2337
- https://github.com/Exiv2/exiv2
- https://github.com/pypa/advisory-database/tree/main/vulns/exiv2/PYSEC-2024-107.yaml
