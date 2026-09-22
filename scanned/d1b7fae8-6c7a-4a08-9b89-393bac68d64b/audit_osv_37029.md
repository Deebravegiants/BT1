# [M] Use after free when parsing EDNS options in Lua

## Summary
Severity: Medium
Advisory: CVE-2026-27854
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-27854
Type: osv

## Details
An attacker might be able to trigger a use-after-free by sending crafted DNS queries to a DNSdist using the DNSQuestion:getEDNSOptions method in custom Lua code. In some cases DNSQuestion:getEDNSOptions might refer to a version of the DNS packet that has been modified, thus triggering a use-after-free and potentially a crash resulting in denial of service.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27854.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27854
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-02.html
- https://github.com/PowerDNS/pdns
