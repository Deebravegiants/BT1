# [M] CVE-2022-41841

## Summary
Severity: Medium
Advisory: CVE-2022-41841
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-30
Source: https://osv.dev/vulnerability/CVE-2022-41841
Type: osv

## Details
An issue was discovered in Bento4 through 1.6.0-639. A NULL pointer dereference occurs in AP4_File::ParseStream in Core/Ap4File.cpp, which is called from AP4_File::AP4_File.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41841.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41841
- https://github.com/axiomatic-systems/Bento4/issues/779
