# [H] Improper Handling of `callbackUrl` parameter in next-auth

## Summary
Severity: High
Advisory: GHSA-g5fm-jp9v-2432
CVE: CVE-2022-31093
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-g5fm-jp9v-2432
Type: github-advisory

## Affected
- npm: `next-auth` — affected >=0 <3.29.5
- npm: `next-auth` — affected >=4.0.0 <4.5.0

## Details
### Impact

An attacker can send a request to an app using NextAuth.js with an invalid `callbackUrl` query parameter, which internally we convert to a `URL` object. The URL instantiation would fail due to a malformed URL being passed into the constructor, causing it to throw an unhandled error which led to our **API route handler timing out and logging in to fail**. This has been remedied in the following releases:

next-auth v3 users before version 3.29.5 are impacted. (We recommend upgrading to v4, as v3 is considered unmaintained. See our [migration guide](https://next-auth.js.org/getting-started/upgrade-v4))

next-auth v4 users before version 4.5.0 are impacted.

### Patches

We've released patches for this vulnerability in:
  
- v3 - `3.29.5`
- v4 - `4.5.0`

You can do:

```sh
npm i next-auth@latest
```

or

```sh
yarn add next-auth@latest
```

or

```sh
pnpm add next-auth@latest
```

(This will update to the latest v4 version, but you can change  `latest` to `3` if you want to stay on v3. This is not recommended.)

### Workarounds

If for some reason you cannot upgrade, the workaround requires you to rely on [Advanced Initialization](https://next-auth.js.org/configuration/initialization#advanced-initialization). Here is an example:

**Before:**

```js
// pages/api/auth/[...nextauth].js
import NextAuth from "next-auth"

export default NextAuth(/* your config */)
```

**After:**

```js
// pages/api/auth/[...nextauth].js
import NextAuth from "next-auth"

function isValidHttpUrl(url) {
  try {
    return /^https?:/.test(url).protocol
  } catch {
    return false;
  }
}

export default async function handler(req, res) {
  if (
    req.query.callbackUrl &&
    !isValidHttpUrl(req.query.callbackUrl)
  ) {
   return res.status(500).send('');
  }
  
  return await NextAuth(req, res, /* your config */)
}
```


### References

This vulnerability was discovered not long after https://github.com/nextauthjs/next-auth/security/advisories/GHSA-q2mx-j4x2-2h74 was published and is very similar in nature.

Related documentation:

- https://next-auth.js.org/getting-started/client#specifying-a-callbackurl
- https://next-auth.js.org/configuration/callbacks#redirect-callback

A test case has been added so this kind of issue will be checked before publishing. See: https://github.com/nextauthjs/next-auth/commit/e498483b23273d1bfc81be68339607f88d411bd6

### For more information

If you have any concerns, we request responsible disclosure, outlined here: https://next-auth.js.org/security#reporting-a-vulnerability

### Timeline

The issue was reported 2022 June 10th, a response was sent out to the reporter in less than 2 hours, and a patch was published within 3 hours.

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-g5fm-jp9v-2432
- https://nvd.nist.gov/vuln/detail/CVE-2022-31093
- https://github.com/nextauthjs/next-auth/commit/25517b73153332d948114bacdff3b5908de91d85
- https://github.com/nextauthjs/next-auth/commit/e498483b23273d1bfc81be68339607f88d411bd6
- https://github.com/nextauthjs/next-auth
- https://next-auth.js.org/configuration/initialization#advanced-initialization
