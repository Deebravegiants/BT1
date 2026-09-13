# [H] MikroORM has Prototype Pollution in Utils.merge

## Summary
Severity: High
Advisory: GHSA-qpfv-44f3-qqx6
CVE: CVE-2026-34221
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-qpfv-44f3-qqx6
Type: github-advisory

## Affected
- npm: `@mikro-orm/core` — affected >=0 <6.6.10
- npm: `@mikro-orm/core` — affected >=7.0.0-dev.0 <7.0.6

## Details
A prototype pollution vulnerability exists in the `Utils.merge` helper used internally by MikroORM when merging object structures.

The function did not prevent special keys such as `__proto__`, `constructor`, or `prototype`, allowing attacker-controlled input to modify the JavaScript object prototype when merged.

Exploitation requires application code to pass untrusted user input into ORM operations that merge object structures, such as entity property assignment or query condition construction.

Prototype pollution may lead to denial of service or unexpected application behavior. In certain scenarios, polluted properties may influence query construction and potentially result in SQL injection depending on application code.

## References
- https://github.com/mikro-orm/mikro-orm/security/advisories/GHSA-qpfv-44f3-qqx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34221
- https://github.com/mikro-orm/mikro-orm
