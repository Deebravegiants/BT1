# [H] CVE-2023-32749

## Summary
Severity: High
Advisory: CVE-2023-32749
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-32749
Type: osv

## Details
Pydio Cells allows users by default to create so-called external users in order to share files with them. By modifying the HTTP request sent when creating such an external user, it is possible to assign the new user arbitrary roles. By assigning all roles to a newly created user, access to all cells and non-personal workspaces is granted.

## References
- http://packetstormsecurity.com/files/172645/Pydio-Cells-4.1.2-Privilege-Escalation.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32749.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32749
- https://www.redteam-pentesting.de/en/advisories/-advisories-publicised-vulnerability-analyses
- https://www.redteam-pentesting.de/en/advisories/rt-sa-2023-003/-pydio-cells-unauthorised-role-assignments
- http://seclists.org/fulldisclosure/2023/May/18
