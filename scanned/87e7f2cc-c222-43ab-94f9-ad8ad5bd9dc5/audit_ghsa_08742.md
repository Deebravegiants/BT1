# [M] Concrete CMS is vulnerable to unauthenticated file usage disclosure

## Summary
Severity: Medium
Advisory: GHSA-4g7q-44qp-cc5c
CVE: CVE-2026-6826
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-4g7q-44qp-cc5c
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below  is vulnerable to unauthenticated file usage disclosure via missing permission check in the usage controller.  Any unauthenticated visitor can request /ccm/system/dialogs/file/usage/{fID} with any file ID and receive a list of every page that references that file, including page IDs, handles, and full URLs. This includes pages that are otherwise restricted by permissions. Concrete CMS thanks Eldudareeno for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6826
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
