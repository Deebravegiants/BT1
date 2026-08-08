### Title
Precompile signature verification (secp256k1/ed25519/secp256r1) is priced with a flat per-signature cost while the actual verification work is unmetered and scales with attacker-controlled message length - ([File: cost-model/src/block_cost_limits.rs])

### Summary
The Megapot report shows a bug class where a computation's real cost scales with an attacker/user-controllable parameter (`bonusballMax`) that is not reflected in the fixed cost accounting used to bound the operation, allowing actual execution work to blow past the enforced external limit. Agave has a structurally similar mismatch in how it prices native precompile signature-verification instructions (`secp256k1`, `ed25519`, `secp256r1`): the cost model charges a fixed compute-unit amount per declared signature, but the real verification cost (elliptic-curve recovery/Ed25519 check plus hashing) is a function of the message length referenced by each signature, and this work happens entirely outside the metered SVM compute budget.

### Finding Description
The cost model prices precompile instructions using flat per-signature constants that do not depend on the message size being verified: [1](#0-0) 

These constants are applied purely based on the declared `num_signatures` byte extracted from instruction data, via `get_precompile_signature_details`/`get_num_signatures_in_instruction`, which just reads `data[0]` as the count — with no reference to any per-signature message size: [2](#0-1) [3](#0-2) 

Critically, precompile verification is not executed against the SVM's metered compute budget at all. A dedicated test confirms that a precompiled instruction consumes 0 units from the CU-meter, and its entire allocated builtin cost is refunded as "adjustment": [4](#0-3) 

The actual verification routines (`agave_precompiles::secp256k1::verify` and `agave_precompiles::ed25519::verify`) loop over `count`/`num_signatures` (up to 255, a `u8`), and for each one, extract a `message` slice using an attacker-supplied `message_data_offset`/`message_data_size` (a `u16`, up to 65535) which can point into *any other instruction's data in the same transaction* — not just the precompile instruction's own data: [5](#0-4) [6](#0-5) 

Each iteration performs a keccak-256 hash (secp256k1) or Ed25519 `verify_strict` (ed25519) over the referenced message and an EC point recovery/scalar verification — real CPU work whose cost scales with message length and signature count, exactly as the project's own benchmarks demonstrate (cost at 32 bytes vs 32KB vs `u16::MAX` message length): [7](#0-6) [8](#0-7) 

Because the cost model only charges `SECP256K1_VERIFY_COST`/`ED25519_VERIFY_STRICT_COST` per signature (flat 6,690 / 2,400 CU regardless of message size) and this cost is not deducted from — nor bounded by — the actual metered compute budget of the transaction, an attacker can construct a transaction with multiple precompile instructions, each declaring up to 255 signatures whose offsets reuse the largest available instruction data blob in the transaction, to make the real, unmetered CPU cost of `verify_precompiles` disproportionately larger than what the transaction "declares"/pays for via the cost model. This is the same root-cause pattern as the Megapot finding: work whose magnitude is attacker-controlled is priced with a cost function that ignores the dominant scaling factor (message size), and the actual computation is performed in a code path that is not gated by the same limit used to admit/schedule the transaction.

### Impact Explanation
Precompile verification runs during transaction sanitization/verification, ahead of (and independent from) the SVM compute meter that would otherwise abort overlong SBF execution. Because this work is unmetered and underpriced relative to its true cost, a leader packing many such transactions into a block, or a validator replaying them, spends CPU time not reflected in the block's accounted cost-model budget (`MAX_BLOCK_UNITS`), which is the mechanism used to bound how much work a block can require in a fixed slot time. This risks disproportionate/underpriced execution and can push actual per-block or per-transaction processing time beyond what the cost accounting assumes, similarly to how the Megapot bonusball loop caused actual gas usage to exceed the externally-imposed transaction gas ceiling that the cost estimate was supposed to respect.

### Likelihood Explanation
Any unprivileged user can submit ordinary transactions containing `secp256k1_program`/`ed25519_program`/`secp256r1_program` instructions; declaring the maximum `num_signatures` (255) and pointing `message_instruction_index`/`message_data_offset`/`message_data_size` at another large instruction's data within the same transaction requires no special privileges, only careful transaction construction, and is straightforward to reproduce using the project's own precompile instruction builders and benchmarks as a template.

### Recommendation
Price precompile signature verification proportionally to the actual message bytes hashed/verified per signature (not just a flat per-signature constant), and/or account this cost against the same metered budget (or an equivalent hard cap) that governs SBF execution, so that the cost model's estimate cannot diverge from the real CPU cost incurred during `verify_precompiles`.

### Proof of Concept
Not executed in this analysis (index-only investigation); the report is based on tracing the constant per-signature pricing in `cost-model/src/block_cost_limits.rs` and `cost-model/src/cost_model.rs::get_signature_cost` against the true message-length-dependent verification loops in `precompiles/src/secp256k1.rs::verify` and `precompiles/src/ed25519.rs::verify`, combined with the test in `core/tests/scheduler_cost_adjustment.rs::test_builtin_ix_precompiled` confirming that precompile execution consumes 0 units from the SVM compute meter. A concrete PoC would need to be built and benchmarked against a running validator/bank harness (e.g., using `precompiles/benches/secp256k1_instructions.rs`/`ed25519_instructions.rs` as a starting point) to quantify the wall-clock/CPU divergence versus the charged cost-model units, which was not performed here due to the read-only nature of this investigation.

### Citations

**File:** cost-model/src/block_cost_limits.rs (L9-16)
```rust
/// Number of compute units for one signature verification.
pub const SIGNATURE_COST: u64 = COMPUTE_UNIT_TO_US_RATIO * 24;
/// Number of compute units for one secp256k1 signature verification.
pub const SECP256K1_VERIFY_COST: u64 = COMPUTE_UNIT_TO_US_RATIO * 223;
/// Number of compute units for one ed25519 strict signature verification.
pub const ED25519_VERIFY_STRICT_COST: u64 = COMPUTE_UNIT_TO_US_RATIO * 80;
/// Number of compute units for one secp256r1 signature verification.
pub const SECP256R1_VERIFY_COST: u64 = COMPUTE_UNIT_TO_US_RATIO * 160;
```

**File:** runtime-transaction/src/signature_details.rs (L60-74)
```rust
/// Get transaction signature details.
pub fn get_precompile_signature_details<'a>(
    instructions: impl Iterator<Item = (&'a Pubkey, SVMInstruction<'a>)>,
) -> PrecompileSignatureDetails {
    let mut builder = PrecompileSignatureDetailsBuilder::default();
    for (program_id, instruction) in instructions {
        builder.process_instruction(program_id, &instruction);
    }
    builder.build()
}

#[inline]
fn get_num_signatures_in_instruction(instruction: &SVMInstruction) -> u64 {
    u64::from(instruction.data.first().copied().unwrap_or(0))
}
```

**File:** cost-model/src/cost_model.rs (L129-151)
```rust
    /// Returns signature details and the total signature cost
    fn get_signature_cost(transaction: &impl TransactionMeta) -> u64 {
        let signatures_count_detail = transaction.signature_details();

        signatures_count_detail
            .num_transaction_signatures()
            .saturating_mul(SIGNATURE_COST)
            .saturating_add(
                signatures_count_detail
                    .num_secp256k1_instruction_signatures()
                    .saturating_mul(SECP256K1_VERIFY_COST),
            )
            .saturating_add(
                signatures_count_detail
                    .num_ed25519_instruction_signatures()
                    .saturating_mul(ED25519_VERIFY_STRICT_COST),
            )
            .saturating_add(
                signatures_count_detail
                    .num_secp256r1_instruction_signatures()
                    .saturating_mul(SECP256R1_VERIFY_COST),
            )
    }
```

**File:** core/tests/scheduler_cost_adjustment.rs (L381-402)
```rust
#[test]
fn test_builtin_ix_precompiled() {
    let mut test_setup = TestSetup::new();

    // single precompiled instruction
    // Cost model & Compute budget: reserve/allocate default CU for one builtin ix
    // VM Execution: consume 0 from CU-meter
    // Result: adjustment = 3_000
    let expected = TestResult {
        cost_adjustment: MAX_BUILTIN_ALLOCATION_COMPUTE_UNIT_LIMIT as i64,
        execution_status: Ok(()),
    };
    assert_eq!(
        expected,
        test_setup.execute_test_transaction(&[Instruction::new_with_bincode(
            secp256k1_program::id(),
            &[0u8],
            // Add a dummy account to generate a unique transaction
            vec![AccountMeta::new_readonly(Pubkey::new_unique(), false)]
        )],)
    );
}
```

**File:** precompiles/src/secp256k1.rs (L44-96)
```rust
    for i in 0..count {
        let start = i
            .saturating_mul(SIGNATURE_OFFSETS_SERIALIZED_SIZE)
            .saturating_add(1);
        let end = start.saturating_add(SIGNATURE_OFFSETS_SERIALIZED_SIZE);

        let offsets: SecpSignatureOffsets = bincode::deserialize(&data[start..end])
            .map_err(|_| PrecompileError::InvalidSignature)?;

        // Parse out signature
        let signature_index = offsets.signature_instruction_index as usize;
        if signature_index >= instruction_datas.len() {
            return Err(PrecompileError::InvalidInstructionDataSize);
        }
        let signature_instruction = instruction_datas[signature_index];
        let sig_start = offsets.signature_offset as usize;
        let sig_end = sig_start.saturating_add(SIGNATURE_SERIALIZED_SIZE);
        if sig_end >= signature_instruction.len() {
            return Err(PrecompileError::InvalidSignature);
        }

        let signature = libsecp256k1::Signature::parse_standard_slice(
            &signature_instruction[sig_start..sig_end],
        )
        .map_err(|_| PrecompileError::InvalidSignature)?;

        let recovery_id = libsecp256k1::RecoveryId::parse(signature_instruction[sig_end])
            .map_err(|_| PrecompileError::InvalidRecoveryId)?;

        // Parse out pubkey
        let eth_address_slice = get_data_slice(
            instruction_datas,
            offsets.eth_address_instruction_index,
            offsets.eth_address_offset,
            HASHED_PUBKEY_SERIALIZED_SIZE,
        )?;

        // Parse out message
        let message_slice = get_data_slice(
            instruction_datas,
            offsets.message_instruction_index,
            offsets.message_data_offset,
            offsets.message_data_size as usize,
        )?;

        let message_hash: [u8; 32] = solana_keccak_hasher::hash(message_slice).to_bytes();
        let pubkey = libsecp256k1::recover(
            &libsecp256k1::Message::parse_slice(&message_hash).unwrap(),
            &signature,
            &recovery_id,
        )
        .map_err(|_| PrecompileError::InvalidSignature)?;
        let eth_address = eth_address_from_pubkey(&pubkey.serialize()[1..].try_into().unwrap());
```

**File:** precompiles/src/ed25519.rs (L30-76)
```rust
    for i in 0..num_signatures {
        let start = i
            .saturating_mul(SIGNATURE_OFFSETS_SERIALIZED_SIZE)
            .saturating_add(SIGNATURE_OFFSETS_START);

        // SAFETY:
        // - data[start..] is guaranteed to be >= size of Ed25519SignatureOffsets
        // - Ed25519SignatureOffsets is a POD type, so we can safely read it as an unaligned struct
        let offsets = unsafe {
            core::ptr::read_unaligned(data.as_ptr().add(start) as *const Ed25519SignatureOffsets)
        };

        // Parse out signature
        let signature = get_data_slice(
            data,
            instruction_datas,
            offsets.signature_instruction_index,
            offsets.signature_offset,
            SIGNATURE_SERIALIZED_SIZE,
        )?;

        let signature =
            Signature::from_bytes(signature).map_err(|_| PrecompileError::InvalidSignature)?;

        // Parse out pubkey
        let pubkey = get_data_slice(
            data,
            instruction_datas,
            offsets.public_key_instruction_index,
            offsets.public_key_offset,
            PUBKEY_SERIALIZED_SIZE,
        )?;

        let publickey = ed25519_dalek::PublicKey::from_bytes(pubkey)
            .map_err(|_| PrecompileError::InvalidPublicKey)?;

        // Parse out message
        let message = get_data_slice(
            data,
            instruction_datas,
            offsets.message_instruction_index,
            offsets.message_data_offset,
            offsets.message_data_size as usize,
        )?;
        publickey
            .verify_strict(message, &signature)
            .map_err(|_| PrecompileError::InvalidSignature)?;
```

**File:** precompiles/benches/secp256k1_instructions.rs (L43-86)
```rust
#[bench]
fn bench_secp256k1_len_032(b: &mut Bencher) {
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(32);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}

#[bench]
fn bench_secp256k1_len_256(b: &mut Bencher) {
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(256);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}

#[bench]
fn bench_secp256k1_len_32k(b: &mut Bencher) {
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(32 * 1024);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}

#[bench]
fn bench_secp256k1_len_max(b: &mut Bencher) {
    let required_extra_space = 113_u16; // len for pubkey, sig, and offsets
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(u16::MAX - required_extra_space);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}
```

**File:** precompiles/benches/ed25519_instructions.rs (L33-76)
```rust
#[bench]
fn bench_ed25519_len_032(b: &mut Bencher) {
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(32);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}

#[bench]
fn bench_ed25519_len_128(b: &mut Bencher) {
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(128);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}

#[bench]
fn bench_ed25519_len_32k(b: &mut Bencher) {
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(32 * 1024);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}

#[bench]
fn bench_ed25519_len_max(b: &mut Bencher) {
    let required_extra_space = 113_u16; // len for pubkey, sig, and offsets
    let feature_set = FeatureSet::all_enabled();
    let ixs = create_test_instructions(u16::MAX - required_extra_space);
    let mut ix_iter = ixs.iter().cycle();
    b.iter(|| {
        let instruction = ix_iter.next().unwrap();
        verify(&instruction.data, &[&instruction.data], &feature_set).unwrap();
    });
}
```
