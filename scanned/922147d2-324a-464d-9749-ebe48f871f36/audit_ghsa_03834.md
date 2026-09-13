# [C] Sandbox Breakout in realms-shim

## Summary
Severity: Critical
Advisory: GHSA-6jg8-7333-554w
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-04
Source: https://github.com/advisories/GHSA-6jg8-7333-554w
Type: github-advisory

## Affected
- npm: `realms-shim` — affected >=0 <1.2.0
- npm: `ses` — affected >=0 <0.6.3

## Details
Versions of `realms-shim` prior to 1.2.0 are vulnerable to a Sandbox Breakout. `Reflect.construct` can be used on the sandboxed Function constructor to reach the prototypes of the primal Realm, which may allow an attacker to escape the sandbox and execute arbitrary code.


## Recommendation

Upgrade to version 1.2.0 or later.

## References
- https://github.com/Agoric/realms-shim/security/advisories/GHSA-6jg8-7333-554w
- https://github.com/Agoric/realms-shim
- https://github.com/advisories/GHSA-6jg8-7333-554w
- https://snyk.io/vuln/SNYK-JS-REALMSSHIM-471680
- https://www.npmjs.com/advisories/1180
- https://www.npmjs.com/advisories/1181
- https://www.npmjs.com/advisories/1182
- https://www.npmjs.com/advisories/1190
- https://www.npmjs.com/advisories/1191
