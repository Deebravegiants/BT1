# [M] Denial of service via IXFR queries

## Summary
Severity: Medium
Advisory: CVE-2026-40209
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40209
Type: osv

## Details
An attacker might be able to cause outgoing TCP connections to backend to be stuck until a timeout occurs instead of being released immediately, by sending IXFR queries. This could be used to cause a denial of service if there is a limit to the number of concurrent connections to this backend, or if the process runs out of file descriptors.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40209.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40209
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-09.html
- https://github.com/PowerDNS/pdns
