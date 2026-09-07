# [M] Potential Authorization Header Exposure in NPM Packages @finastra/nestjs-proxy, @ffdc/nestjs-proxy

## Summary
Severity: Medium
Advisory: GHSA-j562-c3cw-3p5g
CVE: CVE-2022-31069
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-j562-c3cw-3p5g
Type: github-advisory

## Affected
- npm: `@finastra/nestjs-proxy` — affected >=0 <0.7.0

## Details
The nestjs-proxy library did not have a way to control when Authorization headers should should be forwarded for specific backend services configured by the application developer. This could have resulted in sensitive information such as OAuth bearer access tokens being inadvertently exposed to such services that should not see them.

A new feature has been introduced in the patched version of nestjs-proxy that allows application developers to opt out of forwarding the Authorization headers on a per service basis using the `forwardToken` config setting. Developers are advised to review the README for this library on Github or NPM for further details on how this configuration can be applied.

### Patches
- This issue has been fixed in version 0.7.0 of `@finastra/nestjs-proxy`.
- Users of `@ffdc/nestjs-proxy` are advised that this package has been deprecated and is no longer being maintained or receiving updates. Please update your package.json file to use `@finastra/nestjs-proxy` instead.

### References
- https://github.com/Finastra/finastra-nodejs-libs/pull/231
- https://github.com/Finastra/finastra-nodejs-libs/blob/master/libs/proxy/README.md

## References
- https://github.com/Finastra/finastra-nodejs-libs/security/advisories/GHSA-j562-c3cw-3p5g
- https://nvd.nist.gov/vuln/detail/CVE-2022-31069
- https://github.com/Finastra/finastra-nodejs-libs/pull/231
- https://github.com/Finastra/finastra-nodejs-libs
