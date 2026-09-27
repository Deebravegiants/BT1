# [H] Potential SQL Injection in sequelize

## Summary
Severity: High
Advisory: GHSA-2v7q-2xqx-f4q5
CVE: CVE-2016-10553
CWE: CWE-89
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-2v7q-2xqx-f4q5
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <3.0.0

## Details
Affected versions of `sequelize` are vulnerable to SQL Injection when user input is passed into `findOne` or into a statement such as `where: "user input"`.



## Recommendation

Update to version 3.0.0 or later.

Version 3.0.0 will introduce a number of breaking changes.
Thankfully, the project authors have provided a 2.x -> 3.x [upgrade guide](https://github.com/sequelize/sequelize/wiki/Upgrade-from-2.0-to-3.0) to ease this transition.

If upgrading is not an option, it is also possible to mitigate this by ensuring that all uses of `where: "input"` and `findOne("input")` are properly sanitized, such as by the use of a wrapper function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10553
- https://github.com/advisories/GHSA-2v7q-2xqx-f4q5
- https://github.com/sequelize/sequelize/blob/master/changelog.md#300
- https://www.npmjs.com/advisories/109
