# [H] CVAT vulnerable to privilege escalation of users with staff status

## Summary
Severity: High
Advisory: CVE-2026-23526
Aliases: GHSA-7pvv-w55f-qmw7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2026-23526
Type: osv

## Details
CVAT is an open source interactive video and image annotation tool for computer vision. In versions 1.0.0 through 2.54.0, users that have the staff status may freely change their permissions, including giving themselves superuser status and joining the admin group, which gives them full access to the data in the CVAT instance. Version 2.55.0 fixes the issue. As a workaround, review the list of users with staff status and revoke it from any users that are not expected to have superuser privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23526.json
- https://github.com/cvat-ai/cvat/security/advisories/GHSA-7pvv-w55f-qmw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-23526
- https://github.com/cvat-ai/cvat/commit/88ac7aa4d5b52271a30f1aa387c0f5745f8f77d4
