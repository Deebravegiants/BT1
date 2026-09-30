# [M] Resource exhaustion via DoQ/DoH3 connections

## Summary
Severity: Medium
Advisory: CVE-2026-33254
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33254
Type: osv

## Details
An attacker can create a large number of concurrent DoQ or DoH3 connections, causing unlimited memory allocation in DNSdist and leading to a denial of service. DOQ and DoH3 are disabled by default.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33254.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33254
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-04.html
- https://github.com/PowerDNS/pdns
