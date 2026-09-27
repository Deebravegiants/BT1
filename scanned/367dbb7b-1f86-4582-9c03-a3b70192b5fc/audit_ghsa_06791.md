# [H] ZITADEL Users Can Self-Verify Email/Phone via API

## Summary
Severity: High
Advisory: GHSA-jq8w-8q2f-ffm9
CVE: CVE-2026-54693
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-jq8w-8q2f-ffm9
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0
- Go: `github.com/zitadel/zitadel` — affected >=2.43.0
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20260608144108-ed09b3df7f43

## Details
### Summary

A vulnerability in Zitadel's self-management capability allowed users to mark their email and phone as verified without going through an actual verification process.

While [`GHSA-282g-fhmx-xf54`](https://github.com/zitadel/zitadel/security/advisories/GHSA-282g-fhmx-xf54) (CVE-2026-27946, "Users Can Self-Verify Email/Phone via UpdateHumanUser API") closed the path that let any authenticated user mark an arbitrary email or phone as verified on their own account by calling `UpdateHumanUser` with `email.is_verified: true`, additional paths were discovered.

### Impact 

Zitadel provides an API for managing users. The API also allows users to self-manage their own data including updating the email and phone.

Due to an improper permission check, the API allowed returning the verification code for the email and phone to the own user.
This allows users to claim ownership of an email or phone they do not control and potentially bypass email-based security policies.

Note that when changing another user's email or phone, regardless of the verification flag, the permissions were correctly checked.

### Affected Versions

Systems running one of the following versions are affected:
- **4.x**: `4.0.0` through `4.15.0` (including RC versions)
- **3.x**: `3.0.0` through `3.4.10` (including RC versions)
- **2.x**: `2.43.0` through `2.71.19`

### Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by requiring the correct permission in case the verification flag is provided and only allows self-management of the email address, resp. phone number itself.

4.x: Upgrade to >=[4.15.1](https://github.com/zitadel/zitadel/releases/tag/v4.15.1)
3.x: Update to >=[3.4.11](https://github.com/zitadel/zitadel/releases/tag/v3.4.11)
2.x: Update to >=[3.4.11](https://github.com/zitadel/zitadel/releases/tag/v3.4.11)

### Workarounds

The recommended solution is to upgrade to a patched version. If an upgrade is not possible, an action (v2) could be used to prevent returning the verification code to the own user.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)


### Credits

Thanks to [eddieran](https://github.com/eddieran) for reporting this vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-jq8w-8q2f-ffm9
- https://github.com/zitadel/zitadel/commit/90f310212d3a5075084a603bf61fed549c92956d
- https://github.com/zitadel/zitadel/commit/a1748b2f0326ddf7be0de44b4f980ae2c07c0151
- https://github.com/zitadel/zitadel/commit/ed09b3df7f43e870423e4d8f2757e6894481604f
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v3.4.11
- https://github.com/zitadel/zitadel/releases/tag/v4.15.1
