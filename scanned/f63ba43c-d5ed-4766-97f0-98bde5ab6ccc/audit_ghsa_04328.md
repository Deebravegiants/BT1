# [H] LimeSurvey constructs account password-reset links from the client-supplied HTTP Host header without validating it.

## Summary
Severity: High
Advisory: GHSA-5c37-5j7w-8mh8
CVE: CVE-2026-50635
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-5c37-5j7w-8mh8
Type: github-advisory

## Affected
- Packagist: `limesurvey/limesurvey` — affected >=0

## Details
LimeSurvey constructs account password-reset links from the client-supplied HTTP Host header without validating it. The optional allowedHosts allowlist that would constrain this is undefined in the default (and documented) configuration, so LSHttpRequest::checkIsAllowedHost() results in no operation. A remote, unauthenticated attacker who submits a forgotten-password request for a known account (requiring only the target's username and email) with a spoofed Host header causes LimeSurvey to email that account a reset link whose hostname is attacker-controlled while embedding the genuine validation_key. When the recipient or an automated inbound mail-security link scanner dereferences the link, the valid reset token is disclosed to the attacker, who replays it against the legitimate host's newPassword endpoint to set a new password and take over the account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50635
- https://github.com/LimeSurvey/LimeSurvey/pull/5032
- https://github.com/LimeSurvey/LimeSurvey/commit/ac2a4f1673de7b56e7a342c338f36e8bb077d4b3
- https://github.com/LimeSurvey/LimeSurvey/commit/b394cb64328aa6db95e3304f82c8c9e603e9ceb0
- https://github.com/LimeSurvey/LimeSurvey
- https://www.limesurvey.org
- https://www.vulncheck.com/advisories/limesurvey-password-reset-host-header-injection-discloses-reset-token
