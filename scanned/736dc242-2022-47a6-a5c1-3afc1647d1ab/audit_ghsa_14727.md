# [M] SimpleSAMLphp SAML2 has an XXE in parsing SAML messages

## Summary
Severity: Medium
Advisory: GHSA-pxm4-r5ph-q2m2
CVE: CVE-2024-52806
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-pxm4-r5ph-q2m2
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=0 <4.6.14
- Packagist: `simplesamlphp/saml2-legacy` — affected >=0 <4.6.14

## Details
Summary

When loading an (untrusted) XML document, for example the SAMLResponse, it's possible to induce an XXE.

$options is defined as: https://github.com/simplesamlphp/saml2/blob/717c0adc4877ebd58428637e5626345e59fa0109/src/SAML2/DOMDocumentFactory.php#L41
including the DTDLoad option, which allows an attacker to read file contents from local file system OR internal network.

While there is the NONET option, an attacker can simply bypass if by using PHP filters:
php://filter/convert.base64-encode/resource=http://URL OR FILE

From there an attacker can induce network connections and steal the targeted file OOB (haven't fully tested this).

RCE may be possible with the php://expect or php://phar wrappers, but this hasn't been tested.

Note:
The mitigation here:
https://github.com/simplesamlphp/saml2/blob/717c0adc4877ebd58428637e5626345e59fa0109/src/SAML2/DOMDocumentFactory.php#L63-L69
Comes too late, as the XML has already been loaded into a document.
Mitigation:

Remove the LIBXML_DTDLOAD | LIBXML_DTDATTR options.
Additionally, as a defense in depth measure, check if there is the string: <!DOCTYPE inside the XML before parsing it. (This is not a complete fix because someone may be able to exploit some parser differentials, to load a DOCTYPE, maybe through spacing like: <! DOCTYPE)

## References
- https://github.com/simplesamlphp/saml2/security/advisories/GHSA-pxm4-r5ph-q2m2
- https://nvd.nist.gov/vuln/detail/CVE-2024-52806
- https://github.com/simplesamlphp/saml2/commit/5fd4ce4596656fb0c1278f15b8305825412e89f7
- https://github.com/simplesamlphp/saml2
