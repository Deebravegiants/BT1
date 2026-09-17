# [M] Path Traversal in SharpZipLib

## Summary
Severity: Medium
Advisory: GHSA-mm6g-mmq6-53ff
CVE: CVE-2021-32842
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-mm6g-mmq6-53ff
Type: github-advisory

## Affected
- NuGet: `SharpZipLib` — affected >=1.0.0 <1.3.3

## Details
SharpZipLib (or #ziplib) is a Zip, GZip, Tar and BZip2 library. Starting version 1.0.0 and prior to version 1.3.3, a check was added if the destination file is under a destination directory. However, it is not enforced that `_baseDirectory` ends with slash. If the _baseDirectory is not slash terminated like `/home/user/dir` it is possible to create a file with a name thats begins as the destination directory one level up from the directory, i.e. `/home/user/dir.sh`. Because of the file name and destination directory constraints, the arbitrary file creation impact is limited and depends on the use case. Version 1.3.3 fixed this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32842
- https://github.com/icsharpcode/SharpZipLib
- https://github.com/icsharpcode/SharpZipLib/releases/tag/v1.3.3
- https://securitylab.github.com/advisories/GHSL-2021-125-sharpziplib
