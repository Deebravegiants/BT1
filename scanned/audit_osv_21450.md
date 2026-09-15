# [M] CVE-2021-4314

## Summary
Severity: Medium
Advisory: CVE-2021-4314
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-01-18
Source: https://osv.dev/vulnerability/CVE-2021-4314
Type: osv

## Details
It is possible to manipulate the JWT token without the knowledge of the JWT secret and authenticate without valid JWT token as any user. This is happening only in the situation when zOSMF doesn’t have the APAR PH12143 applied. This issue affects: 1.16 versions to 1.19. What happens is that the services using the ZAAS client or the API ML API to query will be deceived into believing the information in the JWT token is valid when it isn’t. It’s possible to use this to persuade the southbound service that different user is authenticated.

## References
- https://github.com/zowe/api-layer/
