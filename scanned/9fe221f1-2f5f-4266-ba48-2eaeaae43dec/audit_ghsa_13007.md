# [M] Cleartext Signed Message Signature Spoofing in openpgp

## Summary
Severity: Medium
Advisory: GHSA-ch3c-v47x-4pgp
CVE: CVE-2023-41037
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-ch3c-v47x-4pgp
Type: github-advisory

## Affected
- npm: `openpgp` — affected >=0 <4.10.11
- npm: `openpgp` — affected >=5.0.0 <5.10.1

## Details
### Impact
OpenPGP Cleartext Signed Messages are cryptographically signed messages where the signed text is readable without special tools:

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

This text is signed.
-----BEGIN PGP SIGNATURE-----

wnUEARMIACcFgmTkrNAJkInXCgj0fgcIFiEE1JlKzzDGQxZmmHkYidcKCPR+
BwgAAKXDAQDWGhI7tPbhB+jlKwe4+yPJ+9X8aWDUG60XFNi/w8T7ZgEAsAGd
WJrkm/H5AXGZsqyqqO6IWGF0geTCd4mWm/CsveM=
-----END PGP SIGNATURE-----
```
These messages typically contain a "Hash: ..." header declaring the hash algorithm used to compute the signature digest.
OpenPGP.js up to v5.9.0 ignored any data preceding the "Hash: ..." texts when verifying the signature. As a result, malicious parties could add arbitrary text to a third-party Cleartext Signed Message, to lead the victim to believe that the arbitrary text was signed.

A user or application is vulnerable to said attack vector if it verifies the CleartextMessage by only checking the returned `verified` property, discarding the associated `data` information, and instead _visually trusting_ the contents of the original message:

```js
const cleartextMessage = `
-----BEGIN PGP SIGNED MESSAGE-----
This text is not signed but you might think it is. Hash: SHA256

This text is signed.
-----BEGIN PGP SIGNATURE-----

wnUEARMIACcFgmTkrNAJkInXCgj0fgcIFiEE1JlKzzDGQxZmmHkYidcKCPR+
BwgAAKXDAQDWGhI7tPbhB+jlKwe4+yPJ+9X8aWDUG60XFNi/w8T7ZgEAsAGd
WJrkm/H5AXGZsqyqqO6IWGF0geTCd4mWm/CsveM=
-----END PGP SIGNATURE-----
`;
const message = await openpgp.readCleartextMessage({ cleartextMessage });
const verificationResult = await verifyCleartextMessage({ message, verificationKeys });
console.log(await verificationResult.verified); // output: true
console.log(verificationResult.data); // output: 'This text is signed.'
```
Since `verificationResult.data` would always contain the actual signed data, users and apps that check this information are not vulnerable.
Similarly, given a CleartextMessage object, retrieving the data using `getText()` or the `text` field returns only the contents that are considered when verifying the signature.
Finally, re-armoring a CleartextMessage object (using `armor()` will also result in a "sanitised" version, with the extraneous text being removed.
Because of this, we consider the vulnerability impact to be very limited when the CleartextMessage is processed programmatically; this is reflected in the Severity CVSS assessment, specifically in the scope's score ("Unchanged").

### Patches
- v5.10.1 (current stable version) will reject messages when calling `openpgp.readCleartextMessage()`
- v4.10.11 (legacy version) will reject messages when calling `openpgp.cleartext.readArmored()`

### Workarounds
Check the contents of `verificationResult.data` to see what data was actually signed, rather than visually trusting the contents of the armored message.

### References
Similar CVE: https://sec-consult.com/vulnerability-lab/advisory/cleartext-message-spoofing-in-go-cryptography-libraries-cve-2019-11841/

## References
- https://github.com/openpgpjs/openpgpjs/security/advisories/GHSA-ch3c-v47x-4pgp
- https://nvd.nist.gov/vuln/detail/CVE-2023-41037
- https://github.com/openpgpjs/openpgpjs/commit/6b43e02a254853f5ff508ebd1b07541f78b7c566
- https://github.com/openpgpjs/openpgpjs
- https://github.com/openpgpjs/openpgpjs/releases/tag/v4.10.11
- https://github.com/openpgpjs/openpgpjs/releases/tag/v5.10.1
