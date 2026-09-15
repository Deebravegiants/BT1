# [H] Monkeytype: Rate-limit and anti-brute-force controls bypassable via spoofed HTTP headers (forgotPasswordEmail/verificationEmail mail bombing and badAuth bypass)

## Summary
Severity: High
Advisory: CVE-2026-69183
Aliases: GHSA-c878-p3jh-mmjf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-69183
Type: osv

## Details
Monkeytype is a minimalistic and customizable typing test. In 26.26.0 and earlier, the backend rate-limit key generator in backend/src/middlewares/rate-limit.ts uses client-controlled cf-connecting-ip and x-forwarded-for headers before the trust-proxy-derived req.ip value. An unauthenticated attacker can rotate either header to create a new bucket for each request, bypassing rootRateLimiter, badAuthRateLimiter, getKey(), and the getKeyWithUid() fallback used by public endpoints. This permits repeated POST /users/forgotPasswordEmail and verificationEmail requests, mail bombing registered users, consuming Firebase or SMTP quota, evading brute-force protection, and enabling resource exhaustion. Exploitability of cf-connecting-ip depends on deployment topology, but x-forwarded-for and direct-to-origin paths remain affected when those values are not overwritten by a trusted proxy. No fixed version is available as of this review.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69183.json
- https://github.com/monkeytypegame/monkeytype/security/advisories/GHSA-c878-p3jh-mmjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-69183
