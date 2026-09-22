# [M] Crafted zones can cause increased resource usage

## Summary
Severity: Medium
Advisory: CVE-2026-33258
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33258
Type: osv

## Details
By publishing and querying a crafted zone an attacker can cause allocation of large entries in the negative and aggressive NSEC(3) caches.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-03.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33258.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33258
- https://github.com/PowerDNS/pdns
