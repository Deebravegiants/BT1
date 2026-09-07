# [M] mysql Node.JS Module Vulnerable to Remote Memory Exposure

## Summary
Severity: Medium
Advisory: GHSA-5f7m-mmpc-qhh4
CWE: CWE-201
Ecosystem: npm
Published: 2019-05-23
Source: https://github.com/advisories/GHSA-5f7m-mmpc-qhh4
Type: github-advisory

## Affected
- npm: `mysql` — affected >=2.0.0-alpha8 <2.14.0

## Details
Versions of `mysql` before 2.14.0 are vulnerable to remove memory exposure.

Affected versions of `mysql` package allocate and send an uninitialized memory over the network when a number is provided as a password.

Only `mysql` running on Node.js versions below 6.0.0 are affected due to a throw added in newer node.js versions.

Proof of Concept:

```
require('mysql').createConnection({
  host: 'localhost',
  user: 'user',
  password : USERPROVIDEDINPUT,  // number
  database : 'my_db'
}).connect();
```



## Recommendation

Update to version 2.14.0 or later.

## References
- https://github.com/mysqljs/mysql/commit/192fe45593ba5768534afb6f2154432ca67a5002
- https://github.com/mysqljs/mysql/commit/310c6a7d1b2e14b63b572dbfbfa10128f20c6d52
- https://github.com/mysqljs/mysql
- https://www.npmjs.com/advisories/602
