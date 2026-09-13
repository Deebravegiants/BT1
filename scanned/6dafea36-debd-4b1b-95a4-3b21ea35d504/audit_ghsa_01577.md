# [H] xml-crypto's HMAC-SHA1 signatures can bypass validation via key confusion

## Summary
Severity: High
Advisory: GHSA-c27r-x354-4m68
CWE: CWE-287
Ecosystem: npm
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-c27r-x354-4m68
Type: github-advisory

## Affected
- npm: `xml-crypto` — affected >=0 <2.0.0

## Details
### Impact
An attacker can inject an HMAC-SHA1 signature that is valid using only knowledge of the RSA public key. This allows bypassing signature validation.

### Patches
Version 2.0.0 has the fix.

### Workarounds
The recommendation is to upgrade. In case that is not possible remove the 'http://www.w3.org/2000/09/xmldsig#hmac-sha1' entry from SignedXml.SignatureAlgorithms.

## References
- https://github.com/yaronn/xml-crypto/security/advisories/GHSA-c27r-x354-4m68
- https://github.com/yaronn/xml-crypto/commit/3d9db712e6232c765cd2ad6bd2902b88a0d22100
- https://github.com/yaronn/xml-crypto
- https://www.npmjs.com/package/xml-crypto
