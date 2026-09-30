# [M] Path Traversal in SharpZipLib

## Summary
Severity: Medium
Advisory: GHSA-2x7h-96h5-rq84
CVE: CVE-2021-32841
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-2x7h-96h5-rq84
Type: github-advisory

## Affected
- NuGet: `SharpZipLib` — affected >=1.3.0 <1.3.3

## Details
SharpZipLib (or #ziplib) is a Zip, GZip, Tar and BZip2 library. Starting version 1.3.0 and prior to version 1.3.3, a check was added if the destination file is under destination directory. However, it is not enforced that `destDir` ends with slash. If the `destDir` is not slash terminated like `/home/user/dir` it is possible to create a file with a name thats begins with the destination directory, i.e. `/home/user/dir.sh`. Because of the file name and destination directory constraints, the arbitrary file creation impact is limited and depends on the use case. Version 1.3.3 contains a patch for this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32841
- https://github.com/icsharpcode/SharpZipLib/commit/5c3b293de5d65b108e7f2cd0ea8f81c1b8273f78
- https://github.com/icsharpcode/SharpZipLib
- https://github.com/icsharpcode/SharpZipLib/releases/tag/v1.3.3
- https://securitylab.github.com/advisories/GHSL-2021-125-sharpziplib
