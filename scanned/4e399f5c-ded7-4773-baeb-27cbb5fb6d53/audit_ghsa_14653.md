# [H] SimpleSAMLphp xml-common XXE vulnerability

## Summary
Severity: High
Advisory: GHSA-2x65-fpch-2fcm
CVE: CVE-2024-52596
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-2x65-fpch-2fcm
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/xml-common` — affected >=0 <1.20.0

## Details
Summary

When loading an (untrusted) XML document, for example the SAMLResponse, it's possible to induce an XXE.

$options is defined as: https://github.com/simplesamlphp/xml-common/blob/v1.19.0/src/DOMDocumentFactory.php#L39
including the DTDLoad option, which allows an attacker to read file contents from local file system OR internal network.

While there is the NONET option, an attacker can simply bypass if by using PHP filters:
php://filter/convert.base64-encode/resource=http://URL OR FILE

From there an attacker can induce network connections and steal the targeted file OOB (haven't fully tested this).

RCE may be possible with the php://expect or php://phar wrappers, but this hasn't been tested.

Note:
The mitigation here:
https://github.com/simplesamlphp/xml-common/blob/v1.19.0/src/DOMDocumentFactory.php#L58
Comes too late, as the XML has already been loaded into a document.
Mitigation:

Remove the LIBXML_DTDLOAD | LIBXML_DTDATTR options.
Additionally, as a defense in depth measure, check if there is the string: <!DOCTYPE inside the XML before parsing it. (This is not a complete fix because someone may be able to exploit some parser differentials, to load a DOCTYPE, maybe through spacing like: <! DOCTYPE)

## References
- https://github.com/simplesamlphp/xml-common/security/advisories/GHSA-2x65-fpch-2fcm
- https://nvd.nist.gov/vuln/detail/CVE-2024-52596
- https://github.com/simplesamlphp/xml-common/commit/fa4ade391c3194466acf5fbfd5d2ecdbf5e831f5
- https://github.com/simplesamlphp/xml-common
- https://lists.debian.org/debian-lts-announce/2024/12/msg00001.html
