# [H] Faker: helpers.fake exploitable into arbritary code execution

## Summary
Severity: High
Advisory: GHSA-qxc2-j82w-r537
CVE: CVE-2026-73231
CWE: CWE-95
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-qxc2-j82w-r537
Type: github-advisory

## Affected
- npm: `@faker-js/faker` — affected >=0 <10.5.0

## Details
### Summary

`faker.helpers.fake` can be tricked into arbritary code execution.

### Details

fakeEval.resolveProperty resolves properties on functions itself instead of resolving the nested function first.
This can be addressed by recursively calling resolveProperty instead of accessing the property after one iteration.

### PoC

Go to https://fakerjs.dev/
Open Browser console and run

````ts
await enableFaker(); // or import faker
faker.rawDefinitions.test = (() => () => {}); // Any function that returns a function
faker.helpers.fake(`{{test.constructor(alert('PowerLevel: Eval'))}}`);
````

### Impact

The Fake method claims:

> It is also NOT possible to use any non-faker methods or plain javascript in such patterns.

Which is objectively false, since any global gets fully accessible in the fake string.

## References
- https://github.com/faker-js/faker/security/advisories/GHSA-qxc2-j82w-r537
- https://nvd.nist.gov/vuln/detail/CVE-2026-73231
- https://github.com/faker-js/faker/pull/3852
- https://github.com/faker-js/faker/commit/54586208f904012f57c50b46cc1ad32bcbe4bfb7
- https://github.com/faker-js/faker
- https://github.com/faker-js/faker/releases/tag/v10.5.0
