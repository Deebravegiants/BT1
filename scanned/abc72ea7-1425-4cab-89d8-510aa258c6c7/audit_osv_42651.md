# [C] MaxKey Hard-coded JWT Secret Unauthorized Access via /login/jwt/trust

## Summary
Severity: Critical
Advisory: CVE-2026-69102
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-69102
Type: osv

## Details
MaxKey contains an unauthorized access vulnerability due to a hard-coded JWT signing secret in application-maxkey.properties that allows unauthenticated attackers to forge valid JWT tokens and authenticate as any user by exploiting the password-skipped login endpoint. Attackers can craft a JWT token signed with the publicly known default secret, submit it to the /sign/login/jwt/trust endpoint, and obtain a fully authenticated admin session with access to SSO application configuration and downstream application secrets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69102.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69102
- https://www.vulncheck.com/advisories/maxkey-hard-coded-jwt-secret-unauthorized-access-via-login-jwt-trust
- https://github.com/dromara/MaxKey/issues/270
- https://github.com/dromara/MaxKey/commit/6cda394ec111f03a06fb2eed0de74f787d68bd97
- https://github.com/dromara/MaxKey
