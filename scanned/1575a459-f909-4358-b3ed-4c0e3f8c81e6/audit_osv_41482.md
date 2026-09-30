# [M] PasswordPusher < 2.9.2 Passphrase Brute-Force via Unthrottled Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-61458
Aliases: GHSA-59w3-h5v2-c4xw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-61458
Type: osv

## Details
PasswordPusher before 2.9.2 contains a brute-force vulnerability in the POST /p/:token/access endpoint that lacks route-specific rate limiting and per-push lockout mechanisms. Attackers who know a push token can systematically guess passphrases at 120 attempts per minute without triggering any push-level defense, making short or dictionary-derived passphrases practically recoverable within hours or days.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61458.json
- https://github.com/pglombardo/PasswordPusher/security/advisories/GHSA-59w3-h5v2-c4xw
- https://nvd.nist.gov/vuln/detail/CVE-2026-61458
- https://www.vulncheck.com/advisories/passwordpusher-passphrase-brute-force-via-unthrottled-endpoint
- https://github.com/pglombardo/PasswordPusher
