# [H] Out-of-bounds read in Apache Thrift

## Summary
Severity: High
Advisory: GHSA-jq7p-26h5-w78r
CVE: CVE-2019-0210
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-jq7p-26h5-w78r
Type: github-advisory

## Affected
- Go: `github.com/apache/thrift` — affected >=0.9.3 <0.13.0

## Details
In Apache Thrift 0.9.3 to 0.12.0, a server implemented in Go using TJSONProtocol or TSimpleJSONProtocol may panic when feed with invalid input data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0210
- https://github.com/apache/thrift/commit/264a3f318ed3e9e51573f67f963c8509786bcec2
- https://access.redhat.com/errata/RHSA-2020:0804
- https://access.redhat.com/errata/RHSA-2020:0805
- https://access.redhat.com/errata/RHSA-2020:0806
- https://access.redhat.com/errata/RHSA-2020:0811
- https://github.com/apache/thrift
- https://github.com/apache/thrift/blob/master/CHANGES.md#0130
- https://lists.apache.org/thread.html/r2832722c31d78bef7526e2c701ba4b046736e4c851473194a247392f@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r36581cc7047f007dd6aadbdd34e18545ec2c1eb7ccdae6dd47a877a9@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r55609613abab203a1f2c1f3de050b63ae8f5c4a024df0d848d6915ff@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rab740e5c70424ef79fd095a4b076e752109aeee41c4256c2e5e5e142@%3Ccommits.pulsar.apache.org%3E
- https://pkg.go.dev/vuln/GO-2021-0101
- https://security.gentoo.org/glsa/202107-32
- https://www.oracle.com/security-alerts/cpujul2021.html
- http://mail-archives.apache.org/mod_mbox/thrift-dev/201910.mbox/%3C277A46CA87494176B1BBCF5D72624A2A%40HAGGIS%3E
