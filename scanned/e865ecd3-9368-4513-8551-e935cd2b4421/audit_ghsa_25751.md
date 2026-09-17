# [H] golang.org/x/crypto/ssh Denial of service via crafted Signer

## Summary
Severity: High
Advisory: GHSA-8c26-wmh5-6g9v
CVE: CVE-2022-27191
CWE: CWE-327
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-19
Source: https://github.com/advisories/GHSA-8c26-wmh5-6g9v
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20220314234659-1baeb1ce4c0b

## Details
The golang.org/x/crypto/ssh package before 0.0.0-20220314234659-1baeb1ce4c0b for Go allows an attacker to crash a server in certain circumstances involving AddHostKey.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27191
- https://security.netapp.com/advisory/ntap-20220429-0002
- https://raw.githubusercontent.com/golang/vulndb/df2d3d326300e2ae768f00351ffa96cc2c56cf54/reports/GO-2021-0356.yaml
- https://pkg.go.dev/vuln/GO-2021-0356
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZY2SLWOQR4ZURQ7UBRZ7JIX6H6F5JHJR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQNPPQWSTP2IX7SHE6TS4SP4EVMI5EZK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZFUNHFHQVJSADNH7EZ3B53CYDZVEEPBP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z55VUVGO7E5PJFXIOVAY373NZRHBNCI5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YHYRQB7TRMHDB3NEHW5XBRG7PPMUTPGV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RQXU752ALW53OJAF5MG3WMR5CCZVLWW6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QTFOIDHQRGNI4P6LYN6ILH5G443RYYKB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J5WPM42UR6XIBQNQPNQHM32X7S4LJTRX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HHGBEGJ54DZZGTXFUQNS7ZIG3E624YAF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZ3S7LB65N54HXXBCB67P4TTOHTNPP5O
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DLUJZV3HBP56ADXU6QH2V7RNYUPMVBXQ
- https://groups.google.com/g/golang-announce/c/-cp44ypCT5s
- https://groups.google.com/g/golang-announce
- https://go.googlesource.com/crypto/+/1baeb1ce4c0b006eff0f294c47cb7617598dfb3d
- https://go.dev/cl/392355
- https://cs.opensource.google/go/x/crypto
