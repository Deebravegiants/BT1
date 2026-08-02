No vulnerability found for this question.

**Reasoning:** The premise requires a friend module to construct `points` and `compressed_points` in separate loops from independently-ordered attacker data, but this doesn't match the actual code. In production, `new_statement` is only invoked via `StatementBuilder::build()` in [1](#0-0) , and every builder method (`add_point`, `add_points`, `add_points_cloned`) pushes the decompressed point and its compressed form from the *same* single input value in the *same* iteration step: [2](#0-1) . This design is explicitly documented as eliminating "manual parallel-vector construction that must stay in sync" [3](#0-2) .

All production callers (`sigma_protocol_registration`, `sigma_protocol_transfer`, `sigma_protocol_withdraw`, `sigma_protocol_key_rotation`) exclusively use this builder pattern to construct `Statement<P>` — none of them build `points` and `compressed_points` independently or in separate loops from attacker-supplied ciphertext components. For example, `new_transfer_statement` adds each component via `b.add_point(...)`/`b.add_points(...)` calls with the caller's compressed inputs, guaranteeing index-for-index correspondence by construction: [4](#0-3) .

Since `points[i]` is always `decompress(compressed_points[i])` by construction (never populated from a differently-ordered source), the described "reordering" attack path does not exist in this codebase — it's structurally prevented by the builder abstraction, not merely by the length check in `new_statement` ( [5](#0-4) ). No unprivileged input crosses a custody boundary here.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement_builder.move (L1-14)
```text
/// A builder for `Statement<P>` that eliminates manual parallel-vector construction.
///
/// Instead of manually maintaining two parallel vectors (`points` and `compressed_points`) that must
/// stay in sync, callers add points via builder methods that handle both vectors internally.
///
/// ## CRITICAL: Builder order must match index constants
///
/// Points must be added in exactly the order the index constants define:
/// - `IDX_H = 0` → first `add_point` call adds H
/// - `IDX_EK = 1` → second `add_point` call adds ek
/// - etc.
///
/// The `assert_*_statement_is_well_formed()` check catches size mismatches but NOT ordering mistakes.
/// The builder does NOT change the index layout.
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement_builder.move (L44-61)
```text
    /// Add a compressed point; decompresses internally. Returns the index.
    public(friend) fun add_point<P>(self: &mut StatementBuilder<P>, p: CompressedRistretto): u64 {
        let idx = self.points.length();
        self.points.push_back(p.point_decompress());
        self.compressed_points.push_back(p);
        idx
    }

    /// Add a vector of compressed points; decompresses all internally. Returns the starting index.
    public(friend) fun add_points<P>(self: &mut StatementBuilder<P>, v: &vector<CompressedRistretto>): u64 {
        let start = self.points.length();
        v.for_each_ref(|p| {
            let p_val = *p;
            self.points.push_back(p_val.point_decompress());
            self.compressed_points.push_back(p_val);
        });
        start
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement_builder.move (L84-87)
```text
    public(friend) fun build<P>(self: StatementBuilder<P>): Statement<P> {
        let StatementBuilder { points, compressed_points, scalars } = self;
        sigma_protocol_statement::new_statement(points, compressed_points, scalars)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/proofs/sigma_protocol_transfer.move (L283-296)
```text
        let b = new_builder();
        assert!(b.add_point(ristretto255::basepoint_compressed()) == IDX_G, e);                                            // G
        assert!(b.add_point(confidential_balance::get_encryption_key_basepoint_compressed()) == IDX_H, e);         // H
        assert!(b.add_point(compressed_ek_sender) == IDX_EK_SENDER, e);                                                       // ek_sender
        assert!(b.add_point(compressed_ek_recip) == IDX_EK_RECIP, e);                                                         // ek_recip
        assert!(b.add_points(compressed_old_balance.get_compressed_P()) == START_IDX_OLD_P, e);                            // old_P
        assert!(b.add_points(compressed_old_balance.get_compressed_R()) == START_IDX_OLD_P + ell, e);                      // old_R
        assert!(b.add_points(compressed_new_balance.get_compressed_P()) == START_IDX_OLD_P + 2 * ell, e); // new_P
        assert!(b.add_points(compressed_new_balance.get_compressed_R()) == START_IDX_OLD_P + 3 * ell, e);                  // new_R
        let (idx, amount_P) = b.add_points_cloned(compressed_amount.get_compressed_P());           // amount_P
        assert!(idx == START_IDX_OLD_P + 4 * ell, e);
        assert!(b.add_points(compressed_amount.get_compressed_R_sender()) == START_IDX_OLD_P + 4 * ell + n, e);            // amount_R_sender
        let (idx, recip_R) = b.add_points_cloned(compressed_amount.get_compressed_R_recip());      // amount_R_recip
        assert!(idx == START_IDX_OLD_P + 4 * ell + 2 * n, e);
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/sigma_protocols/sigma_protocol_statement.move (L35-42)
```text
    public(friend) fun new_statement<P>(
        points: vector<RistrettoPoint>,
        compressed_points: vector<CompressedRistretto>,
        scalars: vector<Scalar>
    ): Statement<P> {
        assert!(points.length() == compressed_points.length(), error::invalid_argument(E_MISMATCHED_NUMBER_OF_COMPRESSED_POINTS));
        Statement { points, compressed_points, scalars }
    }
```
