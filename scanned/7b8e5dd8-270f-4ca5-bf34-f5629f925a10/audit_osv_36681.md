# [M] Budibase: Unauthenticated Password Reset Endpoint Lacks Rate Limiting, Enabling Email Flooding

## Summary
Severity: Medium
Advisory: CVE-2026-25043
Aliases: GHSA-277c-prw2-rqgh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-25043
Type: osv

## Details
Budibase is an open-source low-code platform. Prior to version 3.23.25, a business logic vulnerability exists in Budibase’s password reset functionality due to the absence of rate limiting, CAPTCHA, or abuse prevention mechanisms on the “Forgot Password” endpoint. An unauthenticated attacker can repeatedly trigger password reset requests for the same email address, resulting in hundreds of password reset emails being sent in a short time window. This enables large-scale email flooding, user harassment, denial of service (DoS) against user inboxes, and potential financial and reputational impact for Budibase. This issue has been patched in version 3.23.25.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-277c-prw2-rqgh
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25043.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25043
- https://github.com/Budibase/budibase/commit/21bc3f812b2312f082f7683c2abc22d1ecc880c7
