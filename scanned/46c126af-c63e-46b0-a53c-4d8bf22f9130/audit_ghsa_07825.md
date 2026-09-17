# [M] ZITADEL's truncated opaque tokens are still valid

## Summary
Severity: Medium
Advisory: GHSA-6mq3-xmgp-pjm5
CVE: CVE-2026-27840
CWE: CWE-302
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-6mq3-xmgp-pjm5
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0 <4.11.0
- Go: `github.com/zitadel/zitadel` — affected >=3.0.0 <3.4.7
- Go: `github.com/zitadel/zitadel` — affected >=2.31.0
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20260216092519-feab8e1fa371

## Details
### Summary

Opaque OIDC access tokens in v2 format, truncated to 80 characters are still considered valid. 

ZITADEL uses a symmetric AES encryption for opaque tokens. The cleartext payload is a concatenation of a couple of identifiers, such as a token ID and user ID. Internally Zitadel has 2 different versions of token payloads. v1 tokens are no longer created, but are still verified as to not invalidate existing session after upgrade.

The cleartext payload has a format of `<token_id>:<user_id>`. v2 tokens distinguished further where the `token_id` is of the format `v2_<oidc_session_id>-at_<access_token_id>`. This is an example of such a cleartext: `V2_354201447279099906-at_354201447279165442:354201364702363650`

### Impact

V1 token authZ/N session data is retrieved from the database using the (simple) `token_id` value and `user_id` value. The `user_id` (called `subject` in some parts of our code) was used as being the trusted user ID.

V2 token authZ/N session data is retrieved from the database using the `oidc_session_id` and `access_token_id` and in this case the `user_id` from the token is ignored and taken from the session data in the database.

By truncating the token to 80 chars, the user_id is now missing from the cleartext of the v2 token: `V2_354201447279099906-at_354201447279165442:`  The back-end still accepts this for above reasons.

This issue is not considered exploitable, but may look awkward when reproduced.

### Affected Versions

All versions within the following ranges, including release candidates (RCs), are affected:
- **v4.x**: `4.0.0` through `4.10.1`
- **3.x**: `3.0.0` through `3.4.6`
- **2.x**: `2.31.0` through `2.71.19`

### Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by verifying the `user_id` from the token against the session data from the database

4.x: Upgrade to >=[4.11.0](https://github.com/zitadel/zitadel/releases/tag/v4.11.0)
3.x: Update to >=[3.4.7](https://github.com/zitadel/zitadel/releases/tag/v3.4.7)
2.x: Update to >=[3.4.7](https://github.com/zitadel/zitadel/releases/tag/v3.4.7)

### Workarounds

The recommended solution is to update ZITADEL to a patched version.

### Questions

If there any questions or comments about this advisory, please send an email to [security@zitadel.com](mailto:security@zitadel.com)

### Credits

ZITADEL thanks Olivier Becker and Lucas Dodgson for reporting this vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-6mq3-xmgp-pjm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27840
- https://github.com/zitadel/zitadel/commit/feab8e1fa371f3ad654640fc869b2c14f2fdb602
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.71.19
- https://github.com/zitadel/zitadel/releases/tag/v3.4.7
- https://github.com/zitadel/zitadel/releases/tag/v4.11.0
