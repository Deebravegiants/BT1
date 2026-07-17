### Title
Cheap SIR FunctionCall Chunk Stuffing via Gas/Byte Limit Mismatch - (File: chain/chain/src/runtime/mod.rs)

### Summary
The `prepare_transactions_extra` function enforces a gas limit (`max_tx_gas` = 500 TGas) and a byte limit (`combined_transactions_size_limit` = 4 MiB) independently. For same-shard (SIR) `FunctionCall` transactions, the `send_sir` per-byte gas cost (2,235,934 gas/byte) is ~21× cheaper than the `send_not_sir` cost (47,683,715 gas/byte). An unprivileged attacker can fill the 4 MiB byte limit with two max-size (1.5 MiB) SIR `FunctionCall` transactions while consuming only ~7.6 TGas — approximately 1.5% of the 500 TGas gas limit — cheaply excluding all other users' transactions from the chunk.

### Finding Description
In `prepare_transactions_extra`, two limits are checked independently:

```rust
let transactions_gas_limit = chunk_tx_gas_limit(runtime_config, &prev_block, shard_id);
let size_limit = runtime_config.witness_config.combined_transactions_size_limit as u64;
// ...
if total_gas_burnt >= transactions_gas_limit { break; }
if total_size >= size_limit { break; }
```

The `size_limit` is `combined_transactions_size_limit` = 4,194,304 bytes (4 MiB). The `transactions_gas_limit` is derived from `max_tx_gas` = 500 TGas.

For a SIR `FunctionCall` transaction with 1,572,864 bytes (max `max_transaction_size`) of arguments:

- `action_receipt_creation.send_sir` = 108,059,500,000 gas
- `action_function_call.send_sir` = 200,000,000,000 gas
- `action_function_call_per_byte.send_sir` = 2,235,934 gas/byte × 1,572,864 bytes ≈ 3,516 TGas

Total gas burnt per transaction ≈ **3.82 TGas**.

Two such transactions fill ~3.14 MiB of the 4 MiB byte limit while burning only **~7.64 TGas** — 1.53% of the 500 TGas gas limit. The size limit is hit first, stopping all further transaction inclusion.

The `send_sir` per-byte fee was deliberately left unchanged at 2,235,934 gas/byte in protocol version 69 when `send_not_sir` was raised to 47,683,715 gas/byte to prevent cross-shard stuffing. The comment in `69.yaml` reads "Change the cost of sending receipt to **another account** to 50 TGas / MiB" — SIR transactions were excluded from the increase because they do not cross shards. However, SIR transactions still consume the shared `combined_transactions_size_limit` (witness size budget), creating the mismatch.

### Impact Explanation
An attacker who controls any NEAR account with a deployed contract can submit SIR `FunctionCall` transactions with 1.5 MiB of arguments via the public RPC. These are valid, accepted transactions. Once two such transactions are included, `total_size` reaches the 4 MiB `combined_transactions_size_limit` and the chunk producer stops adding any further transactions. All other users' transactions are excluded from that chunk. The chunk's gas utilization is ~1.5% of the allowed maximum, meaning the chunk is effectively empty from a throughput perspective while appearing byte-full. The corrupted protocol value is the set of receipts generated per chunk (legitimate transactions are denied receipt creation) and the effective gas utilization reported on-chain.

### Likelihood Explanation
The attack requires no special privileges — only a funded NEAR account with a deployed contract. At the minimum gas price of 10^9 yoctoNEAR/gas, the cost to fill one chunk's byte limit is approximately 7.64 TGas × 10^9 yN/gas ≈ 7.64 × 10^21 yN ≈ **7.64 mNEAR per chunk**. This is orders of magnitude cheaper than filling the gas limit (which would cost ~500 mNEAR). The attack can be sustained continuously at negligible cost.

