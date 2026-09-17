# [M] Insecure Cryptography Algorithm in simple-crypto-js

## Summary
Severity: Medium
Advisory: GHSA-5v7r-jg9r-vq44
CWE: CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-5v7r-jg9r-vq44
Type: github-advisory

## Affected
- npm: `simple-crypto-js` — affected >=0 <2.3.0

## Details
Versions of `simple-crypto-js` prior to 2.3.0 use AES-CBC with PKCS#7 padding, which is vulnerable to padding oracle attacks. This may allow attackers to break the encryption and access sensitive data.


## Recommendation

Upgrade to version 2.3.0 or later.

## References
- https://github.com/danang-id/simple-crypto-js/issues/12
- https://github.com/danang-id/simple-crypto-js/pull/17
- https://github.com/danang-id/simple-crypto-js/commit/416584369de1dad9b21ac3fe85df0b71cf5718b2
- https://github.com/danang-id/simple-crypto-js
- https://robertheaton.com/2013/07/29/padding-oracle-attack
- https://snyk.io/vuln/SNYK-JS-SIMPLECRYPTOJS-544027
