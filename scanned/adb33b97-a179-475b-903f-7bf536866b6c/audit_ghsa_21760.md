# [H] Path Traversal in SharpZipLib

## Summary
Severity: High
Advisory: GHSA-m22m-h4rf-pwq3
CVE: CVE-2021-32840
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-m22m-h4rf-pwq3
Type: github-advisory

## Affected
- NuGet: `SharpZipLib` — affected >=0 <1.3.3

## Details
SharpZipLib (or #ziplib) is a Zip, GZip, Tar and BZip2 library. Prior to version 1.3.3, a TAR file entry `../evil.txt` may be extracted in the parent directory of `destFolder`. This leads to arbitrary file write that may lead to code execution. The vulnerability was patched in version 1.3.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32840
- https://github.com/icsharpcode/SharpZipLib/commit/a0e96de70b5264f4c919b09253b1522bc7a221cc
- https://github.com/icsharpcode/SharpZipLib
- https://github.com/icsharpcode/SharpZipLib/releases/tag/v1.3.3
- https://securitylab.github.com/advisories/GHSL-2021-125-sharpziplib
