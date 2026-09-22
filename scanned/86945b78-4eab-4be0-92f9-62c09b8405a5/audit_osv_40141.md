# [C] Mass Assignment via Onboarding Endpoint Allows Unauthenticated JWT_SECRET Overwrite

## Summary
Severity: Critical
Advisory: CVE-2026-50160
Aliases: GHSA-j542-4rch-8hwf
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-50160
Type: osv

## Details
Hoppscotch is an API development ecosystem. In self-hosted deployments of hoppscotch-backend from version 2026.4.1 and earlier, the unauthenticated POST /v1/onboarding/config endpoint is vulnerable to mass assignment. The global NestJS ValidationPipe is configured without whitelist: true, so extra properties on the request body that are not declared in SaveOnboardingConfigRequest are not stripped and are iterated in the service layer as if they were legitimate InfraConfig entries. Because keys such as JWT_SECRET and SESSION_SECRET are valid InfraConfigEnum values and are not explicitly rejected during validation, an unauthenticated attacker who can reach a fresh instance before onboarding completes (or when no users exist) can overwrite these values in the database. Overwriting JWT_SECRET gives the attacker control of the JWT signing key, allowing them to forge tokens for any user, including administrators, and results in full server compromise. The issue is fixed in hoppscotch 2026.5.0.

## References
- http://www.openwall.com/lists/oss-security/2026/06/23/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50160.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-j542-4rch-8hwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-50160
- https://github.com/hoppscotch/hoppscotch/pull/6171
