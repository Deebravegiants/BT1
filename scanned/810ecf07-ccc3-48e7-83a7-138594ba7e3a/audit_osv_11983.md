# [H] CVE-2018-1000531

## Summary
Severity: High
Advisory: CVE-2018-1000531
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000531
Type: osv

## Details
inversoft prime-jwt version prior to commit abb0d479389a2509f939452a6767dc424bb5e6ba contains a CWE-20 vulnerability in JWTDecoder.decode that can result in an incorrect signature validation of a JWT token. This attack can be exploitable when an attacker crafts a JWT token with a valid header using 'none' as algorithm and a body to requests it be validated. This vulnerability was fixed after commit abb0d479389a2509f939452a6767dc424bb5e6ba.

## References
- https://github.com/inversoft/prime-jwt/issues/3
