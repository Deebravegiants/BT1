# [M] Out-of-bounds write when rewriting large DNS packets

## Summary
Severity: Medium
Advisory: CVE-2026-27853
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-27853
Type: osv

## Details
An attacker might be able to trigger an out-of-bounds write by sending crafted DNS responses to a DNSdist using the DNSQuestion:changeName or DNSResponse:changeName methods in custom Lua code. In some cases the rewritten packet might become larger than the initial response and even exceed 65535 bytes, potentially leading to a crash resulting in denial of service.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27853.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27853
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-02.html
- https://github.com/PowerDNS/pdns
