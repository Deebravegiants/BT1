# [H] TOTP enrollment hijack: password gate skipped due to unawaited promise

## Summary
Severity: High
Advisory: CVE-2026-49467
Aliases: GHSA-59q6-jvp6-w282
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-49467
Type: osv

## Details
Pingvin Share X is a secure and easy self-hosted file sharing platform. A vulnerability in versions 1.5.0 through 1.18.0 allow an attacker to bypass password verification when managing Time-based One-Time Password (TOTP) settings. The root cause is a missing `await` keyword on calls to the asynchronous `verifyPassword` method in `authTotp.service.ts` and the `authenticateUser` method in `auth.service.ts`. In JavaScript, an unawaited `Promise` is always truthy. So the logic intended to throw a `ForbiddenException` when a password is incorrect. It never executes because the expression evaluates the existence of the `Promise` object rather than its resolved boolean result. The vulnerability is fixed in version 1.18.1 by ensuring all asynchronous authentication calls are properly awaited. There are no official workarounds. If a user is locked out, an administrator must manually reset the user's TOTP status in the database.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49467.json
- https://github.com/smp46/pingvin-share-x/security/advisories/GHSA-59q6-jvp6-w282
- https://nvd.nist.gov/vuln/detail/CVE-2026-49467
