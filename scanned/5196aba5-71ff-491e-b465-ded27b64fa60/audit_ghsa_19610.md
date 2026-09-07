# [C] xml-crypto Vulnerable to XML Signature Verification Bypass via Multiple SignedInfo References

## Summary
Severity: Critical
Advisory: GHSA-9p8x-f768-wp2g
CVE: CVE-2025-29774
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-9p8x-f768-wp2g
Type: github-advisory

## Affected
- npm: `xml-crypto` — affected >=4.0.0 <6.0.1
- npm: `xml-crypto` — affected >=3.0.0 <3.2.1
- npm: `xml-crypto` — affected >=0 <2.1.6

## Details
# Impact
An attacker may be able to exploit this vulnerability to bypass authentication or authorization mechanisms in systems that rely on xml-crypto for verifying signed XML documents. The vulnerability allows an attacker to modify a valid signed XML message in a way that still passes signature verification checks. For example, it could be used to alter critical identity or access control attributes, enabling an attacker with a valid account to escalate privileges or impersonate another user.

# Patches
All versions <= 6.0.0 are affected. Please upgrade to version 6.0.1.

If you are still using v2.x or v3.x please upgrade to the associated patch version.

# Indicators of Compromise

When logging XML payloads, check for the following indicators. If the payload includes encrypted elements, ensure you analyze the decrypted version for a complete assessment. (If encryption is not used, analyze the original XML document directly). This applies to various XML-based authentication and authorization flows, such as SAML Response payloads.

### Multiple SignedInfo Nodes
There should not be more than one SignedInfo node inside a Signature. If you find multiple SignedInfo nodes, it could indicate an attack.

```xml
<Signature>
    <SomeNode>
      <SignedInfo>
        <Reference URI="somefakereference">
          <DigestValue>forgeddigestvalue</DigestValue>
        </Reference>
      </SignedInfo>
    </SomeNode>
    <SignedInfo>
        <Reference URI="realsignedreference">
          <DigestValue>realdigestvalue</DigestValue>
        </Reference>
      </SignedInfo>
    </SignedInfo>
</Signature>
```

### Code to test

Pass in the decrypted version of the document
```js
decryptedDocument = ... // yours to implement

// This check is per-Signature node, not per-document
const signedInfoNodes = xpath.select(".//*[local-name(.)='SignedInfo']", signatureNode);

if (signedInfoNodes.length === 0) {
  // Not necessarily a compromise, but invalid. Should contain exactly one SignedInfo node
  // Yours to implement
}

if (signedInfoNodes.length > 1) {
  // Compromise detected, yours to implement
}
```

## References
- https://github.com/node-saml/xml-crypto/security/advisories/GHSA-9p8x-f768-wp2g
- https://nvd.nist.gov/vuln/detail/CVE-2025-29774
- https://github.com/node-saml/xml-crypto/commit/28f92218ecbb8dcbd238afa4efbbd50302aa9aed
- https://github.com/node-saml/xml-crypto/commit/886dc63a8b4bb5ae1db9f41c7854b171eb83aa98
- https://github.com/node-saml/xml-crypto/commit/8ac6118ee7978b46aa56b82cbcaa5fca58c93a07
- https://github.com/node-saml/xml-crypto
- https://github.com/node-saml/xml-crypto/releases/tag/v2.1.6
- https://github.com/node-saml/xml-crypto/releases/tag/v3.2.1
- https://github.com/node-saml/xml-crypto/releases/tag/v6.0.1
- https://workos.com/blog/samlstorm
