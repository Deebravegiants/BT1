# [M] LDAP DN injection

## Summary
Severity: Medium
Advisory: CVE-2026-33609
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33609
Type: osv

## Details
Incomplete escaping of LDAP queries when running with 8bit-dns enabled allows users to perform queries of internal domain subtrees.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/authoritative/security-advisories/powerdns-advisory-powerdns-2026-05.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33609.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33609
- https://github.com/PowerDNS/pdns
