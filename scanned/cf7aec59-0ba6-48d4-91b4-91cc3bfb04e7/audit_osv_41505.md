# [M] FastGPT: Unauthenticated cross-tenant data access via forgeable plugin-invoke JWT (default INVOKE_TOKEN_SECRET='token')

## Summary
Severity: Medium
Advisory: CVE-2026-61684
Aliases: GHSA-w732-rq8c-chc8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61684
Type: osv

## Details
FastGPT is a knowledge-based AI application platform. In 4.15.0-beta4, FastGPT plugin invoke reverse-call endpoints under /api/invoke/* authenticate only by verifying a JWT signed with INVOKE_TOKEN_SECRET, which defaults to the constant string token and was not set in official deployment templates. An unauthenticated attacker can self-sign an HS256 JWT and reach /api/invoke/userInfo to disclose cross-tenant user PII by attacker-supplied tmbId values, or /api/invoke/fileUpload to write attacker-controlled content into chat files. This issue is fixed in version 4.15.0-beta5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.15.0-beta5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61684.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-w732-rq8c-chc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-61684
- https://github.com/labring/FastGPT/commit/f5f1e58b25571b7107ca49d9bf96bb2b0e0a620a
- https://github.com/labring/FastGPT/pull/7170
