# [M] Unbounded memory allocation by internal web server

## Summary
Severity: Medium
Advisory: CVE-2026-33256
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33256
Type: osv

## Details
An attacker can send a web request that causes unlimited memory allocation in the internal web server, leading to a denial of service. The internal web server is disabled by default.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-03.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33256.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33256
- https://github.com/PowerDNS/pdns
