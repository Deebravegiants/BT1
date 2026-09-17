# [M] DNS over HTTPS ACL bypass

## Summary
Severity: Medium
Advisory: CVE-2026-24029
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-24029
Type: osv

## Details
When the early_acl_drop (earlyACLDrop in Lua) option is disabled (default is enabled) on a DNS over HTTPs frontend using the nghttp2 provider, the ACL check is skipped, allowing all clients to send DoH queries regardless of the configured ACL.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24029.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24029
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-02.html
- https://github.com/PowerDNS/pdns
