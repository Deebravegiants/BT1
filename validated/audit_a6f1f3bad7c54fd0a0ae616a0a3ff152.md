### Title
Hardcoded `Fee(1)` in `convert_consensus_l1_handler_to_internal_l1_handler` Ignores Actual `paid_fee_on_l1` — (File: `crates/apollo_transaction_converter/src/transaction_converter.rs`)

### Summary

`TransactionConverter::convert_consensus_l1_handler_to_internal_l1_handler` unconditionally passes `Fee(1)` as the `paid_fee_on_l1` argument when constructing the executable `L1HandlerTransaction`, discarding whatever fee was actually paid on L1. This is the direct Sequencer analog of the external `create_issuance_information` bug: a parameter that should carry a real value is silently replaced with a hardcoded constant.

### Finding Description

In `crates/apollo_transaction_converter/src/transaction_converter.rs` at lines 473–483, the validator-side conversion of a consensus L1Handler transaction to its executable form always supplies `Fee(1)`:

```rust
fn convert_consensus_l1_handler_to_internal_l1_handler(
    &self,
    tx: transaction::L1HandlerTransaction,
) -> TransactionConverterResult<executable_transaction::L1HandlerTransaction> {
    Ok(executable_transaction::L1HandlerTransaction::create(
        tx,
        &self.chain_id,
        // TODO(Gilad): Change this once we put real value in paid_fee_on_l1.
        Fee(1),
    )?)
}
``` [1](#0-0) 

This function is reached from `convert_consensus_tx_to_internal_consensus_tx` whenever the consensus layer delivers a `ConsensusTransaction::L1Handler` to the validator: [2](#0-1) 

The `ConsensusTransaction::L1Handler` variant carries only the raw `transaction::L1HandlerTransaction`, which has no `paid_fee_on_l1` field. The actual fee paid on L1 is only present in the executable form (`executable_transaction::L1HandlerTransaction`): [3](#0-2) 

The proposer, by contrast, obtains L1Handler transactions from the L1 events scraper with the real `paid_fee_on_l1` value set. The validator therefore always executes L1Handler transactions with `paid_fee_on_l1 = Fee(1)`, regardless of what was actually paid on L1.

### Impact Explanation

The blockifier's `execute_raw` for `L1HandlerTransaction` checks `paid_fee_on_l1` at lines 103–113:

```rust
let paid_fee = self.paid_fee_on_l1;
if paid_fee == Fee(0) {
    return Err(TransactionExecutionError::TransactionFeeError(Box::new(
        TransactionFeeError::InsufficientFee { paid_fee, actual_fee: receipt.fee },
    )));
}
``` [4](#0-3) 

Because the validator always supplies `Fee(1)`, this check always passes on the validator side. If the proposer receives an L1Handler transaction with `paid_fee_on_l1 = 0` (e.g., from a buggy or malicious L1 scraper, or a non-standard L1 contract), the proposer's execution returns `InsufficientFee` and rejects the transaction, while the validator's execution succeeds. This proposer/validator divergence produces different `BlockExecutionArtifacts`, different `PartialBlockHashComponents`, and ultimately a different `ProposalCommitment`, causing the `ProposalFin` comparison to fail and breaking consensus for that block. [5](#0-4) 

Additionally, the wrong `paid_fee_on_l1` is permanently bound into the executable transaction object used for all downstream processing (bouncer, state diff, receipt), meaning the fee field carried through the execution pipeline is structurally incorrect for every L1Handler transaction processed by a validator.

### Likelihood Explanation

The Ethereum Starknet core contract enforces a non-zero ETH value for `sendMessageToL2`, so `paid_fee_on_l1 = 0` is prevented in the normal production path. However, the bug is unconditional and affects every L1Handler transaction processed by a validator node. Any deviation in the L1 scraper, a non-standard deployment, or a future change to the fee check semantics (e.g., checking the actual amount rather than just non-zero) would immediately surface the divergence. The `TODO(Gilad)` comment confirms this is a known incomplete implementation.

### Recommendation

Transmit `paid_fee_on_l1` through the consensus protocol. Either:
1. Add a `paid_fee_on_l1: Fee` field to `ConsensusTransaction::L1Handler` (or a wrapper type), so the proposer can include the actual value when streaming the transaction, and the validator can use it during conversion; or
2. Have the validator look up the `paid_fee_on_l1` from its own L1 event log using the transaction's nonce and contract address before constructing the executable transaction.

Until then, replace the hardcoded `Fee(1)` with an explicit error or a clearly documented sentinel that is rejected by the fee check, so that the divergence is surfaced immediately rather than silently accepted.

### Proof of Concept

1. Proposer scrapes an L1Handler event with `paid_fee_on_l1 = 0` (e.g., injected via a test L1 contract that bypasses the fee requirement).
2. Proposer calls `execute_raw` → `paid_fee == Fee(0)` → returns `InsufficientFee` → transaction is rejected → proposer's `BlockExecutionArtifacts` excludes this transaction.
3. Proposer streams the transaction to validators via `ConsensusTransaction::L1Handler(raw_tx)`.
4. Validator calls `convert_consensus_l1_handler_to_internal_l1_handler` → `Fee(1)` is used → `paid_fee != Fee(0)` → execution succeeds → validator's `BlockExecutionArtifacts` includes this transaction.
5. Validator computes a different `PartialBlockHash` and `ProposalCommitment` than the proposer.
6. `validate_proposal` reaches the `ProposalFin` comparison: `built_block != received_fin.proposal_commitment` → `ProposalFinMismatch` → consensus round fails. [1](#0-0) [4](#0-3) [5](#0-4)

### Citations

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L197-201)
```rust
            ConsensusTransaction::L1Handler(tx) => {
                let internal_tx = self.convert_consensus_l1_handler_to_internal_l1_handler(tx)?;
                Ok((InternalConsensusTransaction::L1Handler(internal_tx), None))
            }
        }
```

**File:** crates/apollo_transaction_converter/src/transaction_converter.rs (L473-483)
```rust
    fn convert_consensus_l1_handler_to_internal_l1_handler(
        &self,
        tx: transaction::L1HandlerTransaction,
    ) -> TransactionConverterResult<executable_transaction::L1HandlerTransaction> {
        Ok(executable_transaction::L1HandlerTransaction::create(
            tx,
            &self.chain_id,
            // TODO(Gilad): Change this once we put real value in paid_fee_on_l1.
            Fee(1),
        )?)
    }
```

**File:** crates/starknet_api/src/executable_transaction.rs (L380-397)
```rust
#[derive(Clone, Debug, Default, Deserialize, Eq, PartialEq, Serialize, Hash)]
pub struct L1HandlerTransaction {
    pub tx: crate::transaction::L1HandlerTransaction,
    pub tx_hash: TransactionHash,
    pub paid_fee_on_l1: Fee,
}

impl L1HandlerTransaction {
    pub const L1_HANDLER_TYPE_NAME: &str = "L1_HANDLER";

    pub fn create(
        raw_tx: crate::transaction::L1HandlerTransaction,
        chain_id: &ChainId,
        paid_fee_on_l1: Fee,
    ) -> Result<L1HandlerTransaction, StarknetApiError> {
        let tx_hash = raw_tx.calculate_transaction_hash(chain_id, &raw_tx.version)?;
        Ok(Self { tx: raw_tx, tx_hash, paid_fee_on_l1 })
    }
```

**File:** crates/blockifier/src/transaction/l1_handler_transaction.rs (L103-113)
```rust
                        let paid_fee = self.paid_fee_on_l1;
                        // For now, assert only that any amount of fee was paid.
                        // The error message still indicates the required fee.
                        if paid_fee == Fee(0) {
                            return Err(TransactionExecutionError::TransactionFeeError(Box::new(
                                TransactionFeeError::InsufficientFee {
                                    paid_fee,
                                    actual_fee: receipt.fee,
                                },
                            )));
                        }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L244-247)
```rust
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```
