# [M] Concurrent modification of RPZ data can lead to denial of servce

## Summary
Severity: Medium
Advisory: CVE-2026-33259
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33259
Type: osv

## Details
Having many concurrent transfers of the same RPZ can lead to inconsistent RPZ data, use after free and/or a crash of the recursor. Normally concurrent transfers of the same RPZ zone can only occur with a malfunctioning RPZ provider.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-03.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33259.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33259
- https://github.com/PowerDNS/pdns
