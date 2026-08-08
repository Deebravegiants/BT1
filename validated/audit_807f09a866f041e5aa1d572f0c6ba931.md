Based on the codebase, the premise of this question is invalidated by an existing hard transaction-size gate.

### Analysis

`ed25519::verify` in [1](#0-0)  does perform `verify_strict` over an attacker-controlled `message` slice, and `get_data_slice` in [2](#0-1)  allows `message_instruction_index == u16::MAX` to self-reference the precompile instruction's own `data` buffer, with `offset_start`/`size` bounded only by `instruction.len()`. In isolation this looks like it could allow `message_data_size` up to `u16::MAX`.

However, the entire serialized transaction (including this precompile instruction's `data`) is size-gated well below 65535 bytes before any precompile verification occurs. `Bank::verify_transaction_with_serialized_message` enforces: [3](#0-2) 

This caps legacy/v0 transactions at `PACKET_DATA_SIZE` (1232 bytes) and v1 transactions at `solana_message::v1::MAX_TRANSACTION_SIZE` (4096 bytes), confirmed by [4](#0-3)  and [5](#0-4) . Since `verify_if_precompile`/`ed25519::verify` runs on this already-size-checked transaction, `data.len()` (and hence `offsets.message_data_offset + message_data_size` for a `u16::MAX` self-reference) can never approach `u16::MAX`; it's capped at 4096 bytes max.

Consequently, even with `num_signatures = 255` (which itself consumes `255 * 14 + 2 = 3572` bytes of the 4096-byte v1 budget just for offset headers, leaving only ~524 bytes for all pubkey/signature/message data combined), the worst-case total `Sha512` input across all 255 iterations is on the order of ~130KB per instruction (with maximal overlap reuse), not `255 * 65535 ≈ 16.7MB` as hypothesized. This is far closer to what `ED25519_VERIFY_STRICT_COST * 255 = 2400 * 255 = 612,000` CU (cost-model/src/block_cost_limits.rs:14 and cost-model/src/cost_model.rs:142-145) is intended to bound, and is not a case of cost being "message-size-independent" in any exploitable sense — the message size itself is tightly bounded by the transaction size gate, not by the precompile logic.

#No vulnerability found for this question.

### Citations

**File:** precompiles/src/ed25519.rs (L66-79)
```rust
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
    }
    Ok(())
}
```

**File:** precompiles/src/ed25519.rs (L81-105)
```rust
fn get_data_slice<'a>(
    data: &'a [u8],
    instruction_datas: &'a [&[u8]],
    instruction_index: u16,
    offset_start: u16,
    size: usize,
) -> Result<&'a [u8], PrecompileError> {
    let instruction = if instruction_index == u16::MAX {
        data
    } else {
        let signature_index = instruction_index as usize;
        if signature_index >= instruction_datas.len() {
            return Err(PrecompileError::InvalidDataOffsets);
        }
        instruction_datas[signature_index]
    };

    let start = offset_start as usize;
    let end = start.saturating_add(size);
    if end > instruction.len() {
        return Err(PrecompileError::InvalidDataOffsets);
    }

    Ok(&instruction[start..end])
}
```

**File:** runtime/src/bank.rs (L5535-5549)
```rust
        let max_transaction_size = match tx.version() {
            TransactionVersion::Number(1) if enable_tx_v1 => {
                solana_message::v1::MAX_TRANSACTION_SIZE
            }
            _ => PACKET_DATA_SIZE,
        } as u64;

        // WARNING: Any pending features added here most likely must also be checked in
        //          `Bank::resanitize_transaction_minimally`.
        let sanitized_tx = {
            let size =
                wincode::serialized_size(&tx).map_err(|_| TransactionError::SanitizeFailure)?;
            if size > max_transaction_size {
                return Err(TransactionError::SanitizeFailure);
            }
```

**File:** runtime/src/bank/tests.rs (L9393-9439)
```rust
#[test]
fn test_verify_transactions_packet_data_size() {
    let GenesisConfigInfo { genesis_config, .. } =
        create_genesis_config_with_leader(42, &solana_pubkey::new_rand(), 42);
    let bank = Bank::new_for_tests(&genesis_config);

    let recent_blockhash = Hash::new_unique();
    let keypair = Keypair::new();
    let pubkey = keypair.pubkey();
    let make_transaction = |size| {
        let ixs: Vec<_> = std::iter::repeat_with(|| {
            system_instruction::transfer(&pubkey, &Pubkey::new_unique(), 1)
        })
        .take(size)
        .collect();
        let message = Message::new(&ixs[..], Some(&pubkey));
        Transaction::new(&[&keypair], message, recent_blockhash)
    };
    // Small transaction.
    {
        let tx = make_transaction(5);
        assert!(bincode::serialized_size(&tx).unwrap() <= PACKET_DATA_SIZE as u64);
        assert!(
            bank.verify_transaction(tx.into(), TransactionVerificationMode::FullVerification)
                .is_ok(),
        );
    }
    // Big transaction.
    {
        let tx = make_transaction(25);
        assert!(bincode::serialized_size(&tx).unwrap() > PACKET_DATA_SIZE as u64);
        assert_matches!(
            bank.verify_transaction(tx.into(), TransactionVerificationMode::FullVerification),
            Err(TransactionError::SanitizeFailure)
        );
    }
    // Assert that verify fails as soon as serialized
    // size exceeds packet data size.
    for size in 1..30 {
        let tx = make_transaction(size);
        assert_eq!(
            bincode::serialized_size(&tx).unwrap() <= PACKET_DATA_SIZE as u64,
            bank.verify_transaction(tx.into(), TransactionVerificationMode::FullVerification)
                .is_ok(),
        );
    }
}
```

**File:** rpc/src/rpc.rs (L4390-4396)
```rust
// Base58 encoding is deprecated, not increased for v1 transactions
const MAX_BASE58_SIZE: usize = 1683; // Golden, bump if PACKET_DATA_SIZE changes
// Cap base64 based on the largest supported transaction version,
// which is v1 (4096 bytes).
const MAX_BASE64_SIZE: usize = 5464; // ceil(4096 / 3) * 4
// Legacy/v0 transactions are still capped at PACKET_DATA_SIZE (1232 bytes).
const MAX_BASE64_LEGACY_SIZE: usize = 1644; // ceil(1232 / 3) * 4
```
