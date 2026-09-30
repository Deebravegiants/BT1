# [H] IDOR Vulnerability in transformeroptimus/superagi

## Summary
Severity: High
Advisory: CVE-2024-12048
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12048
Type: osv

## Details
An IDOR (Insecure Direct Object Reference) vulnerability exists in transformeroptimus/superagi version v0.0.14. The application fails to properly check authorization for multiple API endpoints, allowing attackers to view, edit, and delete other users' information without proper authorization. Affected endpoints include but are not limited to /get/project/{project_id}, /get/schedule_data/{agent_id}, /delete/{agent_id}, /get/organisation/{organisation_id}, and /get/user/{user_id}.

## References
- https://huntr.com/bounties/6def3e3a-c443-44bb-b20e-3e69b48f37dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12048.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12048