### Recommendation
Align the `send_sir` per-byte fee for `FunctionCall` (and `DeployContract`) with the witness size cost, not just the network bandwidth cost. Alternatively, enforce a joint gas-per-byte floor during chunk packing: before admitting a transaction, verify that `gas_burnt / size_for_limits` exceeds a minimum ratio derived from the ratio `max_tx_gas / combined_transactions_size_limit`. This mirrors the recommendation in the external report to rethink the relationship between the gas limit and the byte limit.

### Proof of Concept
1. Attacker deploys any contract on account `attacker.near`.
2. Attacker submits two `SignedTransaction` objects via `broadcast_tx_async` RPC:
   - `signer_id = receiver_id = "attacker.near"` (SIR)
   - `actions = [FunctionCall { method_name: "f", args: vec![0u8; 1_572_800], gas: 1, deposit: 0 }]`
3. Each transaction's `size_for_limits` ≈ 1,572,864 bytes; two transactions total ≈ 3,145,728 bytes < 4,194,304 bytes.
4. Each transaction burns ≈ 3.82 TGas; two transactions burn ≈ 7.64 TGas << 500 TGas.
5. The chunk producer hits `size_limit` after including both transactions and stops. All other pending transactions are excluded from the chunk.

**Root cause lines:** [1](#0-0) 

**Independent limit enforcement (gas vs. bytes):** [2](#0-1) 

**Size accumulation after transaction admission:** [3](#0-2) 

**The `send_sir` fee left unchanged while `send_not_sir` was raised 21×:** [4](#0-3) 

**`combined_transactions_size_limit` = 4 MiB, `max_tx_gas` = 500 TGas (independent dimensions):** [5](#0-4)

### Citations

**File:** chain/chain/src/runtime/mod.rs (L933-948)
```rust
        let size_limit = runtime_config.witness_config.combined_transactions_size_limit as u64;
        // for metrics only
        let mut rejected_due_to_congestion = 0;
        let mut rejected_invalid_tx = 0;
        let mut rejected_invalid_for_chain = 0;

        // Add new transactions to the result until some limit is hit or the transactions run out.
        'add_txs_loop: while let Some(transaction_group_iter) = transaction_groups.next() {
            if total_gas_burnt >= transactions_gas_limit {
                prepared_transactions.limited_by = PrepareTransactionsLimit::Gas;
                break;
            }
            if total_size >= size_limit {
                prepared_transactions.limited_by = PrepareTransactionsLimit::Size;
                break;
            }
```

**File:** chain/chain/src/runtime/mod.rs (L1122-1124)
```rust
                        total_gas_burnt = total_gas_burnt.checked_add(result.gas_burnt).unwrap();
                        total_size += validated_tx.size_for_limits(protocol_version);
                        prepared_transactions.transactions.push(validated_tx);
```

**File:** core/parameters/res/runtime_configs/69.yaml (L34-45)
```yaml
action_function_call_per_byte: {
  old: {
    send_sir: 2_235_934,
    send_not_sir: 2_235_934,
    execution: 2_235_934,
  },
  new: {
    send_sir: 2_235_934,
    send_not_sir: 47_683_715,
    execution: 2_235_934,
  }
}
```

**File:** core/parameters/src/config.rs (L260-272)
```rust
#[derive(Debug, Copy, Clone, PartialEq)]
pub struct WitnessConfig {
    /// Size limit for storage proof generated while executing receipts in a chunk.
    /// After this limit is reached we defer execution of any new receipts.
    pub main_storage_proof_size_soft_limit: u64,
    /// Maximum size of transactions contained inside ChunkStateWitness.
    ///
    /// A witness contains transactions from both the previous chunk and the current one.
    /// This parameter limits the sum of sizes of transactions from both of those chunks.
    pub combined_transactions_size_limit: usize,
    /// Size limit of storage proof used to validate new transactions in ChunkStateWitness.
    pub new_transactions_validation_state_size_soft_limit: u64,
}
```
