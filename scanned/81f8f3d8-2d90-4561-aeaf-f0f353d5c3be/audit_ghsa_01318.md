# [H] NoSQL injection in express-cart

## Summary
Severity: High
Advisory: GHSA-f5cv-xrv9-r8w7
CWE: CWE-89
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-f5cv-xrv9-r8w7
Type: github-advisory

## Affected
- npm: `express-cart` — affected >=0 <1.1.8

## Details
Versions of `express-cart` before 1.1.8 are vulnerable to NoSQL injection. 

The vulnerability is caused by the lack of user input sanitization in the login handlers. In both cases, the customer login and the admin login, parameters from the JSON body are sent directly into the MongoDB query which allows to insert operators. 

These operators can be used to extract the value of the field blindly in the same manner of a blind SQL injection. In this case, the `$regex` operator is used to guess each character of the token from the start.


## Recommendation

Update to version 1.1.8 or later.

## References
- https://hackerone.com/reports/397445
- https://github.com/nodejs/security-wg
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/472.json
- https://www.npmjs.com/advisories/724
