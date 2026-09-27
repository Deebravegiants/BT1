# [M] CVE-2021-21310

## Summary
Severity: Medium
Advisory: CVE-2021-21310
Aliases: GHSA-pg53-56cg-4m8q
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-11
Source: https://osv.dev/vulnerability/CVE-2021-21310
Type: osv

## Details
NextAuth.js (next-auth) is am open source authentication solution for Next.js applications. In next-auth before version 3.3.0 there is a token verification vulnerability. Implementations using the Prisma database adapter in conjunction with the Email provider are impacted. Implementations using the Email provider with the default database adapter are not impacted. Implementations using the Prisma database adapter but not using the Email provider are not impacted. The Prisma database adapter was checking the verification token, but was not verifying the email address associated with that token. This made it possible to use a valid token to sign in as another user when using the Prima adapter in conjunction with the Email provider. This issue is specific to the community supported Prisma adapter. This issue is fixed in version 3.3.0.

## References
- https://github.com/nextauthjs/next-auth/releases/tag/v3.3.0
- https://www.npmjs.com/package/next-auth
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-pg53-56cg-4m8q
