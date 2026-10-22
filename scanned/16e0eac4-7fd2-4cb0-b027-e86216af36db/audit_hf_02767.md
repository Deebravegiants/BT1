# [C] Peg-In Proofs Are Only Verified For Top-level Calls

## Summary
Severity: Critical
Contest weight: 0.2783
Dataset id: 15145
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the execute_state_transitions() function botanix_mint_contract_checks() is called to ensure any call that was made to the minting contract has a valid peg-in proof. If a peg-in proof is deemed invalid the balance of the receiver is decremented again. However, botanix_mint_contract_checks() is only called if transaction.to() is equal to the minting contract. This means that if the call to mint() is not the top-level call, for example if a smart contract calls mint(), the peg-in proof is never verified.
The impact and likelihood is rated a high as it allows an arbitrary user to mint BTC without a valid peg-in proof.
crates/ethereum/evm/src/execute.rs
```rust
for (sender, transaction) in block.transactions_with_sender() {
    if result.is_success() && transaction.to() == Some(*MINT_CONTRACT_ADDRESS) {
        match self.botanix_mint_contract_checks(
            &result,
            &botanix_consensus_pkg,
            transaction.hash,
            provider.clone(),
        )
```
In a similar vein, calls to burn() that are not the top-level call will not be picked up by botanix_mint_contract_checks(). The result is users will have their BTC stuck in the minting contract without tokens being released on Bitcoin L1.

## Recommendation
To resolve the issue, check each Mint() and Burn() event emitted by the minting contract regardless of the original destination of the transaction.
