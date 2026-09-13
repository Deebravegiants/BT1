# [M] Bytebase allows low-privilege users to view admin projects

## Summary
Severity: Medium
Advisory: GHSA-9mmc-27gw-w6mq
CVE: CVE-2022-32170
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-9mmc-27gw-w6mq
Type: github-advisory

## Affected
- Go: `github.com/bytebase/bytebase` — affected >=0.1.0

## Details
### Overview
The "Bytebase" application does not restrict low privilege user from accessing admin projects

### Details
The "Bytebase" application does not restrict low privilege user from accessing admin projects for which an unauthorized user can view the "projects" created by "Admin". The affected endpoint is `/api/project?user=${userId}`.

### PoC
1. Log in to the application as both "Admin" (`admin@example.com:admin`) and Developer "User" (`user@admin.com:user`) and then click on "Projects".
2. Now open "Burp suite" and turn "Intercept on" and from "admin" dashboard click on "projects" and see the "user id" of "admin" in the capture request.
3. Note the "user id" and "Forward" the request and again capture the request of "projects" from the "user" dashboard and change "user id" to "admin user id" and "Forward" the request.
4. Now "user" can see the "projects" created by "admin".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32170
- https://github.com/bytebase/bytebase
- https://github.com/bytebase/bytebase/blob/1.0.4/frontend/src/store/modules/project.ts#L166-L197
- https://www.mend.io/vulnerability-database/CVE-2022-32170
