# [M] Discourse allows iframe injection though default site setting

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-39320
Aliases: CVE-2024-39320, GHSA-4p82-xh38-gq4p
Ecosystem: Bitnami
Published: 2024-08-01
Source: https://osv.dev/vulnerability/BIT-discourse-2024-39320
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.5

## Details
Discourse is an open source discussion platform. Prior to 3.2.5 and 3.3.0.beta5, the vulnerability allows an attacker to inject iframes from any domain, bypassing the intended restrictions enforced by the allowed_iframes setting. This vulnerability is fixed in 3.2.5 and 3.3.0.beta5.

## References
- https://github.com/discourse/discourse/commit/188cb58daa833839c54c266ce22db150a3f3a210
- https://github.com/discourse/discourse/commit/76f06f6b1491db6bd09a4017d2c5591431b3b16e
- https://github.com/discourse/discourse/security/advisories/GHSA-4p82-xh38-gq4p
- https://nvd.nist.gov/vuln/detail/CVE-2024-39320
