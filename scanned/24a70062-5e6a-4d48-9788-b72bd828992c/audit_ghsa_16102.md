# [C] codechecker vulnerable to authentication bypass when using specifically crafted URLs

## Summary
Severity: Critical
Advisory: GHSA-f3f8-vx3w-hp5q
CVE: CVE-2024-10081
CWE: CWE-288
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-f3f8-vx3w-hp5q
Type: github-advisory

## Affected
- PyPI: `codechecker` — affected >=0 <6.24.2

## Details
### Summary
Authentication bypass occurs when the API URL ends with Authentication, Configuration or ServerInfo. This bypass allows superuser access to all API endpoints other than Authentication. These endpoints include the ability to add, edit, and remove products, among others.

### Details
All endpoints, apart from the /Authentication is affected by the vulnerability.

The vulnerability allows unauthenticated users to access all API functionality.
You can look for the following pattern in the logs to check if the vulnerabilty was exploited:
![image](https://github.com/user-attachments/assets/6ba02231-a3d8-4832-aee6-f96462b7441e)

Note that the url starts with v and contains a valid CodeChecker endpoint, but it ends in `Authentication`, `Configuration` or `ServerInfo` and it was made by an `Anonymous` user.

### Impact
This authentication bypass allows querying, adding, changing, and deleting Products contained on the CodeChecker server, without authentication, by an anonymous user.

## References
- https://github.com/Ericsson/codechecker/security/advisories/GHSA-f3f8-vx3w-hp5q
- https://nvd.nist.gov/vuln/detail/CVE-2024-10081
- https://github.com/Ericsson/codechecker/commit/ad41702e3108e4b92ae5d0143a5b961cc34195eb
- https://github.com/Ericsson/codechecker
- https://github.com/pypa/advisory-database/tree/main/vulns/codechecker/PYSEC-2024-238.yaml
