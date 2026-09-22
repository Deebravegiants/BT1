# [H] Homarr: missing input sanitization and possible privilege escalation through ldap search query injection

## Summary
Severity: High
Advisory: CVE-2025-67493
Aliases: GHSA-59gp-q3xx-489q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:L)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-67493
Type: osv

## Details
Homarr is an open-source dashboard. Prior to version 1.45.3, it was possible to craft an input which allowed privilege escalation and getting access to groups of other users due to missing sanitization of inputs in ldap search query. The vulnerability could impact all instances using ldap authentication where a malicious actor had access to a user account. Version 1.45.3 has a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67493.json
- https://github.com/homarr-labs/homarr/security/advisories/GHSA-59gp-q3xx-489q
- https://nvd.nist.gov/vuln/detail/CVE-2025-67493
