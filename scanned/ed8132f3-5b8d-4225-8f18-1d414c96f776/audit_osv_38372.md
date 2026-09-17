# [C] Genealogy is Missing Authorization in `TeamController::transferOwnership()` Allows Any Authenticated User to Hijack Any Team (Broken Access Control)

## Summary
Severity: Critical
Advisory: CVE-2026-39355
Aliases: GHSA-2rq7-jqm7-w8x4
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39355
Type: osv

## Details
Genealogy is a family tree PHP application. Prior to 5.9.1, a critical broken access control vulnerability in the genealogy application allows any authenticated user to transfer ownership of arbitrary non-personal teams to themselves. This enables complete takeover of other users’ team workspaces and unrestricted access to all genealogy data associated with the compromised team. This vulnerability is fixed in 5.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39355.json
- https://github.com/MGeurts/genealogy/security/advisories/GHSA-2rq7-jqm7-w8x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-39355
