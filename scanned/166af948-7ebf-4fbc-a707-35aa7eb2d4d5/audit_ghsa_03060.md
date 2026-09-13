# [M] miekg/dns insecurely generates random numbers

## Summary
Severity: Medium
Advisory: GHSA-44r7-7p62-q3fr
CVE: CVE-2019-19794
CWE: CWE-330, CWE-338
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-44r7-7p62-q3fr
Type: github-advisory

## Affected
- Go: `github.com/miekg/dns` — affected >=0 <1.1.25

## Details
The miekg Go DNS package before 1.1.25, as used in CoreDNS before 1.6.6 and other products, improperly generates random numbers because math/rand is used. The TXID becomes predictable, leading to response forgeries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19794
- https://github.com/coredns/coredns/issues/3519
- https://github.com/coredns/coredns/issues/3547
- https://github.com/miekg/dns/issues/1037
- https://github.com/miekg/dns/issues/1043
- https://github.com/miekg/dns/pull/1044
- https://github.com/miekg/dns/commit/8ebf2e419df7857ac8919baa05248789a8ffbf33
- https://github.com/miekg/dns/compare/v1.1.24...v1.1.25
- https://pkg.go.dev/vuln/GO-2020-0008
