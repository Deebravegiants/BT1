# [M] Weblate: Restricted-component change history leaked to non-member project users through the nested `GET /api/projects/{slug}/changes/` endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-62249
Aliases: GHSA-92m8-wv36-prmx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-62249
Type: osv

## Details
Weblate is a web-based continuous localization platform used to manage software translations. In versions prior to 2026.7, an authenticated user with access to a project can retrieve the change history of restricted components in that project through nested API change endpoints, even without permission to view those components directly. The nested endpoints do not apply the component-level access checks enforced on the direct component views, so the requester can enumerate changes for components that should be hidden from them. The exposed data can include the restricted component's identity, translation and unit links, and change payload fields such as source or translated string content in the target, old, and details values. This issue is fixed in version 2026.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62249.json
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-92m8-wv36-prmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-62249
- https://github.com/WeblateOrg/weblate/commit/a27b02110ab33995bce8cf9ea0eeddf72aa334ca
