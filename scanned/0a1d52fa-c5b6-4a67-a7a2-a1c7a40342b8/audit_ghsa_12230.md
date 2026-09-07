# [H] SQL Injection in sequelize

## Summary
Severity: High
Advisory: GHSA-xqg8-cv3h-xppv
CVE: CVE-2015-1369
CWE: CWE-89
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-xqg8-cv3h-xppv
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <2.0.0-rc8

## Details
Versions 2.0.0-rc-7 and earlier of `sequelize` are affected by a SQL injection vulnerability when user input is passed into the order parameter.



## Proof of Concept

```javascript
Test.findAndCountAll({
where: { id :1 },
order : [['id', 'UNTRUSTED USER INPUT']]
})
```


## Recommendation

Update to version 2.0.0-rc8 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1369
- https://github.com/sequelize/sequelize/issues/2906
- https://github.com/sequelize/sequelize/pull/2919
- https://github.com/advisories/GHSA-xqg8-cv3h-xppv
- https://github.com/sequelize/sequelize
- https://www.npmjs.com/advisories/33
- http://www.openwall.com/lists/oss-security/2015/01/23/2
