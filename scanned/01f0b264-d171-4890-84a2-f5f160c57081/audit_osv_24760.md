# [H] CVE-2023-26130

## Summary
Severity: High
Advisory: CVE-2023-26130
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-26130
Type: osv

## Details
Versions of the package yhirose/cpp-httplib before 0.12.4 are vulnerable to CRLF Injection when untrusted user input is used to set the content-type header in the HTTP .Patch, .Post, .Put and .Delete requests. This can lead to logical errors and other misbehaviors.**Note:** This issue is present due to an incomplete fix for [CVE-2020-11709](https://security.snyk.io/vuln/SNYK-UNMANAGED-YHIROSECPPHTTPLIB-2366507).

## References
- https://gist.github.com/dellalibera/094aece17a86069a7d27f93c8aba2280
- https://github.com/yhirose/cpp-httplib/releases/tag/v0.12.4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2RY6PKBU73I45L6YWNYCUK2XBEXEFX7L/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JY2E7EIRWQMKH6GY4OZOWWBZBY3Q7CGS/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NYODHZECXYFC2BNODZPZXZAXOKGMCYAP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U6MO4FSKYNSAJVUXYP7LRY7ARUIGKBFL/
- https://security.snyk.io/vuln/SNYK-UNMANAGED-YHIROSECPPHTTPLIB-5591194
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26130.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26130
- https://github.com/yhirose/cpp-httplib/commit/5b397d455d25a391ba346863830c1949627b4d08
