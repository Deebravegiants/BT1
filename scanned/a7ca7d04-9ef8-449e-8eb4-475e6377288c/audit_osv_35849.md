# [H] IdP-initiated SAML sessions not reliably invalidated (replay)

## Summary
Severity: High
Advisory: CVE-2026-15614
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-15614
Type: osv

## Details
Logto silently fails to delete IdP-initiated SAML sessions, enabling session replay and reuse within the session’s validity window.

## References
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/libraries/verification-helpers/single-sign-on.ts#L81-L99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15614.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15614
