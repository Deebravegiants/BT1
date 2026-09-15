# [M] NextAuth.js default redirect callback vulnerable to open redirects

## Summary
Severity: Medium
Advisory: GHSA-f9wg-5f46-cjmw
CVE: CVE-2022-24858
CWE: CWE-290, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-f9wg-5f46-cjmw
Type: github-advisory

## Affected
- npm: `next-auth` — affected >=0 <3.29.2
- npm: `next-auth` — affected >=4.0.0 <4.3.2

## Details
`next-auth` v3 users before version 3.29.2 are impacted. (We recommend upgrading to v4 in most cases. See our [migration guide](https://next-auth.js.org/getting-started/upgrade-v4)).`next-auth` v4 users before version 4.3.2 are impacted. Upgrading to 3.29.2 or 4.3.2 will patch this vulnerability. If you are not able to upgrade for any reason, you can add a configuration to your `callbacks` option:

```js
// async redirect(url, baseUrl) { // v3
async redirect({ url, baseUrl }) { // v4
    // Allows relative callback URLs
    if (url.startsWith("/")) return new URL(url, baseUrl).toString()
    // Allows callback URLs on the same origin
    else if (new URL(url).origin === baseUrl) return url
    return baseUrl
}
```
If you already have a `redirect` callback, make sure that you match the incoming `url` origin against the `baseUrl`.

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-f9wg-5f46-cjmw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24858
- https://github.com/nextauthjs/next-auth/commit/6e15bdcb2d93c1ad5ee3889f702607637e79db50
- https://github.com/nextauthjs/next-auth
- https://github.com/nextauthjs/next-auth/releases/tag/next-auth%40v4.3.2
- https://next-auth.js.org/configuration/callbacks#redirect-callback
- https://next-auth.js.org/getting-started/upgrade-v4
