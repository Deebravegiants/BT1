# [M] Conjur OSS and Secrets Manager, Self-Hosted (formerly Conjur Enterprise) missing validations

## Summary
Severity: Medium
Advisory: CVE-2025-49829
Aliases: GHSA-9w76-m74g-4c2r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-49829
Type: osv

## Details
Conjur provides secrets management and application identity for infrastructure. Missing validations in Secrets Manager, Self-Hosted allows authenticated attackers to inject resources into the database and to bypass permission checks. This issue affects Secrets Manager, Self-Hosted (formerly Conjur Enterprise) prior to versions 13.5.1 and 13.6.1 and Conjur OSS prior to version 1.22.1. Conjur OSS version 1.22.1 and Secrets Manager, Self-Hosted versions 13.5.1 and 13.6.1 fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/16/7
- http://www.openwall.com/lists/oss-security/2025/08/08/1
- https://github.com/cyberark/conjur/releases/tag/v1.22.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49829.json
- https://github.com/cyberark/conjur/security/advisories/GHSA-9w76-m74g-4c2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-49829
