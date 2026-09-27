# [H] Validation of SignedInfo

## Summary
Severity: High
Advisory: GHSA-ww7x-3gxh-qm6r
CVE: CVE-2023-49087
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-ww7x-3gxh-qm6r
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/xml-security` — affected >=1.6.11 <1.6.12
- Packagist: `simplesamlphp/saml2` — affected >=5.0.0-alpha.12 <5.0.0-alpha.13

## Details
Validation of an XML Signature requires verification that the hash value of the related XML-document (after any optional transformations and/or normalizations) matches a specific DigestValue-value, but also that the cryptografic signature on the SignedInfo-tree (the one that contains the DigestValue) verifies and matches a trusted public key.

Within the simpleSAMLphp/xml-security library (https://github.com/simplesamlphp/xml-security), the hash is being validated using SignedElementTrait::validateReference, and the signature is being verified in SignedElementTrait::verifyInternal

https://github.com/simplesamlphp/xml-security/blob/master/src/XML/SignedElementTrait.php:

![afbeelding](https://user-images.githubusercontent.com/841045/285817284-a7b7b3b4-768a-46e8-a34b-61790b6e23a5.png)

What stands out is that the signature is being calculated over the canonical version of the SignedInfo-tree. The validateReference method, however, uses the original non-canonicalized version of SignedInfo.

### Impact
If an attacker somehow (i.e. by exploiting a bug in PHP's canonicalization function) manages to manipulate the canonicalized version's DigestValue, it would be potentially be possible to forge the signature. No possibilities to exploit this were found during the investigation.

## References
- https://github.com/simplesamlphp/xml-security/security/advisories/GHSA-ww7x-3gxh-qm6r
- https://nvd.nist.gov/vuln/detail/CVE-2023-49087
- https://github.com/simplesamlphp/xml-security/commit/f509e3083dd7870cce5880c804b5122317287581
- https://github.com/simplesamlphp/xml-security
- https://github.com/simplesamlphp/xml-security/blob/master/src/XML/SignedElementTrait.php
