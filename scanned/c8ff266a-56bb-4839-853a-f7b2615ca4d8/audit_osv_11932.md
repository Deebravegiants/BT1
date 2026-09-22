# [C] CVE-2018-1000125

## Summary
Severity: Critical
Advisory: CVE-2018-1000125
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000125
Type: osv

## Details
inversoft prime-jwt version prior to version 1.3.0 or prior to commit 0d94dcef0133d699f21d217e922564adbb83a227 contains an input validation vulnerability in JWTDecoder.decode that can result in a JWT that is decoded and thus implicitly validated even if it lacks a valid signature. This attack appear to be exploitable via an attacker crafting a token with a valid header and body and then requests it to be validated. This vulnerability appears to have been fixed in 1.3.0 and later or after commit 0d94dcef0133d699f21d217e922564adbb83a227.

## References
- https://github.com/inversoft/prime-jwt/blob/master/CHANGES
- https://github.com/inversoft/prime-jwt/issues/2
