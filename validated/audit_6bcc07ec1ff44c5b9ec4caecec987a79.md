No vulnerability found for this question.

**Rationale:**

The behavior described—duplicate `Ed25519PublicKey` entries inside a `MultiEd25519PublicKey`—is explicit, documented, intended design in Aptos, not a bug in `MultiEd25519PublicKey::try_from`.

`MultiEd25519PublicKey::try_from` only validates chunk length and threshold bounds (`threshold != 0`, `threshold <= num_of_keys`, `num_of_keys <= MAX_NUM_OF_KEYS`); it never rejects duplicate public keys, and the framework's own Move authenticator module states this is by design: `create_multi_ed25519` explicitly documents "this does *not* check uniqueness of keys. Repeated keys are convenient to encode weighted multisig policies. For example Alice AND 1 of Bob or Carol is public_key: {alice_key, alice_key, bob_key, carol_key}, threshold: 3" [1](#0-0)  and a unit test explicitly asserts "duplicate keys are ok" [2](#0-1) .

`verify_arbitrary_msg` enforces threshold against *distinct bitmap positions* (`num_ones_in_bitmap`), not distinct underlying keys, and requires one signature per set bitmap index, verified against the public key at that index [3](#0-2) . If a key is duplicated at two bitmap positions, one holder can indeed satisfy two "slots" with signatures over the same key (Ed25519 is deterministic, so the same signature bytes validate at both positions). This is exactly the intended "weighted multisig" mechanism, not a bypass.

Critically, whoever assembles the `MultiEd25519PublicKey` and registers it as an account's or resource account's authentication key is the *owner* choosing their own key material — there is no unprivileged attacker crossing into someone else's custody boundary. A victim who wants an actual N-distinct-party threshold must supply N distinct keys; nothing in this codebase silently converts a caller-supplied distinct-key policy into a duplicated one, and no privileged/other-party asset gets reassigned as a result of this behavior. This fails the Custody Impact Gate: it does not let unprivileged input take over value or authority belonging to someone other than the key-set's own creator.

### Citations

**File:** third_party/move/move-examples/diem-framework/move-packages/DPN/sources/Authenticator.move (L32-36)
```text
    /// Create a a multisig policy from a vector of ed25519 public keys and a threshold.
    /// Note: this does *not* check uniqueness of keys. Repeated keys are convenient to
    /// encode weighted multisig policies. For example Alice AND 1 of Bob or Carol is
    /// public_key: {alice_key, alice_key, bob_key, carol_key}, threshold: 3
    /// Aborts if threshold is zero or bigger than the length of `public_keys`.
```

**File:** third_party/move/move-examples/diem-framework/move-packages/DPN/tests/AuthenticatorTests.move (L36-38)
```text
        // duplicate keys are ok
        vector::push_back(&mut keys, pubkey3);
        t = Authenticator::create_multi_ed25519(copy keys, 3);
```

**File:** crates/aptos-crypto/src/multi_ed25519.rs (L527-557)
```rust
        let num_ones_in_bitmap = bitmap_count_ones(self.bitmap);
        if num_ones_in_bitmap < public_key.threshold as u32 {
            return Err(anyhow!(
                "{}",
                CryptoMaterialError::BitVecError(
                    "Not enough signatures to meet the threshold".to_string()
                )
            ));
        }
        if num_ones_in_bitmap != self.signatures.len() as u32 {
            return Err(anyhow!(
                "{}",
                CryptoMaterialError::BitVecError(
                    "Bitmap ones and signatures count are not equal".to_string()
                )
            ));
        }
        let mut bitmap_index = 0;
        // TODO: Eventually switch to deterministic batch verification
        for sig in &self.signatures {
            while !bitmap_get_bit(self.bitmap, bitmap_index) {
                bitmap_index += 1;
            }
            let pk = public_key
                .public_keys
                .get(bitmap_index)
                .ok_or_else(|| anyhow::anyhow!("Public key index {bitmap_index} out of bounds"))?;
            sig.verify_arbitrary_msg(message, pk)?;
            bitmap_index += 1;
        }
        Ok(())
```
