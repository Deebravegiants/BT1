# [H] Logto: Account Center MFA management step-up bypass via WebAuthn registration verification

## Summary
Severity: High
Advisory: CVE-2026-55377
Aliases: GHSA-q4h3-38gc-4p4j
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55377
Type: osv

## Details
Logto is the modern, open-source auth infrastructure for SaaS and AI apps. Prior to 1.41.0, Logto's Account Center step-up check accepted any active verification record that belonged to the current user and had isVerified === true. A WebAuthn registration verification record for binding a new passkey could be created and verified with only an existing Account API bearer token, then sent in the logto-verification-id header and treated as identityVerified=true by Account Center routes, allowing MFA factor management without proving possession of an existing password, identifier, or MFA factor. This issue is fixed in version 1.41.0.

## References
- https://github.com/logto-io/logto/releases/tag/v1.41.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55377.json
- https://github.com/logto-io/logto/security/advisories/GHSA-q4h3-38gc-4p4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-55377
- https://github.com/logto-io/logto/commit/f56255a7edf3b22b0ec2fdb814814ce6b0123b74
- https://github.com/logto-io/logto/pull/9110
