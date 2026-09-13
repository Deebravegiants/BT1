# [M] Potential Sensitive Cookie Exposure in NPM Packages @finastra/nestjs-proxy, @ffdc/nestjs-proxy

## Summary
Severity: Medium
Advisory: GHSA-77mv-4rg7-r8qv
CVE: CVE-2022-31070
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-77mv-4rg7-r8qv
Type: github-advisory

## Affected
- npm: `@finastra/nestjs-proxy` — affected >=0 <0.7.0

## Details
The nestjs-proxy library did not have a way to block sensitive cookies (e.g. session cookies) from being forwarded to backend services configured by the application developer. This could have led to sensitive cookies being inadvertently exposed to such services that should not see them.

The patched version now blocks cookies from being forwarded by default. However developers can configure an allow-list of cookie names by using the `allowedCookies` config setting. Further details of this feature can be found in the library's README on [Github](https://github.com/Finastra/finastra-nodejs-libs/tree/develop/libs/proxy) or [NPM](https://www.npmjs.com/package/@finastra/nestjs-proxy).

### Patches
- This issue has been fixed in version 0.7.0 of `@finastra/nestjs-proxy`.
- Users of `@ffdc/nestjs-proxy` are advised that this package has been deprecated and is no longer being maintained or receiving updates. Please update your package.json file to use `@finastra/nestjs-proxy` instead.

### References
- https://github.com/Finastra/finastra-nodejs-libs/pull/232
- https://github.com/Finastra/finastra-nodejs-libs/blob/master/libs/proxy/README.md

## References
- https://github.com/Finastra/finastra-nodejs-libs/security/advisories/GHSA-77mv-4rg7-r8qv
- https://nvd.nist.gov/vuln/detail/CVE-2022-31070
- https://github.com/Finastra/finastra-nodejs-libs/pull/232
- https://github.com/Finastra/finastra-nodejs-libs
