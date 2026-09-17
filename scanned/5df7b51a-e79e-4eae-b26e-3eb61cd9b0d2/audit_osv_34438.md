# [C] Formbricks missing JWT signature verification

## Summary
Severity: Critical
Advisory: CVE-2025-59934
Aliases: GHSA-7229-q9pv-j6p4
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-09-26
Source: https://osv.dev/vulnerability/CVE-2025-59934
Type: osv

## Details
Formbricks is an open source qualtrics alternative. Prior to version 4.0.1, Formbricks is missing JWT signature verification. This vulnerability stems from a token validation routine that only decodes JWTs (jwt.decode) without verifying their signatures. Both the email verification token login path and the password reset server action use the same validator, which does not check the token’s signature, expiration, issuer, or audience. If an attacker learns the victim’s actual user.id, they can craft an arbitrary JWT with an alg: "none" header and use it to authenticate and reset the victim’s password. This issue has been patched in version 4.0.1.

## References
- https://github.com/formbricks/formbricks/blob/843110b0d6c37b5c0da54291616f84c91c55c4fc/apps/web/lib/jwt.ts#L114-L117
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59934.json
- https://github.com/formbricks/formbricks/security/advisories/GHSA-7229-q9pv-j6p4
- https://nvd.nist.gov/vuln/detail/CVE-2025-59934
- https://github.com/formbricks/formbricks/commit/eb1349f205189d5b2d4a95ec42245ca98cf68c82
- https://github.com/formbricks/formbricks/pull/6596
