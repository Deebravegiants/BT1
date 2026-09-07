# [H] Unauthorized File Access in node-git-server

## Summary
Severity: High
Advisory: GHSA-cv3v-7846-6pxm
CWE: CWE-552
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-cv3v-7846-6pxm
Type: github-advisory

## Affected
- npm: `node-git-server` — affected >=0.2.0 <0.6.1

## Details
Versions of `node-git-server` prior to 0.6.1 are vulnerable to Unauthorized File Access. It is possible to access any git repository by using absolute paths, which may allow attackers to access private repositories.


## Recommendation

Upgrade to version 0.6.1 or later.

## References
- https://github.com/gabrielcsapo/node-git-server/pull/62
- https://github.com/gabrielcsapo/node-git-server/commit/ac26650f69bc445d71e4f2c55328676d10a4be43
- https://github.com/gabrielcsapo/node-git-server/commit/fb8d62710e3d78c796e04a33fcff66cea3f212f3
- https://github.com/gabrielcsapo/node-git-server
- https://github.com/gabrielcsapo/node-git-server/blob/0.2.0/lib/git.js
- https://github.com/gabrielcsapo/node-git-server/tree/0.1.0
- https://snyk.io/vuln/SNYK-JS-NODEGITSERVER-474343
