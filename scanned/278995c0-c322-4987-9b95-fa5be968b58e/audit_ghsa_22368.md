# [M] SimpleSAMLphp Unauthenticated encryption in CBC mode

## Summary
Severity: Medium
Advisory: GHSA-44pr-mgcp-v36r
CVE: CVE-2017-12870
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-44pr-mgcp-v36r
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.14.13

## Details
SimpleSAMLphp 1.14.12 and earlier make it easier for man-in-the-middle attackers to obtain sensitive information by leveraging use of the aesEncrypt and aesDecrypt methods in the SimpleSAML/Utils/Crypto class to protect session identifiers in replies to non-HTTPS service providers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12870
- https://github.com/simplesamlphp/simplesamlphp/commit/4c939be1696bacb2b95ee11d4ebc5814a08b04c5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12870.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201704-01
