# [M] Json-jwt did not verify the cryptographic signature for data

## Summary
Severity: Medium
Advisory: GHSA-mj4x-wcxf-hm8x
CVE: CVE-2018-1000539
CWE: CWE-347
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-mj4x-wcxf-hm8x
Type: github-advisory

## Affected
- RubyGems: `json-jwt` — affected >=0.5.1 <1.9.4

## Details
The json-jwt rubygem version >= 0.5.0 && < 1.9.4 contains a CWE-347: Improper Verification of Cryptographic Signature vulnerability in Decryption of AES-GCM encrypted JSON Web Tokens that can result in Attacker can forge a authentication tag. This attack appear to be exploitable via network connectivity. This vulnerability appears to have been fixed in 1.9.4 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000539
- https://github.com/nov/json-jwt/pull/62
- https://github.com/nov/json-jwt/commit/a3b2147f0f6d9aca653e7a30e453d3a92b33413f
- https://github.com/nov/json-jwt
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/json-jwt/CVE-2018-1000539.yml
- https://www.debian.org/security/2018/dsa-4283
