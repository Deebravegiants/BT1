# [H] Weblate path traversal allows a project administrator to read arbitrary files via App store metadata download (Incomplete Fix of CVE-2026-34242)

## Summary
Severity: High
Advisory: CVE-2026-61792
Aliases: GHSA-xwj4-fp82-r2rj
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-61792
Type: osv

## Details
Weblate is a web-based continuous localization platform used to manage software translations. In versions prior to 2026.7, a project administrator can read files outside their repository through the App store metadata download feature, which resolves attacker-influenced paths without adequately confining them to the repository. This is an incomplete fix for CVE-2026-34242, whose original patch failed to fully prevent the path traversal, allowing the arbitrary file read to persist. A user with project-administrator privileges can therefore disclose the contents of files on the Weblate host that lie outside the project's repository. This issue is fixed in version 2026.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61792.json
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-xwj4-fp82-r2rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-61792
- https://github.com/WeblateOrg/weblate/commit/299fb28315674ae3fb010e96031951cacfe367db
- https://github.com/WeblateOrg/weblate/commit/33a9acb5ad223a927a56ffd741bbddf28a54a5e3
