# [M] ZONEMD validation can be bypassed

## Summary
Severity: Medium
Advisory: CVE-2026-42390
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-42390
Type: osv

## Details
An invalid zone might pass ZONEMD validation while it should not. This is only relevant if ZoneToCache is configured with ZONEMD validation.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-08.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42390
- https://github.com/PowerDNS/pdns
