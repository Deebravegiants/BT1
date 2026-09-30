# [H] Denial of Service in miekg-dns

## Summary
Severity: High
Advisory: GHSA-p55x-7x9v-q8m4
CVE: CVE-2017-15133
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-p55x-7x9v-q8m4
Type: github-advisory

## Affected
- Go: `github.com/miekg/dns` — affected >=0 <1.0.4

## Details
A denial of service flaw was found in miekg-dns before 1.0.4. A remote attacker could use carefully timed TCP packets to block the DNS server from accepting new connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15133
- https://github.com/miekg/dns/issues/627
- https://github.com/miekg/dns/pull/631
- https://github.com/miekg/dns/commit/43913f2f4fbd7dcff930b8a809e709591e4dd79e
- https://bugzilla.redhat.com/show_bug.cgi?id=1538763
- https://pkg.go.dev/vuln/GO-2020-0006
