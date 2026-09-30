# [M] Upstash Adapter missing token verification

## Summary
Severity: Medium
Advisory: GHSA-4rxr-27mm-mxq9
CVE: CVE-2022-39263
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-4rxr-27mm-mxq9
Type: github-advisory

## Affected
- npm: `@next-auth/upstash-redis-adapter` — affected >=0 <3.0.2

## Details
### Impact
Applications that use `next-auth` Email Provider and `@next-auth/upstash-redis-adapter` before v3.0.2 are affected.

### Description
The Upstash Redis adapter implementation did not check for both the identifier (email) and the token, but only checking for the identifier when verifying the token in the email callback flow. An attacker who knows about the victim's email could easily sign in as the victim, given the attacker also knows about the verification token's expired duration. 

### Patches
The vulnerability is patched in v3.0.2.
To upgrade, run one of the following:
```
npm i @next-auth/upstash-redis-adapter@latest
```
```
yarn add @next-auth/upstash-redis-adapter@latest
```
```
pnpm add @next-auth/upstash-redis-adapter@latest
```

### Workarounds
Using Advanced Initialization, developers can check the requests and compare the query's token and identifier before proceeding. Below is an example of how to do this: (Upgrading is still strongly recommended)

```js
import { createHash } from "crypto"
export default async function auth(req, res) {
  if (req.method === "POST" && req.action === "callback") {
    const token = req.query?.token
    const identifier = req.query?.email
    function hashToken(token: string) {
      const provider = authOptions.providers.find((p) => p.id === "email")
      const secret = authOptions.secret
      return (
        createHash("sha256")
          // Prefer provider specific secret, but use default secret if none specified
          .update(`${token}${provider.secret ?? secret}`)
          .digest("hex")
      )
    }
    const hashedToken = hashToken(token)

    const invite = await authOptions.adapter.useVerificationToken?.({
      identifier,
      token: hashedToken,
    })
    if (invite.token !== hashedToken) {
      res.status(400).json({ error: "Invalid token" })
    }
  }
  return await NextAuth(req, res, authOptions)
}

```
### References
EmailProvider: https://next-auth.js.org/providers/email
Advanced Initialization: https://next-auth.js.org/configuration/initialization#advanced-initialization
Upstash Redis Adapter: https://next-auth.js.org/adapters/upstash-redis

### For more information
If you have any concerns, we request responsible disclosure, outlined here: https://next-auth.js.org/security#reporting-a-vulnerability

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-4rxr-27mm-mxq9
- https://nvd.nist.gov/vuln/detail/CVE-2022-39263
- https://github.com/nextauthjs/next-auth/commit/d16e04848ee703cf797724194d4ad2907fe125a9
- https://github.com/nextauthjs/next-auth
