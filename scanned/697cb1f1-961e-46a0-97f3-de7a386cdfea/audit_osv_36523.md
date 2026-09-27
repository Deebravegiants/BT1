# [M] Out-of-bounds read when parsing DNS packets via Lua

## Summary
Severity: Medium
Advisory: CVE-2026-24028
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-24028
Type: osv

## Details
An attacker might be able to trigger an out-of-bounds read by sending a crafted DNS response packet, when custom Lua code uses newDNSPacketOverlay to parse DNS packets. The out-of-bounds read might trigger a crash, leading to a denial of service, or access unrelated memory, leading to potential information disclosure.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24028.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24028
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-02.html
- https://github.com/PowerDNS/pdns
