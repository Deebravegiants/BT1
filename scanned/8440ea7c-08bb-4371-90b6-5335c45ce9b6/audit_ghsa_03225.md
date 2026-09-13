# [H] miekg/dns parsing error leads to nil pointer dereference and DoS

## Summary
Severity: High
Advisory: GHSA-9jcx-pr2f-qvq5
CVE: CVE-2018-17419
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-9jcx-pr2f-qvq5
Type: github-advisory

## Affected
- Go: `github.com/miekg/dns` — affected >=0 <1.0.10

## Details
An issue was discovered in `setTA` in `scan_rr.go` in the Miek Gieben DNS library before 1.0.10 for Go. A `dns.ParseZone()` parsing error causes a segmentation violation, leading to denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17419
- https://github.com/miekg/dns/issues/742
- https://github.com/miekg/dns/pull/745/commits/f71d7d9d77d439b30a5e50900df5b1f988a50e5e
- https://github.com/miekg/dns/commit/501e858f679edecd4a38a86317ce50271014a80d
- https://github.com/miekg/dns
- https://pkg.go.dev/vuln/GO-2020-0028
