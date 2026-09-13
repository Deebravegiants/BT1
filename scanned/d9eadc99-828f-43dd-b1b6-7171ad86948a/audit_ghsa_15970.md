# [M] Exiv2 has an out-of-bounds read in QuickTimeVideo::NikonTagsDecoder

## Summary
Severity: Medium
Advisory: GHSA-g9xm-7538-mq8w
CVE: CVE-2024-24826
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-17
Source: https://github.com/advisories/GHSA-g9xm-7538-mq8w
Type: github-advisory

## Affected
- PyPI: `exiv2` — affected >=0.16.0 <0.16.1

## Details
### Impact
An out-of-bounds read was found in Exiv2 version v0.28.1. The vulnerable function, `QuickTimeVideo::NikonTagsDecoder`, was new in v0.28.0 (see https://github.com/Exiv2/exiv2/pull/2337), so Exiv2 versions before v0.28 are _not_ affected. Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. The out-of-bounds read is triggered when Exiv2 is used to read the metadata of a crafted video file.

### Patches
The bug is fixed in version v0.28.2.

### For more information
Please see our [security policy](https://github.com/Exiv2/exiv2/security/policy) for information about Exiv2 security.

### Credit
This bug was found by [OSS-Fuzz](https://github.com/google/oss-fuzz).

## References
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-g9xm-7538-mq8w
- https://nvd.nist.gov/vuln/detail/CVE-2024-24826
- https://github.com/Exiv2/exiv2/pull/2337
- https://github.com/Exiv2/exiv2
- https://github.com/pypa/advisory-database/tree/main/vulns/exiv2/PYSEC-2024-106.yaml
