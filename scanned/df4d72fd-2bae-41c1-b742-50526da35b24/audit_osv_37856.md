# [M] Out-of-bounds read in cache inspection via Lua

## Summary
Severity: Medium
Advisory: CVE-2026-33598
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33598
Type: osv

## Details
A cached crafted response can cause an out-of-bounds read if custom Lua code calls getDomainListByAddress() or getAddressListByDomain() on a packet cache.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33598
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-04.html
- https://github.com/PowerDNS/pdns
