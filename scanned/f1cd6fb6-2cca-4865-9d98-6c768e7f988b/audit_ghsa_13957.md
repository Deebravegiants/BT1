# [H] golang.org/x/net vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-vvpx-j8f3-3w6h
CVE: CVE-2022-41723
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-17
Source: https://github.com/advisories/GHSA-vvpx-j8f3-3w6h
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.7.0

## Details
A maliciously crafted HTTP/2 stream could cause excessive CPU consumption in the HPACK decoder, sufficient to cause a denial of service from a small number of small requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41723
- https://go.dev/cl/468135
- https://go.dev/cl/468295
- https://go.dev/issue/57855
- https://groups.google.com/g/golang-announce/c/V0aBFqaFs_E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4BUK2ZIAGCULOOYDNH25JPU6JBES5NF2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4MA5XS5DAOJ5PKKNG5TUXKPQOFHT5VBC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/REMHVVIBDNKSRKNOTV7EQSB7CYQWOUOU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGW7GE2Z32ZT47UFAQFDRQE33B7Q7LMT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RLBQ3A7ROLEQXQLXFDLNJ7MYPKG5GULE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T7N5GV4CHH6WAGX3GFMDD3COEOVCZ4RI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XX3IMUTZKRQ73PBZM4E2JP4BKYH4C6XE
- https://pkg.go.dev/vuln/GO-2023-1571
- https://security.gentoo.org/glsa/202311-09
- https://vuln.go.dev/ID/GO-2023-1571.json
- https://www.couchbase.com/alerts
