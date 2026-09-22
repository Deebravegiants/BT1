# [H] PyJWT vulnerable to key confusion attacks

## Summary
Severity: High
Advisory: GHSA-r9jw-mwhq-wp62
CVE: CVE-2017-11424
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r9jw-mwhq-wp62
Type: github-advisory

## Affected
- PyPI: `pyjwt` — affected >=0 <1.5.1

## Details
In PyJWT 1.5.0 and below the `invalid_strings` check in `HMACAlgorithm.prepare_key` does not account for all PEM encoded public keys. Specifically, the PKCS1 PEM encoded format would be allowed because it is prefaced with the string `-----BEGIN RSA PUBLIC KEY-----` which is not accounted for. This enables symmetric/asymmetric key confusion attacks against users using the PKCS1 PEM encoded public keys, which would allow an attacker to craft JWTs from scratch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11424
- https://github.com/jpadilla/pyjwt/pull/277
- https://github.com/jpadilla/pyjwt
- https://github.com/pypa/advisory-database/tree/main/vulns/pyjwt/PYSEC-2017-24.yaml
- http://www.debian.org/security/2017/dsa-3979
