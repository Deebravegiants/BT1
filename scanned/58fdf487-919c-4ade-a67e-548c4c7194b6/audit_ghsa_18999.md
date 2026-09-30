# [H] node-forge has an Interpretation Conflict vulnerability via its ASN.1 Validator Desynchronization

## Summary
Severity: High
Advisory: GHSA-5gfm-wpxj-wjgq
CVE: CVE-2025-12816
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-5gfm-wpxj-wjgq
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.3.2

## Details
### Summary

CVE-2025-12816 has been reserved by CERT/CC

**Description**
An Interpretation Conflict (CWE-436) vulnerability in node-forge versions 1.3.1 and below enables remote, unauthenticated attackers to craft ASN.1 structures to desynchronize schema validations, yielding a semantic divergence that may bypass downstream cryptographic verifications and security decisions.


### Details

A critical ASN.1 validation bypass vulnerability exists in the node-forge asn1.validate function within `forge/lib/asn1.js`. ASN.1 is a schema language that defines data structures, like the typed record schemas used in X.509, PKCS#7, PKCS#12, etc. DER (Distinguished Encoding Rules), a strict binary encoding of ASN.1, is what cryptographic code expects when verifying signatures, and the exact bytes and structure must match the schema used to compute and verify the signature. After deserializing DER, Forge uses static ASN.1 validation schemas to locate the signed data or public key, compute digests over the exact bytes required, and feed digest and signature fields into cryptographic primitives.

This vulnerability allows a specially crafted ASN.1 object to desynchronize the validator on optional boundaries, causing a malformed optional field to be semantically reinterpreted as the subsequent mandatory structure. This manifests as logic bypasses in cryptographic algorithms and protocols with optional security features (such as PKCS#12, where MACs are treated as absent) and semantic interpretation conflicts in strict protocols (such as X.509, where fields are read as the wrong type).

### Impact

This flaw allows an attacker to desynchronize the validator, allowing critical components like digital signatures or integrity checks to be skipped or validated against attacker-controlled data.

This vulnerability impacts the `ans1.validate` function in `node-forge` before patched version `1.3.2`.
https://github.com/digitalbazaar/forge/blob/main/lib/asn1.js.

The following components in `node-forge` are impacted.
[lib/asn1.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/asn1.js#L1153)
[lib/x509.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/x509.js#L667)
[lib/pkcs12.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/pkcs12.js#L328)
[lib/pkcs7.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/pkcs7.js#L90)
[lib/rsa.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/rsa.js#L1167)
[lib/pbe.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/pbe.js#L363)
[lib/ed25519.js](https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/ed25519.js#L81)

Any downstream application using these components is impacted.

These components may be leveraged by downstream applications in ways that enable full compromise of integrity, leading to potential availability and confidentiality compromises.

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-5gfm-wpxj-wjgq
- https://github.com/digitalbazaar/forge/pull/1124
- https://github.com/digitalbazaar/forge
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/asn1.js#L1153
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/ed25519.js#L81
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/pbe.js#L363
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/pkcs12.js#L328
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/pkcs7.js#L90
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/rsa.js#L1167
- https://github.com/digitalbazaar/forge/blob/2bb97afb5058285ef09bcf1d04d6bd6b87cffd58/lib/x509.js#L667
- https://kb.cert.org/vuls/id/521113
- https://www.kb.cert.org/vuls/id/521113
- https://www.npmjs.com/package/node-forge
