# [M] Missing Authorization in Concrete CMS 9.2.0 to 9.5.2  REST API Groups List Endpoint Allows Authenticated Users to Enumerate All Groups

## Summary
Severity: Medium
Advisory: CVE-2026-81908
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-81908
Type: osv

## Details
Concrete CMS 9.2.0 to 9.5.2 contain a missing authorization vulnerability in the REST API Groups list endpoint. The listGroups() method in concrete/src/Api/Controller/Groups.php registers a permissions checker callback that unconditionally returns true, so no per-object (tree node) authorization is enforced when the group collection is returned. An authenticated user whose API token carries the groups:read scope can call GET /ccm/api/1.0/groups and receive every group on the site regardless of the view permissions on those groups, disclosing the organization's group structure, roles, and access hierarchy. The Concrete CMS security team gave this vulnerability a CVSS v4.0 score of 6.0 with vector CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N. Thanks Winston Crooker for reporting.

## References
- https://documentation.concretecms.org/developers/introduction/version-history/953-release-notes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81908.json
- https://github.com/concretecms/concretecms
- https://nvd.nist.gov/vuln/detail/CVE-2026-81908
