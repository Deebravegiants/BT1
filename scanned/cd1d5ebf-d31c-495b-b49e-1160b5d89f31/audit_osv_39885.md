# [H] OpenReception doesn't rate limit passphrase login attempts

## Summary
Severity: High
Advisory: CVE-2026-48084
Aliases: GHSA-hhg5-xmjg-3m93
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48084
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Versions prior to 1.0.2 don't throttle failed passphrase login attempts. An attacker can submit unlimited wrong passphrase guesses against any known email address, capped only by the Argon2 verification cost (about 100 milliseconds per attempt on the tested host, giving 10 attempts per second sustained). The same backend implements a working per-account throttle on the WebAuthn challenge endpoint, which returns HTTP 429 after roughly 19 attempts. The passphrase branch simply does not invoke that throttle, leaving a supported high-value login path unprotected against credential stuffing and dictionary attacks. The asymmetry confirms this is an oversight rather than a design choice. The throttle infrastructure exists, is wired into the same auth backend, and works on the WebAuthn path. The passphrase branch in `/api/auth/login` was not updated to record failed attempts. Combined with the application's minimum-passphrase policy (12 characters, no entropy or dictionary checks), accounts using common base patterns such as `Spring2026!XX` or words from a leak corpus are realistically reachable in days on a single CPU, hours on a small GPU farm. Version 1.0.2 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48084.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-hhg5-xmjg-3m93
- https://nvd.nist.gov/vuln/detail/CVE-2026-48084
- https://github.com/open-reception/appointment-booking-software/commit/b283dbb670e09112299fb0cf89f3cb054ecc1700
