# [H] Improper Input Validation in GoGo Protobuf

## Summary
Severity: High
Advisory: GHSA-c3h9-896r-86jm
CVE: CVE-2021-3121
CWE: CWE-129, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-03-28
Source: https://github.com/advisories/GHSA-c3h9-896r-86jm
Type: github-advisory

## Affected
- Go: `github.com/gogo/protobuf` — affected >=0 <1.3.2

## Details
An issue was discovered in GoGo Protobuf before 1.3.2. plugin/unmarshal/unmarshal.go lacks certain index validation, aka the "skippy peanut butter" issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3121
- https://github.com/gogo/protobuf/commit/b03c65ea87cdc3521ede29f62fe3ce239267c1bc
- https://discuss.hashicorp.com/t/hcsec-2021-23-consul-exposed-to-denial-of-service-in-gogo-protobuf-dependency/29025
- https://github.com/gogo/protobuf
- https://github.com/gogo/protobuf/compare/v1.3.1...v1.3.2
- https://lists.apache.org/thread.html/r68032132c0399c29d6cdc7bd44918535da54060a10a12b1591328bff@%3Cnotifications.skywalking.apache.org%3E
- https://lists.apache.org/thread.html/r88d69555cb74a129a7bf84838073b61259b4a3830190e05a3b87994e@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rc1e9ff22c5641d73701ba56362fb867d40ed287cca000b131dcf4a44@%3Ccommits.pulsar.apache.org%3E
- https://pkg.go.dev/vuln/GO-2021-0053
- https://security.netapp.com/advisory/ntap-20210219-0006
