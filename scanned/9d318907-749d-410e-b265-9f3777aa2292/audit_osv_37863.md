# [M] Possible file descriptor exhaustion in forward-dnsupdate

## Summary
Severity: Medium
Advisory: CVE-2026-33610
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33610
Type: osv

## Details
A rogue primary server may cause file descriptor exhaustion and eventually a denial of service, when a PowerDNS secondary server forwards a DNS update request to it.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/authoritative/security-advisories/powerdns-advisory-powerdns-2026-05.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33610.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33610
- https://github.com/PowerDNS/pdns
