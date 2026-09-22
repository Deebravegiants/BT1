# [C] xml-crypto vulnerable to XML signature verification bypass due improper verification of signature/signature spoofing

## Summary
Severity: Critical
Advisory: GHSA-2xp3-57p7-qf4v
CVE: CVE-2024-32962
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-2xp3-57p7-qf4v
Type: github-advisory

## Affected
- npm: `xml-crypto` — affected >=4.0.0 <6.0.0

## Details
### Summary

Default configuration does not check authorization of the signer, it only checks the validity of the signature per section 3.2.2 of https://www.w3.org/TR/2008/REC-xmldsig-core-20080610/#sec-CoreValidation. As such, without additional validation steps, the default configuration allows a malicious actor to re-sign an XML document, place the certificate in a `<KeyInfo />` element, and pass `xml-crypto` default validation checks.

### Details

Affected `xml-crypto` versions between versions `>= 4.0.0` and `< 6.0.0`. 

`xml-crypto` trusts by default any certificate provided via digitally signed XML document's `<KeyInfo />`.

`xml-crypto` prefers to use any certificate provided via digitally signed XML document's `<KeyInfo />` even if library was configured to use specific certificate (`publicCert`) for signature verification purposes.

Attacker can spoof signature verification by modifying XML document and replacing existing signature with signature generated with malicious private key (created by attacker) and by attaching that private key's certificate to `<KeyInfo />` element.

Vulnerability is combination of changes introduced to `4.0.0` at
* https://github.com/node-saml/xml-crypto/pull/301
* https://github.com/node-saml/xml-crypto/commit/c2b83f984049edb68ad1d7c6ad0739ec92af11ca

Changes at PR provided default method to extract certificate from signed XML document.
* https://github.com/node-saml/xml-crypto/blob/c2b83f984049edb68ad1d7c6ad0739ec92af11ca/lib/signed-xml.js#L405-L414
* https://github.com/node-saml/xml-crypto/blob/c2b83f984049edb68ad1d7c6ad0739ec92af11ca/lib/signed-xml.js#L334

and changes at PR prefer output of that method to be used as certificate for signature verification even in the case when library is configured to use specific/pre-configured `signingCert`
* https://github.com/node-saml/xml-crypto/blob/c2b83f984049edb68ad1d7c6ad0739ec92af11ca/lib/signed-xml.js#L507

Name of the `signingCert` was changed later (but prior to `4.0.0` release) to `publicCert`:
* https://github.com/node-saml/xml-crypto/commit/78329fbae34c9b25ba25882604e960f506d7c0e7
* https://github.com/node-saml/xml-crypto/blob/78329fbae34c9b25ba25882604e960f506d7c0e7/lib/signed-xml.js#L507

Issue was fixed to `6.0.0` by disabling implicit usage of default `getCertFromKeyInfo` implementation:
* https://github.com/node-saml/xml-crypto/pull/445
* https://github.com/node-saml/xml-crypto/commit/21201723d2ca9bc11288f62cf72552b7d659b000

Possible workarounds for versions 4.x and 5.x:
- Check the certificate extracted via `getCertFromKeyInfo` against trusted certificates before accepting the results of the validation.
- Set `xml-crypto`'s `getCertFromKeyInfo` to `() => undefined` forcing `xml-crypto` to use an explicitly configured `publicCert` or `privateKey` for signature verification.

### PoC

https://github.com/node-saml/xml-crypto/discussions/399

### Impact

An untrusted certificate can be used to pass a malicious XML payload through an improperly configured installation of `xml-crypto`.

## References
- https://github.com/node-saml/xml-crypto/security/advisories/GHSA-2xp3-57p7-qf4v
- https://nvd.nist.gov/vuln/detail/CVE-2024-32962
- https://github.com/node-saml/xml-crypto/pull/301
- https://github.com/node-saml/xml-crypto/pull/445
- https://github.com/node-saml/xml-crypto/commit/21201723d2ca9bc11288f62cf72552b7d659b000
- https://github.com/node-saml/xml-crypto/commit/c2b83f984049edb68ad1d7c6ad0739ec92af11ca
- https://github.com/node-saml/xml-crypto
- https://github.com/node-saml/xml-crypto/discussions/399
- https://security.netapp.com/advisory/ntap-20240705-0003
- https://www.w3.org/TR/2008/REC-xmldsig-core-20080610/#sec-CoreValidation
