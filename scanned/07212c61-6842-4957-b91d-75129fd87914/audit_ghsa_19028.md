# [C] @hpke/core reuses AEAD nonces

## Summary
Severity: Critical
Advisory: GHSA-73g8-5h73-26h4
CVE: CVE-2025-64767
CWE: CWE-323
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-73g8-5h73-26h4
Type: github-advisory

## Affected
- npm: `@hpke/core` — affected >=0 <1.7.5

## Details
### Summary

The public SenderContext Seal() API has a race condition which allows for the same AEAD nonce to be re-used for multiple Seal() calls. This can lead to complete loss of Confidentiality and Integrity of the produced messages.

### Details

The SenderContext Seal() [implementation](https://github.com/dajiaji/hpke-js/blob/b7fd3592c7c08660c98289d67c6bb7f891af75c4/packages/core/src/senderContext.ts#L22-L34) allows for concurrent executions to trigger `computeNonce()` with the same sequence number. This results in the same nonce being used in the suite's AEAD.

### PoC

This code reproduces the issue (and also checks for more things that could be wrong with the implementation).

```js
import { CipherSuite, KdfId, AeadId, KemId } from "hpke-js";

const suite = new CipherSuite({
  kem: KemId.DhkemP256HkdfSha256,
  kdf: KdfId.HkdfSha256,
  aead: AeadId.Aes128Gcm,
});

const keypair = await suite.kem.generateKeyPair();
const skR = keypair.privateKey;
const pkR = keypair.publicKey;

const sender = await suite.createSenderContext({
  recipientPublicKey: pkR,
});

const [message0, message1] = await Promise.all([
  sender.seal(
    new TextEncoder().encode("Secret message 1: Attack at dawn").buffer
  ),
  sender.seal(
    new TextEncoder().encode("Secret message 2: Withdraw troops").buffer
  ),
]);

const recipient = await suite.createRecipientContext({
  recipientKey: skR,
  enc: sender.enc,
});

const plaintext0 = await recipient.open(message0);
console.log("✓ Decrypted message seq=0", new TextDecoder().decode(plaintext0));

try {
  console.log(
    "✓ Decrypted message seq=1",
    new TextDecoder().decode(await recipient.open(message1))
  );
  console.log("\n✓ nonce-reuse reproduction completed, code is NOT vulnerable");
} catch (error) {
  // re-sequence the recipient to verify same nonce was used for two messages
  recipient._ctx.seq = 0;
  console.log(
    "❌ Decrypted a different message with seq=0",
    new TextDecoder().decode(await recipient.open(message1))
  );

  console.log(
    "\n✓ nonce-reuse reproduction completed, code is vulnerable, nonces are reused when concurrent calls to .seal() are used"
  );
}

// Test that failed Open() doesn't increment sequence
const recipient2 = await suite.createRecipientContext({
  recipientKey: skR,
  enc: sender.enc,
});

const invalidMessage = new Uint8Array(message0.byteLength);
invalidMessage.set(new Uint8Array(message0));
invalidMessage[0] ^= 0xff; // Corrupt the first byte

try {
  await recipient2.open(invalidMessage.buffer);
} catch {}

// Now try to open the first valid message - should still work with seq=0
try {
  await recipient2.open(message0);
  console.log("✓ Successfully decrypted message with seq=0 after failed open()");
  console.log("✓ Failed open() did NOT increment sequence");
} catch (error) {
  console.log("❌ Failed to decrypt message - sequence was incorrectly incremented");
}

// Test that same message produces same ciphertext due to nonce reuse
const sender2 = await suite.createSenderContext({
  recipientPublicKey: pkR,
});

const sameMessage = new TextEncoder().encode("Identical message").buffer;
const [cipher0, cipher1] = await Promise.all([
  sender2.seal(sameMessage),
  sender2.seal(sameMessage),
]);

const cipher0Array = new Uint8Array(cipher0);
const cipher1Array = new Uint8Array(cipher1);

let identical = true;
if (cipher0Array.length !== cipher1Array.length) {
  identical = false;
} else {
  for (let i = 0; i < cipher0Array.length; i++) {
    if (cipher0Array[i] !== cipher1Array[i]) {
      identical = false;
      break;
    }
  }
}

if (identical) {
  console.log("\n❌ Same message produced IDENTICAL ciphertext (nonce reuse confirmed)");
} else {
  console.log("\n✓ Same message produced different ciphertext (nonces are unique)");
}
```

### Recommendation

Implement a synchronization mechanism such that only one seal()/open() per context can be executed at a time.

### Notes

Refs: https://github.com/hpkewg/hpke/issues/38

> https://www.rfc-editor.org/rfc/rfc9180.html#section-9.7.5
> The AEADs specified in this document are not secure in case of nonce reuse.

> https://www.rfc-editor.org/rfc/rfc9180.html#section-5-6
> A context is an implementation-specific structure that encodes the AEAD algorithm and key in use, and manages the nonces used so that the same nonce is not used with multiple plaintexts.

The context implementation in @hpke/core is not correct given its AEAD Seal() is awaited/asynchronous.

## References
- https://github.com/dajiaji/hpke-js/security/advisories/GHSA-73g8-5h73-26h4
- https://nvd.nist.gov/vuln/detail/CVE-2025-64767
- https://github.com/dajiaji/hpke-js/commit/94a767c9b9f37ce48d5cd86f7017d8cacd294aaf
- https://github.com/dajiaji/hpke-js
- https://github.com/dajiaji/hpke-js/blob/b7fd3592c7c08660c98289d67c6bb7f891af75c4/packages/core/src/senderContext.ts#L22-L34
