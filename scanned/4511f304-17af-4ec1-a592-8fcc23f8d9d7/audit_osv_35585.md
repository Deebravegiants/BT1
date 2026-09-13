# [M] CVE-2026-10700

## Summary
Severity: Medium
Advisory: CVE-2026-10700
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-10700
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.8.4 contains multiple broken access control vulnerabilities in its file handling API that allow unauthorized access to user files.The /api/v1/files/images/{flow_id}/{file_name} endpoint does not enforce authentication or authorization checks, allowing unauthenticated remote attackers to retrieve image files associated with any flow by specifying a valid flow_id and file_name.Additionally, the /api/v1/files/download/{flow_id}/{file_name} endpoint requires authentication but fails to properly validate ownership of the requested resource. As a result, an authenticated user can access files belonging to other users by supplying arbitrary identifiers, leading to an authorization bypass (IDOR).Successful exploitation may result in unauthorized disclosure of sensitive data, including files stored in private flows. This issue breaks tenant isolation in multi-user deployments.

## References
- https://www.ibm.com/support/pages/node/7279675
