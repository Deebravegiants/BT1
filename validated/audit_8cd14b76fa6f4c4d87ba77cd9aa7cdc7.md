No vulnerability found for this question.

The `ProofOfPossession::verify` function's design and implementation correctly enforce the rogue-key-attack invariant. `verify` calls `self.pop.verify(true, &pk.to_bytes(), DST_BLS_POP_IN_G2, &[], &pk.pubkey, true)` [1](#0-0) , which performs a standard BLS pairing-based signature verification where the message being signed is the public key's own serialized bytes and the verification key is that same public key. A PoP is fundamentally just a BLS signature on `pk_bytes` under `pk`'s own private key [2](#0-1) . For an attacker's crafted 96-byte blob to pass `verify` against a victim's already-registered public key, the attacker would need to produce a valid BLS signature over that victim's public key bytes without knowing the victim's private key — this is exactly the discrete-log/pairing hardness assumption that BLS signature unforgeability rests on, enforced here via the underlying `blst` pairing check (`BLST_ERROR::BLST_SUCCESS`). There is no logic gap in this implementation (e.g., no missing subgroup check, no message/key confusion, no accepting an all-zero or degenerate signature) — subgroup checks are done implicitly via `pk_validate: true` and message binding is exact.

The Move-level entrypoint `public_key_from_bytes_with_pop` in `bls12381.move` correctly requires the pop to verify before returning `Some(PublicKeyWithPoP)` [3](#0-2) , and the underlying native `native_bls12381_verify_proof_of_possession` deserializes both the pk and pop and calls `pop.verify(&pk)`, returning `false` on any deserialization or verification failure [4](#0-3) . Existing unit tests (`bls12381_pop_verify` in `crates/aptos-crypto/src/unit_tests/bls12381_test.rs` and `test_verify_pop`/`test_verify_pop_randomized` in `bls12381.move`) already assert exactly the "proof idea" scenario described in the question — that a PoP created for one keypair does not verify against a different/mismatched public key [5](#0-4) [6](#0-5) . Since the security guarantee relies on BLS signature unforgeability (a cryptographic hardness assumption, not a code-path/custody-boundary bug), and no implementation defect bypasses that check, this does not constitute a valid custody-boundary vulnerability under the review scope.

### Citations

**File:** crates/aptos-crypto/src/bls12381/bls12381_pop.rs (L54-65)
```rust
    pub fn verify(&self, pk: &PublicKey) -> Result<()> {
        // CRYPTONOTE(Alin): We call the signature verification function with pk_validate set to true
        // since we do not necessarily trust the PK we deserialized over the network whose PoP we are
        // verifying here.
        let result = self.pop.verify(
            true,
            &pk.to_bytes(),
            DST_BLS_POP_IN_G2,
            &[],
            &pk.pubkey,
            true,
        );
```

**File:** crates/aptos-crypto/src/bls12381/bls12381_pop.rs (L94-102)
```rust
    pub fn create_with_pubkey(sk: &PrivateKey, pk: &PublicKey) -> ProofOfPossession {
        // CRYPTONOTE(Alin): The standard does not detail how the PK should be serialized for hashing purposes; we just do the obvious.
        let pk_bytes = pk.to_bytes();

        // CRYPTONOTE(Alin): We hash with DST_BLS_POP_IN_G2 as per https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-bls-signature#section-4.2.3
        ProofOfPossession {
            pop: sk.privkey.sign(&pk_bytes, DST_BLS_POP_IN_G2, &[]),
        }
    }
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/bls12381.move (L115-123)
```text
    public fun public_key_from_bytes_with_pop(pk_bytes: vector<u8>, pop: &ProofOfPossession): Option<PublicKeyWithPoP> {
        if (verify_proof_of_possession_internal(pk_bytes, pop.bytes)) {
            option::some(PublicKeyWithPoP {
                bytes: pk_bytes
            })
        } else {
            option::none<PublicKeyWithPoP>()
        }
    }
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/bls12381.move (L967-975)
```text
    #[test]
    fun test_verify_pop_randomized() {
        let (sk, pk) = generate_keys();
        let pk_bytes = public_key_with_pop_to_bytes(&pk);
        let pop = generate_proof_of_possession(&sk);
        assert!(public_key_from_bytes_with_pop(pk_bytes, &pop).is_some(), 1);
        assert!(public_key_from_bytes_with_pop(pk_bytes, &maul_proof_of_possession(&pop)).is_none(), 1);
        assert!(public_key_from_bytes_with_pop(maul_bytes(&pk_bytes), &pop).is_none(), 1);
    }
```

**File:** aptos-move/framework/natives/src/cryptography/bls12381.rs (L567-595)
```rust
fn native_bls12381_verify_proof_of_possession(
    context: &mut SafeNativeContext,
    ty_args: &[Type],
    mut arguments: VecDeque<Value>,
) -> SafeNativeResult<SmallVec<[Value; 1]>> {
    debug_assert!(ty_args.is_empty());
    debug_assert!(arguments.len() == 2);

    context.charge(BLS12381_BASE)?;

    let pop_bytes = safely_pop_arg!(arguments, Vec<u8>);
    let key_bytes = safely_pop_arg!(arguments, Vec<u8>);

    let pk = match bls12381_deserialize_pk(key_bytes, context)? {
        Some(pk) => pk,
        None => return Ok(smallvec![Value::bool(false)]),
    };

    let pop = match bls12381_deserialize_pop(pop_bytes, context)? {
        Some(pop) => pop,
        None => return Ok(smallvec![Value::bool(false)]),
    };

    // NOTE(Gas): 2 bilinear pairings and a hash-to-curve
    context.charge(BLS12381_PER_POP_VERIFY * NumArgs::one())?;
    let valid = pop.verify(&pk).is_ok();

    Ok(smallvec![Value::bool(valid)])
}
```

**File:** crates/aptos-crypto/src/unit_tests/bls12381_test.rs (L72-84)
```rust
    let pop_bad =
        ProofOfPossession::create_with_pubkey(&keypair1.private_key, &keypair2.public_key);

    // PoP for SK i should verify for PK i
    assert!(pop1.verify(&keypair1.public_key).is_ok());
    assert!(pop2.verify(&keypair2.public_key).is_ok());

    // PoP for SK 1 should not verify for PK 2
    assert!(pop1.verify(&keypair2.public_key).is_err());
    // Pop for SK 2 should not verify for PK 1
    assert!(pop2.verify(&keypair1.public_key).is_err());
    // Invalid PoP for SK 2 should not verify
    assert!(pop_bad.verify(&keypair2.public_key).is_err());
```
