No vulnerability found for this question.

**Analysis:**

`new_secret_witness` simply wraps whatever vector is passed into `Witness { w }` without reordering, and `new_proof_from_bytes` builds `resp_sigma` via `sigma_protocol_utils::deserialize_scalars`, which maps `scalars_bytes` element-by-element preserving index order [1](#0-0) [2](#0-1) . So yes, ordering is preserved exactly as submitted — but that is not itself a vulnerability, because the sigma protocol's *algebraic verification equation* — not the labeling of indices — is what enforces correctness.

`psi` always reads witness scalars at the fixed hardcoded positions `IDX_DK=0`, `IDX_DELTA=1`, `IDX_DELTA_INV=2`, and both the prover (during `sigma_protocol::prove`) and verifier (`sigma_protocol::verify`/`verify_slow`) apply this *same* fixed mapping consistently [3](#0-2) . There is no separate "labeling" step where an attacker could confuse which index means what — index 0 is *defined* to be `dk`'s slot for every proof, always.

If an attacker swaps two scalars in the raw `sigma_proto_resp` bytes before submission (e.g. swapping what was meant for `IDX_DK` into `IDX_DELTA`'s slot), the on-chain verifier recomputes `psi_sigma = psi(stmt, &proof.response_to_witness())` using the *tampered* vector and checks it against `A + e·f(X)` via a multi-scalar-multiplication identity check [4](#0-3) . Because `A` was computed by the honest prover using correctly-ordered randomness `alpha` and response `sigma = alpha + e·w` was derived from the correctly-ordered witness `w`, swapping two entries of `sigma` breaks the linear relation `A[i] + e·f(X)[i] = psi(sigma)[i]` for the affected output rows (`dk·ek`, `delta·ek`, `delta_inv·new_ek`) with overwhelming probability — this is exactly the completeness/soundness property a discrete-log-based sigma protocol is designed to guarantee. The check would only accidentally pass if `dk == delta` in the underlying secret field, which is a negligible-probability coincidence not controllable by an attacker who doesn't already know the decryption key relationship, and even then wouldn't let them "change `ek`" without satisfying the genuine algebraic relation, since `f(X)` (built from the actual statement's `ek`/`new_ek`/`H` points) must still match.

There is no mechanism by which `get(IDX_DK)` could be fed a value "meant for" `IDX_DELTA` while still passing verification, because verification checks all three (plus per-chunk) equations jointly and atomically via a single MSM-based zero check [5](#0-4) , and `assert_key_rotation_statement_is_well_formed` plus `assert!(w.length() == 3, ...)` in `psi` prevent any structural mismatch that would let a subset of equations be silently skipped [6](#0-5) . This is guarded by proof soundness, not by any ordering convention that could be subverted through byte manipulation — the review does not identify a custody-boundary crossing here.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_utils.move (L60-62)
```text
    public(friend) fun deserialize_scalars(scalars_bytes: vector<vector<u8>>): vector<Scalar> {
        scalars_bytes.map(|scalar_bytes| new_scalar_from_bytes(scalar_bytes).extract())
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_witness.move (L26-26)
```text
    public(friend) fun new_secret_witness(w: vector<Scalar>): Witness { Witness { w } }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move (L235-253)
```text
    fun psi(_stmt: &Statement<KeyRotation>, w: &Witness): RepresentationVec {
        // WARNING: Crucial for security
        assert_key_rotation_statement_is_well_formed(_stmt);
        // WARNING: Crucial for security
        assert!(w.length() == 3, e_wrong_witness_len());

        let dk = *w.get(IDX_DK);
        let delta = *w.get(IDX_DELTA);
        let delta_inv = *w.get(IDX_DELTA_INV);

        // Build the representation vector
        let reprs = vector[
            // dk * ek
            repr_scaled(IDX_EK, dk),
            // delta * ek
            repr_scaled(IDX_EK, delta),
            // delta_inv * new_ek
            repr_scaled(IDX_EK_NEW, delta_inv),
        ];
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol.move (L150-209)
```text
    public(friend) inline fun verify<P>(
        dst: DomainSeparator,
        psi: Homomorphism<P>,
        f: TransformationFunction<P>,
        stmt: &Statement<P>,
        proof: &Proof,
    ): bool {
        // Step 1: Fiat-Shamir transform on `(dst, (psi, f), stmt)` to derive the random challenge `e`
        let _A = proof.get_commitment();
        let m = _A.length();
        let (e, betas) = fiat_shamir(dst, stmt, proof.get_compressed_commitment(),
            proof.get_response(), proof.get_response_length());

        // Step 2:
        let psi_sigma = psi(stmt, &proof.response_to_witness());
        let efx = f(stmt);

        assert!(m == psi_sigma.length(), error::invalid_argument(E_PROOF_COMMITMENT_WRONG_LEN));
        assert!(m == efx.length(), error::invalid_argument(E_PROOF_COMMITMENT_WRONG_LEN));

        // "Scale" all the representations in `f(stmt)` by `e`. (Implicit assumption here is that `f` is homomorphic:
        // i.e., `e f(X) = f(eX)`, which holds because our `f`'s are a `RepresentationVec`.)
        efx.scale_all(&e);

        // "Scale" the `i`th reprentation in `efx` by `\beta[i]`
        efx.scale_each(&betas);

        // "Scale" the `i`th reprentation in `\psi` by `-\beta[i]`
        // TODO(Perf): I think this could be sub-optimal: we will redo the same \beta[i] \sigma[j] multiplication several times
        //   when a `RepresentationVec`'s row reuses \sigma[j].
        psi_sigma.scale_each(&neg_scalars(&betas));

        // We start with an empty MSM: \sum_{i \in m} 0
        // ...and extend it to: \sum_{i \in [m]} A[i]^{\beta[i]}
        //                                          ^^^^^^^^^^^^^^^
        let bases = points_clone(_A);
        let scalars = betas;

        // These asserts will only fail when we have mis-implemented the cloning of `A` above
        assert!(bases.length() == m, error::internal(E_INTERNAL_INVARIANT_FAILED));
        assert!(scalars.length() == m, error::internal(E_INTERNAL_INVARIANT_FAILED));

        // Extend MSM to: be \sum_{i \in [m]} A[i]^\beta[i] + \beta[i] ( e f(stmt)[i] )
        //                                                    ^^^^^^^^^^^^^^^^^^^^^^^^^
        efx.for_each_ref(|repr| {
            bases.append(repr.to_points(stmt));
            scalars.append(*repr.get_scalars());
        });

        // Extend MSM to: be \sum_{i \in [m]} A[i]^\beta[i] + \beta[i] ( e f(stmt)[i] ) - \beta[i] (\psi(\sigma)[i])
        //                                                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^
        psi_sigma.for_each_ref(|repr| {
            bases.append(repr.to_points(stmt));
            scalars.append(*repr.get_scalars());
        });

        // TODO(Perf): Could combine exponents for shared bases more aggresively? Or does the MSM code do it implicitly?

        // Do the MSM and check it equals the (zero) identity
        multi_scalar_mul(&bases, &scalars).point_equals(&point_identity())
```
