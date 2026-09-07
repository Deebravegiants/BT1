# [H] Improper Verification of Cryptographic Signature in Nimbus JOSE+JWT

## Summary
Severity: High
Advisory: GHSA-pfv2-37f7-9m6w
CVE: CVE-2017-12974
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pfv2-37f7-9m6w
Type: github-advisory

## Affected
- Maven: `com.nimbusds:nimbus-jose-jwt` — affected >=0 <4.36

## Details
Nimbus JOSE+JWT before 4.36 proceeds with ECKey construction without ensuring that the public x and y coordinates are on the specified curve, which allows attackers to conduct an Invalid Curve Attack in environments where the JCE provider lacks the applicable curve validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12974
- https://bitbucket.org/connect2id/nimbus-jose-jwt/commits/f3a7a801f0c6b078899fed9226368eb7b44e2b2f
- https://bitbucket.org/connect2id/nimbus-jose-jwt/issues/217/explicit-check-for-ec-public-key-on-curve
- https://bitbucket.org/connect2id/nimbus-jose-jwt/src/master/CHANGELOG.txt
- https://github.com/felx/nimbus-jose-jwt
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
