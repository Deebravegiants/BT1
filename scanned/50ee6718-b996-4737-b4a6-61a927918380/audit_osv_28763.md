# [H] Kanboard affected by Project Takeover via IDOR in ProjectPermissionController

## Summary
Severity: High
Advisory: CVE-2024-36399
Aliases: GHSA-x8v7-3ghx-65cv
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-36399
Type: osv

## Details
Kanboard is project management software that focuses on the Kanban methodology. The vuln is in app/Controller/ProjectPermissionController.php function addUser(). The users permission to add users to a project only get checked on the URL parameter project_id. If the user is authorized to add users to this project the request gets processed. The users permission for the POST BODY parameter project_id does not get checked again while processing. An attacker with the 'Project Manager' on a single project may take over any other project. The vulnerability is fixed in 1.2.37.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36399.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-x8v7-3ghx-65cv
- https://nvd.nist.gov/vuln/detail/CVE-2024-36399
- https://github.com/kanboard/kanboard/commit/b6703688aac8187f5ea4d4d704fc7afeeffeafa7
