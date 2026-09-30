# [H] Logto: ReDoS via unescaped user input in email subaddressing regex (blockSubaddressing)

## Summary
Severity: High
Advisory: CVE-2026-62317
Aliases: GHSA-qp7j-c3q2-g739
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-62317
Type: osv

## Details
Logto is the modern, open-source auth infrastructure for SaaS and AI apps. Prior to 1.41.0, Logto's email subaddressing blocklist in packages/core/src/libraries/sign-in-experience/email-blocklist-policy.ts used the attacker-controlled domain from email input to construct subaddressingRegex when blockSubaddressing was enabled. The permissive emailRegEx accepted multiple at signs and regular expression metacharacters, and POST /api/experience/verification/verification-code could therefore cause catastrophic backtracking in subaddressingRegex.test(email). The resulting event-loop stall could make authentication, token issuance, SSO, and the administrative console unavailable. This issue is fixed in version 1.41.0.

## References
- https://github.com/logto-io/logto/releases/tag/v1.41.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62317.json
- https://github.com/logto-io/logto/security/advisories/GHSA-qp7j-c3q2-g739
- https://nvd.nist.gov/vuln/detail/CVE-2026-62317
- https://github.com/logto-io/logto/commit/021381237511bc0d42f81d65df8b036b01f40547
- https://github.com/logto-io/logto/pull/9106
