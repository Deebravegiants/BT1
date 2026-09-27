# [H] SimpleSAMLphp saml2 incorrect signature validation

## Summary
Severity: High
Advisory: GHSA-g888-g2pp-82hf
CVE: CVE-2018-7711
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g888-g2pp-82hf
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=0 <1.10.6
- Packagist: `simplesamlphp/saml2` — affected >=2.0 <2.3.8
- Packagist: `simplesamlphp/saml2` — affected >=3.0 <3.1.4

## Details
HTTPRedirect.php in the saml2 library in SimpleSAMLphp before 1.15.4 has an incorrect check of return values in the signature validation utilities, allowing an attacker to get invalid signatures accepted as valid by forcing an error during validation. This occurs because of a dependency on PHP functionality that interprets a -1 error code as a true boolean value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7711
- https://github.com/simplesamlphp/saml2/commit/4f6af7f69f29df8555a18b9bb7b646906b45924d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/saml2/CVE-2018-7711.yaml
- https://lists.debian.org/debian-lts-announce/2018/03/msg00017.html
- https://simplesamlphp.org/security/201803-01
