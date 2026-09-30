# [H] TypeBot: Account takeover via brute-forceable 6-digit magic-link code

## Summary
Severity: High
Advisory: CVE-2026-62862
Aliases: GHSA-4g76-cwmg-gqgw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-62862
Type: osv

## Details
Typebot is an open-source chatbot builder. In self-hosted versions up to and including 3.17.1, the default passwordless email magic-link authentication is vulnerable to login-code brute forcing that leads to account takeover. The email provider overrides NextAuth's default cryptographically secure token with a 6-digit code generated using Math.random(), reducing the keyspace to 900,000 with a 10-minute expiry, and the code itself is the raw value placed in the magic link. The verification callback enforces no attempt limit, lockout, or CSRF protection, and an incorrect guess does not consume the real code because the adapter returns null on a not-found token, so a valid code survives unlimited guessing within its lifetime. The only rate limiter applies to the code-sending path and is keyed on the client-controlled X-Forwarded-For header, allowing an attacker to request many concurrent live codes for one victim and further raise the odds of a matching guess. As a result, an anonymous attacker who knows a victim's email address can brute-force the callback and obtain an authenticated session as that user with no victim interaction, gaining full access to the victim's bots, results, and connected integration credentials. Deployments configured for OAuth or SSO only, with no email provider, are not affected. This issue is fixed in version 3.18.0

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.18.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62862.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-4g76-cwmg-gqgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-62862
- https://github.com/baptisteArno/typebot.io/commit/03c8dd967f21e48e128340e369901d595d89bfd9
