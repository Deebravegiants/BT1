# [H] Better Auth Passkey Plugin allows passkey deletion through IDOR

## Summary
Severity: High
Advisory: GHSA-4vcf-q4xf-f48m
CWE: CWE-284, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-4vcf-q4xf-f48m
Type: github-advisory

## Affected
- npm: `@better-auth/passkey` — affected >=0 <1.4.0

## Details
# Summary

Affected versions of the better-auth passkey plugin allow users with any valid session to delete arbitrary passkeys via their ID using `POST /passkey/delete-passkey`.

# Details

`ctx.body.id` is implicitly trusted and used in passkey deletion queries.

better-auth applications configured with `useNumberId` may use auto incrementing IDs which makes it trivial to delete all passkeys via enumeration.

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-4vcf-q4xf-f48m
- https://github.com/better-auth/better-auth/commit/06d68239e
- https://github.com/better-auth/better-auth
