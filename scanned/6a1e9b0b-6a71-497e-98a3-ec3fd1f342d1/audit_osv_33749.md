# [C] Conjur OSS and Secrets Manager, Self-Hosted (formerly Conjur Enterprise) Vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-49828
Aliases: GHSA-93hx-v9pv-qrm4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-49828
Type: osv

## Details
Conjur provides secrets management and application identity for infrastructure. Conjur OSS versions 1.19.5 through 1.21.1 and Secrets Manager, Self-Hosted (formerly known as Conjur Enterprise) 13.1 through 13.4.1 are vulnerable to remote code execution An authenticated attacker who can inject secrets or templates into the Secrets Manager, Self-Hosted database could take advantage of an exposed API endpoint to execute arbitrary Ruby code within the Secrets Manager process. This issue affects both Secrets Manager, Self-Hosted (formerly Conjur Enterprise) and Conjur OSS. Conjur OSS version 1.21.2 and Secrets Manager, Self-Hosted version 13.5 fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/07/16/7
- http://www.openwall.com/lists/oss-security/2025/08/08/1
- https://github.com/cyberark/conjur/releases/tag/v1.21.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49828.json
- https://github.com/cyberark/conjur/security/advisories/GHSA-93hx-v9pv-qrm4
- https://nvd.nist.gov/vuln/detail/CVE-2025-49828
