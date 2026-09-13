# [M] Mishandling of corrupt central directory record in archive/zip

## Summary
Severity: Medium
Advisory: BIT-golang-2024-24789
Aliases: CVE-2024-24789, GO-2024-2888
Ecosystem: Bitnami
Published: 2024-06-07
Source: https://osv.dev/vulnerability/BIT-golang-2024-24789
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.4

## Details
The archive/zip package's handling of certain types of invalid zip files differs from the behavior of most zip implementations. This misalignment could be exploited to create an zip file with contents that vary depending on the implementation reading the file. The archive/zip package now rejects files containing these errors.

## References
- https://go.dev/cl/585397
- https://go.dev/issue/66869
- https://groups.google.com/g/golang-announce/c/XbxouI9gY7k/m/TuoGEhxIEwAJ
- https://pkg.go.dev/vuln/GO-2024-2888
- http://www.openwall.com/lists/oss-security/2024/06/04/1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U5YAEIA6IUHUNGJ7AIXXPQT6D2GYENX7/
- https://security.netapp.com/advisory/ntap-20250131-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2024-24789
