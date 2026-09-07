# [M] URL Redirection to Untrusted Site ('Open Redirect') in next-auth

## Summary
Severity: Medium
Advisory: GHSA-q2mx-j4x2-2h74
CVE: CVE-2022-29214
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q2mx-j4x2-2h74
Type: github-advisory

## Affected
- npm: `next-auth` — affected >=0 <3.29.3
- npm: `next-auth` — affected >=4.0.0 <4.3.3

## Details
### Impact

We found that this vulnerability is present when the developer is implementing an OAuth 1 provider (by extension, it means Twitter, which is the only built-in provider using OAuth 1), but **upgrading** is **still recommended**.

`next-auth` v3 users before version 3.29.3 are impacted. (We recommend upgrading to v4, as v3 is considered unmaintained. See our [migration guide](https://next-auth.js.org/getting-started/upgrade-v4))

`next-auth` v4 users before version 4.3.3 are impacted.

### Patches

We've released patches for this vulnerability in:
  
- v3 - `3.29.3`
- v4 - `4.3.3`

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

(This will update to the latest v4 version, but you can change  `latest` to `3` if you want to stay on v3.)

### Workarounds

If you are not able to upgrade for any reason, you can add the following configuration to your `callbacks` option:

```ts
// async redirect(url, baseUrl) { // v3
async redirect({ url, baseUrl }) { // v4
    // Allows relative callback URLs
    if (url.startsWith("/")) return `${baseUrl}${url}`
    // Allows callback URLs on the same origin
    else if (new URL(url).origin === baseUrl) return url
    return baseUrl
}
```

### References

This vulnerability was discovered right after https://github.com/nextauthjs/next-auth/security/advisories/GHSA-f9wg-5f46-cjmw was published and is very similar in nature.

Read more about the `callbacks.redirect` option in the documentation: https://next-auth.js.org/configuration/callbacks#redirect-callback

### For more information

If you have any concerns, we request responsible disclosure, outlined here: https://next-auth.js.org/security#reporting-a-vulnerability

### Timeline

The issue was reported 2022 April 20th, a response was sent out to the reporter 8 minutes after, and a patch was produced within a few days.

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-q2mx-j4x2-2h74
- https://nvd.nist.gov/vuln/detail/CVE-2022-29214
- https://github.com/nextauthjs/next-auth
- https://github.com/nextauthjs/next-auth/releases/tag/next-auth%40v4.3.3
