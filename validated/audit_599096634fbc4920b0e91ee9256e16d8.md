No vulnerability found for this question.

**Reasoning:** The `neg`, `add`, `double`, and `zero` operations in `crypto_algebra.move` are thin wrappers around native functions that delegate directly to the `arkworks` library's group arithmetic (`ark_bls12_381::G1Projective`, `ark_bn254::G1Projective`, etc.) using standard projective/extension-field representations, as seen in [1](#0-0)  and [2](#0-1) . These curve implementations use standard, well-audited projective coordinate formulas where the identity/point-at-infinity is represented canonically (e.g., `Z=0`), and negation/addition are defined to correctly handle this case as part of the group law — this is not custom, ad-hoc logic written for this PR that could have an edge-case bug; it's delegated to a widely-used, independently-audited elliptic curve library.

There is already an existing fuzz/PoC test in the repo asserting exactly the invariant the question asks about — `eq(add(x, neg(x)), zero<S>())` — including a check for `neg(zero) == zero`, as seen in [3](#0-2) , and the framework's own `bn254_algebra.move` test suite exercises negation, doubling, and addition together with cross-checks against `scalar_mul` [4](#0-3) . No evidence exists in the repo of a concrete failing case, nor is there a specific custody consumer (e.g., a multisig/aggregate-signature verifier built on `crypto_algebra`) identified in the codebase that would be affected even if such a bug existed. The claim is speculative regarding third-party library correctness rather than a demonstrated repo-specific defect, and it does not trace to a concrete unprivileged entrypoint into a live custody surface (asset transfer/mint/burn/freeze/ownership).

### Citations

**File:** aptos-move/framework/natives/src/cryptography/algebra/arithmetics/neg.rs (L45-58)
```rust
        Some(Structure::BLS12381G1) => ark_unary_op_internal!(
            context,
            args,
            ark_bls12_381::G1Projective,
            neg,
            ALGEBRA_ARK_BLS12_381_G1_PROJ_NEG
        ),
        Some(Structure::BLS12381G2) => ark_unary_op_internal!(
            context,
            args,
            ark_bls12_381::G2Projective,
            neg,
            ALGEBRA_ARK_BLS12_381_G2_PROJ_NEG
        ),
```

**File:** aptos-move/framework/natives/src/cryptography/algebra/arithmetics/double.rs (L28-42)
```rust
    match structure_opt {
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
```

**File:** testsuite/fuzzer/data/0x1/crypto_algebra/neg_internal/sources/call_native.move (L5-13)
```text
    public entry fun main(_owner:&signer) {
        let z = zero<Fr>();
        let x = from_u64<Fr>(5);
        let neg_x = neg(&x);
        let sum = add(&x, &neg_x);
        assert!(eq(&sum, &z), 0);
        let neg_z = neg(&z);
        assert!(eq(&neg_z, &z), 1);
    }
```

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/bn254_algebra.move (L557-577)
```text
        // Doubling.
        let scalar_2 = from_u64<Fr>(2);
        let point_2g = scalar_mul(&generator, &scalar_2);
        let point_double_g = double(&generator);
        assert!(eq(&point_2g, &point_double_g), 1);

        // Negation.
        let point_minus_7g_calc = neg(&point_7g_calc);
        assert!(G2_GENERATOR_MUL_BY_7_NEG_SERIALIZED_COMP == serialize<G2, FormatG2Compr>(&point_minus_7g_calc), 1);
        assert!(G2_GENERATOR_MUL_BY_7_NEG_SERIALIZED_UNCOMP == serialize<G2, FormatG2Uncompr>(&point_minus_7g_calc), 1);

        // Addition.
        let scalar_9 = from_u64<Fr>(9);
        let point_9g = scalar_mul(&generator, &scalar_9);
        let point_2g = scalar_mul(&generator, &scalar_2);
        let point_2g_calc = add(&point_minus_7g_calc, &point_9g);
        assert!(eq(&point_2g, &point_2g_calc), 1);

        // Subtraction.
        assert!(eq(&point_9g, &sub(&point_2g, &point_minus_7g_calc)), 1);
    }
```
