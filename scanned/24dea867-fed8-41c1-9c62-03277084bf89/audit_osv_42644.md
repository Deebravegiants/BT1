# [M] Admidio before 5.0.11 Cross-Organization Role Modification

## Summary
Severity: Medium
Advisory: CVE-2026-69090
Aliases: GHSA-fcq9-w4hp-xchg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69090
Type: osv

## Details
Admidio before 5.0.11 fails to validate target organization membership in role handlers, allowing authenticated role administrators to delete, activate, deactivate, or edit roles belonging to other organizations. Attackers can supply a role UUID from another organization to groups_roles.php handlers to modify that organization's roles without authorization.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-fcq9-w4hp-xchg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69090.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69090
- https://www.vulncheck.com/advisories/admidio-before-cross-organization-role-modification
