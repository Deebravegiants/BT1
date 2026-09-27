# [M] Spoofed answers can mark an authoritative non-EDNS capable

## Summary
Severity: Medium
Advisory: CVE-2026-52690
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-52690
Type: osv

## Details
Spoofing replies to Recursor might mark an IP of an authoritative server as not supporting EDNS, causing valdiation of DNSSEC records served by that server to fail.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-08.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52690.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52690
- https://github.com/PowerDNS/pdns
