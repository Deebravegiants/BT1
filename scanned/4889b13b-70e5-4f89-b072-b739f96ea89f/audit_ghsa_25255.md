# [M] SimpleSAMLphp Incorrect IV generation for encryption

## Summary
Severity: Medium
Advisory: GHSA-ww3w-592j-5qrw
CVE: CVE-2017-12871
CWE: CWE-326
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-ww3w-592j-5qrw
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.14.0 <1.14.12

## Details
The aesEncrypt method in `lib/SimpleSAML/Utils/Crypto.php` in SimpleSAMLphp 1.14.x through 1.14.11 makes it easier for context-dependent attackers to bypass the encryption protection mechanism by leveraging use of the first 16 bytes of the secret key as the initialization vector (IV).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12871
- https://github.com/simplesamlphp/simplesamlphp/commit/77df6a932d46daa35e364925eb73a175010dc904
- https://github.com/simplesamlphp/simplesamlphp/commit/ccf75981187aa88f7165abdb1b1965c0934acda0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12871.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201703-02
