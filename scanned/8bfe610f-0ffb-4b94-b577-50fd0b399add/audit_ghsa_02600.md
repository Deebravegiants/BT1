# [M] matrix-js-sdk can be tricked into disclosing E2EE room keys to a participating homeserver

## Summary
Severity: Medium
Advisory: GHSA-23cm-x6j7-6hq3
CVE: CVE-2021-40823
CWE: CWE-200, CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-14
Source: https://github.com/advisories/GHSA-23cm-x6j7-6hq3
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <12.4.1

## Details
### Impact

A logic error in the room key sharing functionality of matrix-js-sdk before 12.4.1 allows a malicious Matrix homeserver† participating in an encrypted room to steal room encryption keys from affected Matrix clients participating in that room. This allows the homeserver to decrypt end-to-end encrypted messages sent by affected clients.

† Or anyone with access to the account of the original recipient of an encrypted message.

Known clients affected (via their use of vulnerable versions of matrix-js-sdk):

- Element Web (1.8.2 and earlier)
- Element Desktop (1.8.2 and earlier)
- SchildiChat Web (1.7.32-sc1 and earlier)
- SchildiChat Desktop (1.7.32-sc1 and earlier)
- Cinny (1.2.0 and earlier)

### Patch

This was fixed in https://github.com/matrix-org/matrix-js-sdk/commit/894c24880da0e1cc81818f51c0db80e3c9fb2be9.

### Workarounds
To prevent a homeserver from being able to steal the room keys, vulnerable clients can be taken offline or signed out. If signing out, care should be taken to either set up Secure Backup or export E2E room keys in order to preserve access to past messages.

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-23cm-x6j7-6hq3
- https://nvd.nist.gov/vuln/detail/CVE-2021-40823
- https://github.com/matrix-org/matrix-js-sdk/commit/894c24880da0e1cc81818f51c0db80e3c9fb2be9
- https://github.com/matrix-org/matrix-js-sdk
- https://github.com/matrix-org/matrix-js-sdk/releases/tag/v12.4.1
- https://matrix.org/blog/2021/09/13/vulnerability-disclosure-key-sharing
