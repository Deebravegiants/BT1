# [M] SiYuan before v3.8.2 Denial of Service via Auth Throttle

## Summary
Severity: Medium
Advisory: CVE-2026-85584
Aliases: GHSA-2x7j-p79w-7744
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85584
Type: osv

## Details
SiYuan versions before v3.8.2 contain a denial of service vulnerability in the publish-service Basic Auth throttle that stores failed-attempt state using attacker-controlled usernames without enforcing capacity limits or eviction policies. Unauthenticated attackers can submit repeated authentication requests with unique invalid usernames to exhaust memory and increase synchronization overhead, degrading service availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85584.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-2x7j-p79w-7744
- https://nvd.nist.gov/vuln/detail/CVE-2026-85584
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-denial-of-service-via-auth-throttle
