# [M] Logto: TOTP code can be replayed within the RFC 6238 validity window (one-time use violation)

## Summary
Severity: Medium
Advisory: CVE-2026-55370
Aliases: GHSA-6wj7-c66m-6c82
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55370
Type: osv

## Details
Logto is the modern, open-source auth infrastructure for SaaS and AI apps. Prior to 1.41.0, Logto's existing TOTP verification accepted a successfully used TOTP code again while the code remained inside the RFC 6238 acceptance window because the verifier used otplib's stateless check with window = 1 and did not persist or compare the accepted TOTP time-step counter. An attacker who has the victim's first factor and captures a live TOTP value can replay that value to satisfy MFA during the same acceptance window. This issue is fixed in version 1.41.0.

## References
- https://github.com/logto-io/logto/releases/tag/v1.41.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55370.json
- https://github.com/logto-io/logto/security/advisories/GHSA-6wj7-c66m-6c82
- https://nvd.nist.gov/vuln/detail/CVE-2026-55370
- https://github.com/logto-io/logto/commit/9118867f6cbadc7291cf913beb4fede91ed5d374
- https://github.com/logto-io/logto/pull/9109
