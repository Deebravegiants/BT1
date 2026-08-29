# [H] [express-laravel-passport] Improper Authentication

## Summary
Severity: High (CVSS 7.5)
Program: Node.js third-party modules
Weakness: Improper Authentication - Generic
Reporter: ermilov
State: resolved
Disclosed: 2020-01-04T22:09:36.655Z
Source: https://hackerone.com/reports/748214

## Details
I would like to report Improper Authentication in `express-laravel-passport`
It allows to forge user's identity

# Module

**module name:** express-laravel-passport
**version:** 1.1.2
**npm page:** `https://www.npmjs.com/package/express-laravel-passport`

## Module Description

You want a middleware support express get authorization from laravel-passport-structured database, this will help you.

## Module Stats

14 weekly downloads

# Vulnerability

## Vulnerability Description

`express-laravel-passport` is an authentication middleware which utilizes JWT tokens. The module defined to handle authentication but does not validate the JWT token sent by the user. Therefore it allows modifying payload within the token. This weakness provides an opportunity to forge the user's identity by changing the information inside the token's payload that is used to authenticate the client.

source code example:

https://github.com/EugeneNguyen/express-laravel-passport/blob/master/src/index.js#L13

```
const { jti } = jwt.decode(token);
```

`jti` variable retrieved from the token without any verification

## Steps To Reproduce:

* create directory for testing
```bash
mkdir poc
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/748214_
