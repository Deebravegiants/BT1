# [H] PHP JOSE Library by Gree Inc. Uses a Broken or Risky Cryptographic Algorithm

## Summary
Severity: High
Advisory: GHSA-xm5f-hc9r-76f3
CVE: CVE-2016-5431
CWE: CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xm5f-hc9r-76f3
Type: github-advisory

## Affected
- Packagist: `gree/jose` — affected >=0 <2.2.1

## Details
The PHP JOSE Library by Gree Inc. prior to 2.2.1 is vulnerable to key confusion/algorithm substitution in the JWS component resulting in bypassing the signature verification via crafted tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5431
- https://github.com/nov/jose-php/commit/1cce55e27adf0274193eb1cd74b927a398a3df4b
- https://github.com/nov/jose-php
