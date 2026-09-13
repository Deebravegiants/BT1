# [C] xml-crypto Vulnerable to XML Signature Verification Bypass via DigestValue Comment

## Summary
Severity: Critical
Advisory: GHSA-x3m8-899r-f7c3
CVE: CVE-2025-29775
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-x3m8-899r-f7c3
Type: github-advisory

## Affected
- npm: `xml-crypto` — affected >=4.0.0 <6.0.1
- npm: `xml-crypto` — affected >=3.0.0 <3.2.1
- npm: `xml-crypto` — affected >=0 <2.1.6

## Details
# Impact
An attacker may be able to exploit this vulnerability to bypass authentication or authorization mechanisms in systems that rely on xml-crypto for verifying signed XML documents. The vulnerability allows an attacker to modify a valid signed XML message in a way that still passes signature verification checks. For example, it could be used to alter critical identity or access control attributes, enabling an attacker to escalate privileges or impersonate another user.

# Patches
All versions <= 6.0.0 are affected. Please upgrade to version 6.0.1.

If you are still using v2.x or v3.x please upgrade to the associated patch version.

# Indicators of Compromise

When logging XML payloads, check for the following indicators. If the payload includes encrypted elements, ensure you analyze the decrypted version for a complete assessment. (If encryption is not used, analyze the original XML document directly). This applies to various XML-based authentication and authorization flows, such as SAML Response payloads.

### Presence of Comments in `DigestValue`
A `DigestValue` should **not** contain comments. If you find comments within it, this may indicate tampering.

**Example of a compromised `DigestValue`:**
```xml
<DigestValue>
    <!--TBlYWE0ZWM4ODI1NjliYzE3NmViN2E1OTlkOGDhhNmI=-->
    c7RuVDYo83z2su5uk0Nla8DXcXvKYKgf7tZklJxL/LZ=
</DigestValue>
```

### Code to test

Pass in the decrypted version of the document
```js
decryptedDocument = ... // yours to implement

const digestValues = xpath.select(
  "//*[local-name()='DigestValue'][count(node()) > 1]",
  decryptedDocument,
);

if (digestValues.length > 0) {
  // Compromise detected, yours to implement
}
```

## References
- https://github.com/node-saml/xml-crypto/security/advisories/GHSA-x3m8-899r-f7c3
- https://nvd.nist.gov/vuln/detail/CVE-2025-29775
- https://github.com/node-saml/xml-crypto/commit/28f92218ecbb8dcbd238afa4efbbd50302aa9aed
- https://github.com/node-saml/xml-crypto/commit/886dc63a8b4bb5ae1db9f41c7854b171eb83aa98
- https://github.com/node-saml/xml-crypto/commit/8ac6118ee7978b46aa56b82cbcaa5fca58c93a07
- https://github.com/node-saml/xml-crypto
- https://github.com/node-saml/xml-crypto/releases/tag/v2.1.6
- https://github.com/node-saml/xml-crypto/releases/tag/v3.2.1
- https://github.com/node-saml/xml-crypto/releases/tag/v6.0.1
- https://workos.com/blog/samlstorm
