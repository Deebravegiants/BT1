# [H]  jsondiffpatch patch APIs are vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-j4fx-xxwh-2485
CVE: CVE-2026-8657
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-16
Source: https://github.com/advisories/GHSA-j4fx-xxwh-2485
Type: github-advisory

## Affected
- npm: `jsondiffpatch` — affected >=0 <0.7.6

## Details
Versions of the package jsondiffpatch before 0.7.6 are vulnerable to Prototype Pollution via the jsondiffpatch.patch() and jsondiffpatch/formatters/jsonpatch.patch() APIs. An attacker can perform prototype pollution by supplying crafted delta or JSON Patch documents, as attacker-controlled property names and path segments are used to traverse and modify objects without restricting access to special properties like __proto__ or constructor.prototype, allowing modification of Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8657
- https://github.com/benjamine/jsondiffpatch/commit/381c0125efab49f6f0dbc08317d01d55717672af
- https://gist.github.com/yuki-matsuhashi/e570fb1579ae1f3190059b622b0473fb
- https://github.com/benjamine/jsondiffpatch
- https://github.com/benjamine/jsondiffpatch/blob/96112c35a98f9201dd75d67fcee68a952c79e2fe/packages/jsondiffpatch/src/filters/nested.ts%23L107-L115
- https://github.com/benjamine/jsondiffpatch/blob/96112c35a98f9201dd75d67fcee68a952c79e2fe/packages/jsondiffpatch/src/filters/nested.ts%23L82-L87
- https://github.com/benjamine/jsondiffpatch/blob/96112c35a98f9201dd75d67fcee68a952c79e2fe/packages/jsondiffpatch/src/formatters/jsonpatch-apply.ts%23L146-L168
- https://github.com/benjamine/jsondiffpatch/blob/96112c35a98f9201dd75d67fcee68a952c79e2fe/packages/jsondiffpatch/src/formatters/jsonpatch-apply.ts%23L171-L199
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-16732792
- https://security.snyk.io/vuln/SNYK-JS-JSONDIFFPATCH-16322990
