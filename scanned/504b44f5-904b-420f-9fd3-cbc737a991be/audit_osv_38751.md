# [M] Insufficient input validation of internal web server

## Summary
Severity: Medium
Advisory: CVE-2026-42005
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-42005
Type: osv

## Details
An attacker can send a web request that causes unlimited memory 
allocation in the internal web server, leading to a denial of service. 
The internal web server is disabled by default.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/authoritative/security-advisories/powerdns-advisory-powerdns-2026-07.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42005.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42005
- https://github.com/PowerDNS/pdns
