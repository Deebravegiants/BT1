## Answer

No vulnerability found for this question.

`to_points` in [1](#0-0)  maps each `point_idxs` entry through `stmt.get_point(idx)`, and `get_point` in [2](#0-1)  performs `&self.points[i]`, which is Move's native vector-index operator. This operator is a VM-level bounds check that aborts deterministically (`EINDEX_OUT_OF_BOUNDS`) on an out-of-range index — it never silently substitutes a default or wrong `RistrettoPoint`. So the first premise of the question (a "silently wrong" point) does not hold at all; any OOB access is a hard abort, which is the safe failure mode.

More importantly, in the key-rotation protocol the `point_idxs` used inside `psi`/`f` are never attacker-supplied. They are hardcoded/derived constants (`IDX_H`, `IDX_EK`, `IDX_EK_NEW`, `START_IDX_OLD_R + i`) computed from `get_num_available_chunks()`, as seen in [3](#0-2)  and [4](#0-3) . The `Statement<KeyRotation>` itself is only ever constructed via `new_key_rotation_statement`, which builds the point vector to always contain exactly `3 + 2 * get_num_available_chunks()` points and then calls `assert_key_rotation_statement_is_well_formed` to check `stmt.get_points().length() == 3 + 2 * get_num_available_chunks()` — see [5](#0-4)  and the well-formedness check itself at [6](#0-5) .

`assert_verifies` calls `assert_key_rotation_statement_is_well_formed(stmt)` before invoking `psi`/`f` via `sigma_protocol::verify` ( [7](#0-6) ), and `psi` itself re-asserts well-formedness as its first line ( [8](#0-7) ). Since the same `ell = get_num_available_chunks()` value governs both the statement's point-vector length and the indices referenced by `psi`/`f`, there is no way for an unprivileged caller to get a `Statement<KeyRotation>` into the pipeline with fewer points than the indices used by `psi`/`f` reference — the `StatementBuilder` (`new_builder`, `add_point`/`add_points`) is the only way to build a `Statement`, and its friend-only visibility restricts construction to these protocol modules with fixed, self-consistent layouts.

So neither half of the proposed attack holds: (1) an OOB `point_idxs` entry would abort rather than silently substitute a wrong point, and (2) there is no attacker-reachable path to construct a `Statement<KeyRotation>` whose `points` vector is shorter than what `psi`/`f`'s hardcoded indices require, since well-formedness is asserted before verification and the index scheme is derived from the same chunk count used to size the statement.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_representation.move (L53-55)
```text
    public(friend) fun to_points<P>(self: &Representation, stmt: &Statement<P>): vector<RistrettoPoint> {
        self.point_idxs.map(|idx| stmt.get_point(idx).point_clone())
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement.move (L45-47)
```text
    public(friend) fun get_point<P>(self: &Statement<P>, i: u64): &RistrettoPoint {
        &self.points[i]
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move (L167-172)
```text
    fun assert_key_rotation_statement_is_well_formed(
        stmt: &Statement<KeyRotation>,
    ) {
        assert!(stmt.get_points().length() == 3 + 2 * get_num_available_chunks(), e_wrong_num_points());
        assert!(stmt.get_scalars().length() == 0, e_wrong_num_scalars());
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move (L196-212)
```text
    public(friend) fun new_key_rotation_statement(
        compressed_ek: CompressedRistretto,
        compressed_new_ek: CompressedRistretto,
        compressed_old_R: &vector<CompressedRistretto>,
        compressed_new_R: &vector<CompressedRistretto>,
    ): Statement<KeyRotation> {
        let err = error::internal(E_STATEMENT_BUILDER_INCONSISTENCY);
        let b = new_builder();
        assert!(b.add_point(get_encryption_key_basepoint_compressed()) == IDX_H, err);                  // H
        assert!(b.add_point(compressed_ek) == IDX_EK, err);                                                // ek
        assert!(b.add_point(compressed_new_ek) == IDX_EK_NEW, err);                                        // new_ek
        assert!(b.add_points(compressed_old_R) == START_IDX_OLD_R, err);                                   // old_R
        assert!(b.add_points(compressed_new_R) == START_IDX_OLD_R + get_num_available_chunks(), err);      // new_R
        let stmt = b.build();
        assert_key_rotation_statement_is_well_formed(&stmt);
        stmt
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move (L235-264)
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

        // delta * old_R_i for each chunk
        let ell = get_num_available_chunks();
        reprs.append(vector::range(0, ell).map(|i|
            repr_scaled(START_IDX_OLD_R + i, delta)
        ));

        // WARNING: Crucial for security
        assert!(reprs.length() == 3 + ell, e_wrong_output_len());
        new_representation_vec(reprs)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move (L277-302)
```text
    fun f(_stmt: &Statement<KeyRotation>): RepresentationVec {
        // WARNING: We do not re-assert the stmt is well-formed anymore here, since wherever the transformation function
        // is called, so is the homomorphism, so the check will be done.

        let ell = get_num_available_chunks();
        let idx_r_new_start = get_start_idx_for_new_R();

        let reprs = vector[
            // H
            repr_point(IDX_H),
            // new_ek
            repr_point(IDX_EK_NEW),
            // ek
            repr_point(IDX_EK),
        ];

        // new_R_i for each chunk
        reprs.append(vector::range(0, ell).map(|i|
            repr_point(idx_r_new_start + i)
        ));

        // Note: Not needed for security, since a mismatched f(X) length will be caught in the verifier. But good practice
        // for catching mistakes *early* when implementing your f(X).
        assert!(reprs.length() == 3 + ell, e_wrong_output_len());
        new_representation_vec(reprs)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_key_rotation.move (L305-317)
```text
    public(friend) fun assert_verifies(self: &KeyRotationSession, stmt: &Statement<KeyRotation>, proof: &Proof) {
        assert_key_rotation_statement_is_well_formed(stmt);

        let success = sigma_protocol::verify(
            new_domain_separator(@aptos_framework, chain_id::get(), PROTOCOL_ID, bcs::to_bytes(self)),
            |_X, w| psi(_X, w),
            |_X| f(_X),
            stmt,
            proof
        );

        assert!(success, error::invalid_argument(E_INVALID_KEY_ROTATION_PROOF));
    }
```
