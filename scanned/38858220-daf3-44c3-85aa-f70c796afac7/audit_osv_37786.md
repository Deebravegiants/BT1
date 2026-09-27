# [M] Insufficient validation of cookie reply

## Summary
Severity: Medium
Advisory: CVE-2026-33262
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33262
Type: osv

## Details
An attacker can send replies that result in a null pointer dereference, caused by a missing consistency check and leading to a denial of service. Cookies are disabled by default.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-03.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33262
- https://github.com/PowerDNS/pdns
