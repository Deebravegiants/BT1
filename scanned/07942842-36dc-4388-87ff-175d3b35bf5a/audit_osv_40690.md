# [M] MISP sharing group creation mass assignment allows unauthorized takeover of existing sharing groups

## Summary
Severity: Medium
Advisory: CVE-2026-54360
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-54360
Type: osv

## Details
A mass assignment vulnerability exists in MISP’s sharing group creation endpoint. When creating a new sharing group, the controller did not remove a user-supplied id field before saving the submitted data. In CakePHP, supplying a primary key in the save data can cause a create() followed by save() operation to update an existing record instead of creating a new one.

An authenticated user with permission to add sharing groups could therefore submit the identifier of an existing sharing group and modify that sharing group without passing the normal edit access-control checks. This may allow the attacker to take over or alter sharing groups they do not otherwise have access to, potentially affecting the confidentiality and integrity of information shared through those groups.

Affected component:
app/Controller/SharingGroupsController.php, add() action

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54360.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54360
- https://github.com/MISP/MISP/commit/687e7cb530ae0e2faaadf5e3e44712258fb3ef1b
- https://github.com/misp/misp
