No vulnerability found for this question.

**Rationale:**

The premise rests on a hypothetical "custom custody-gating Move contract" that doesn't exist in Aptos production code. `double_internal` in `double.rs` simply dispatches to the `double`/`square` trait methods of the `ark_bls12_381`/`ark_bn254` crates via the `ark_unary_op_internal!` macro for `G1Projective`/`G2Projective`/`Fq12` [1](#0-0) . Projective-coordinate doubling of the identity/point-at-infinity correctly yielding the identity is a basic, well-tested correctness property of the `ark-ec` group-law implementation, not custom Aptos logic, and there is no indication of a defect in it.

More importantly, there is no production custody path in Aptos that combines `crypto_algebra::double`/`eq` with an "owner" derived from an aggregated public key. The actual BLS multisig/custody-relevant aggregation used by Aptos (e.g., for validator sets and multisig authenticators) goes through `bls12381::aggregate_pubkeys` / `aggregate_pubkeys_internal`, a completely separate native from the generic `crypto_algebra` module [2](#0-1) . That path also explicitly treats the identity point as an invalid public key: `validate_pubkey_internal` documents that a valid public key must "NOT [be] the identity point" [3](#0-2) , closing off the identity-confusion scenario described for any real Aptos-native aggregated-key custody check.

The `crypto_algebra` module (and `double`/`double_internal`) is a generic cryptographic building-block library exposed to third-party Move developers [4](#0-3) ; it is not itself part of any Aptos-maintained custody, ownership, or asset-control logic. Since the review scope is limited to "Aptos production custody logic," and no such custody surface uses this native in the way described, the finding does not cross a real custody boundary.

### Citations

**File:** aptos-move/framework/natives/src/cryptography/algebra/arithmetics/double.rs (L29-63)
```rust
        Some(Structure::BLS12381G1) => ark_unary_op_internal!(
            context,
            args,
            ark_bls12_381::G1Projective,
            double,
            ALGEBRA_ARK_BLS12_381_G1_PROJ_DOUBLE
        ),
        Some(Structure::BLS12381G2) => ark_unary_op_internal!(
            context,
            args,
            ark_bls12_381::G2Projective,
            double,
            ALGEBRA_ARK_BLS12_381_G2_PROJ_DOUBLE
        ),
        Some(Structure::BLS12381Gt) => ark_unary_op_internal!(
            context,
            args,
            ark_bls12_381::Fq12,
            square,
            ALGEBRA_ARK_BLS12_381_FQ12_SQUARE
        ),
        Some(Structure::BN254G1) => ark_unary_op_internal!(
            context,
            args,
            ark_bn254::G1Projective,
            double,
            ALGEBRA_ARK_BN254_G1_PROJ_DOUBLE
        ),
        Some(Structure::BN254G2) => ark_unary_op_internal!(
            context,
            args,
            ark_bn254::G2Projective,
            double,
            ALGEBRA_ARK_BN254_G2_PROJ_DOUBLE
        ),
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/bls12381.move (L365-371)
```text
    /// CRYPTOGRAPHY WARNING: This function assumes that the caller verified all public keys have a valid
    /// proof-of-possesion (PoP) using `verify_proof_of_possession`.
    ///
    /// Given a vector of serialized public keys, combines them into an aggregated public key, returning `(bytes, true)`,
    /// where `bytes` store the serialized public key.
    /// Aborts if no public keys are given as input.
    native fun aggregate_pubkeys_internal(public_keys: vector<PublicKeyWithPoP>): (vector<u8>, bool);
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/bls12381.move (L384-390)
```text
    /// Return `true` if the bytes in `public_key` are a valid BLS12-381 public key:
    ///  (1) it is NOT the identity point, and
    ///  (2) it is a BLS12-381 elliptic curve point, and
    ///  (3) it is a prime-order point
    /// Return `false` otherwise.
    /// Does not abort.
    native fun validate_pubkey_internal(public_key: vector<u8>): bool;
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/crypto_algebra.move (L152-158)
```text
    /// Compute `2*P` for an element `P` of a structure `S`. Faster and cheaper than `add(P, P)`.
    public fun double<S>(element_p: &Element<S>): Element<S> {
        abort_unless_cryptography_algebra_natives_enabled();
        Element<S> {
            handle: double_internal<S>(element_p.handle)
        }
    }
```
