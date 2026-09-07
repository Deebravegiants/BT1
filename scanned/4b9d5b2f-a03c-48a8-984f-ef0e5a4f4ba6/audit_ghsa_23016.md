# [H] SimpleSAMLphp Improper Verification of Cryptographic Signature

## Summary
Severity: High
Advisory: GHSA-923w-2xv2-7pr8
CVE: CVE-2018-7644
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-923w-2xv2-7pr8
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=0 <1.10.5
- Packagist: `simplesamlphp/saml2` — affected >=2.0 <2.3.7
- Packagist: `simplesamlphp/saml2` — affected >=3.0 <3.1.3

## Details
The XmlSecLibs library as used in the saml2 library in SimpleSAMLphp before 1.15.3 incorrectly verifies signatures on SAML assertions, allowing a remote attacker to construct a crafted SAML assertion on behalf of an Identity Provider that would pass as cryptographically valid, thereby allowing them to impersonate a user from that Identity Provider, aka a key confusion issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7644
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/saml2/CVE-2018-7644.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201802-01
