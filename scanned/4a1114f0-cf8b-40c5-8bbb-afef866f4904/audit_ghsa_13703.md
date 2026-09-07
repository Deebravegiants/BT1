# [M] Possible user mocking that bypasses basic authentication

## Summary
Severity: Medium
Advisory: GHSA-v64w-49xw-qq89
CVE: CVE-2023-48309
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-v64w-49xw-qq89
Type: github-advisory

## Affected
- npm: `next-auth` — affected >=0 <4.24.5

## Details
### Impact

`next-auth` applications prior to version **4.24.5** that rely on the default [Middleware authorization](https://next-auth.js.org/configuration/nextjs#middleware) are affected.

A bad actor could create an empty/mock user, by getting hold of a NextAuth.js-issued JWT from an interrupted OAuth sign-in flow (state, PKCE or nonce).

Manually overriding the `next-auth.session-token` cookie value with this non-related JWT would let the user simulate a logged in user, albeit having no user information associated with it. (The only property on this user is an opaque randomly generated string).

This vulnerability does **not** give access to other users' data, neither to resources that require proper authorization via scopes or other means. The created mock user has no information associated with it (ie. no name, email, access_token, etc.)

This vulnerability can be exploited by bad actors to peek at logged in user states (e.g. dashboard layout).

_Note: Regardless of the vulnerability, the existence of a NextAuth.js session state can provide simple authentication, but not authorization in your applications. For role-based access control, you can check out [our guide](https://authjs.dev/guides/basics/role-based-access-control)._

### Patches

We patched the vulnerability in `next-auth` `v4.24.5`. To upgrade, run one of the following:

```
npm i next-auth@latest
```
```
yarn add next-auth@latest
```
```
pnpm add next-auth@latest
```

### Workarounds

Upgrading to `latest` is the recommended way to fix this issue. However, using [a custom authorization callback for Middleware](https://next-auth.js.org/configuration/nextjs#advanced-usage), developers can manually do a basic authentication:

```ts
// middleware.ts
import { withAuth } from "next-auth/middleware"

export default withAuth(/*your middleware function*/, {
  // checking the existence of any property - besides `value` which might be a random string - on the `token` object is sufficient to prevent this vulnerability
  callbacks: { authorized: ({ token }) => !!token?.email }
})
```

### References

- [NextAuth.js Middleware](https://next-auth.js.org/configuration/nextjs#middleware)
- [Role-based access contorl (RBAC) guide](https://authjs.dev/guides/basics/role-based-access-control)

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-v64w-49xw-qq89
- https://nvd.nist.gov/vuln/detail/CVE-2023-48309
- https://github.com/nextauthjs/next-auth/commit/d237059b6d0cb868c041ba18b698e0cee20a2f10
- https://authjs.dev/guides/basics/role-based-access-control
- https://github.com/nextauthjs/next-auth
- https://next-auth.js.org/configuration/nextjs#advanced-usage
- https://next-auth.js.org/configuration/nextjs#middlewar
