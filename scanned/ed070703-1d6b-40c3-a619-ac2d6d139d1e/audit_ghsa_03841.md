# [C] SQL Injection in sequelize

## Summary
Severity: Critical
Advisory: GHSA-m9jw-237r-gvfv
CVE: CVE-2019-10752
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-25
Source: https://github.com/advisories/GHSA-m9jw-237r-gvfv
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <4.44.3
- npm: `sequelize` — affected >=5.0.0 <5.15.1

## Details
Affected versions of `sequelize` are vulnerable to SQL Injection. The function `sequelize.json()` incorrectly formatted sub paths for JSON queries, which allows attackers to inject SQL statements and execute arbitrary SQL queries if user input is passed to the query.  Exploitation example:  

```js
return User.findAll({
  where: this.sequelize.json("data.id')) AS DECIMAL) = 1 DELETE YOLO INJECTIONS; -- ", 1)
});
```


## Recommendation

If you are using `sequelize` 5.x, upgrade to version 5.15.1 or later.
If you are using `sequelize` 4.x, upgrade to version 4.44.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10752
- https://github.com/sequelize/sequelize/pull/11329
- https://github.com/sequelize/sequelize/commit/9bd0bc1,
- https://github.com/sequelize/sequelize/commit/9bd0bc111b6f502223edf7e902680f7cc2ed541e
- https://snyk.io/vuln/SNYK-JS-SEQUELIZE-459751
- https://snyk.io/vuln/SNYK-JS-SEQUELIZE-459751,
- https://www.npmjs.com/advisories/1146
