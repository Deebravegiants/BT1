# [C] Invalid Proof Causes Early Return For Multiple Calls To mint()

## Summary
Severity: Critical
Contest weight: 0.3757
Dataset id: 15109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When multiple calls to mint() occur in a single transaction only one error is processed. A user may call mint() multiple times in the same transaction, for example by using a multicall smart contract. When these calls are veriﬁed in botanix_mint_contract_checks(), every mint operation will have their proofs veriﬁed iteratively. However, if a proof is deemed invalid an early return may occur, meaning that subsequent proofs are not veriﬁed. ```rust
/// Performs additional checks on mint contract transactions.
fn botanix_mint_contract_checks(
    &self,
    result: &ExecutionResult,
    botanix_consensus_pkg: &BotanixConsensusPackage,
    tx_hash: TxHash,
    provider: ProviderFactory<RethDB>,
) -> Result<(Vec<PeginData>, Vec<PegoutWithId>), MintContractError> {
    let consensus_pkg = botanix_consensus_pkg;
    let btc_network = consensus_pkg.btc_network;
    // Check pegins.
    let mut pegins = vec![];
    let mut pegouts = vec![];
    for log in result.logs() {
        let pegin_data = match try_parse_mint_event(log)? {
            None => continue,
            Some(p) => p,
        };
        // ... snipped
        // the pegin height must be equal or less than the required block depth (checkpoint)
        if pegin_data.bitcoin_block_height > bitcoin_checkpoint.1 {
            return Err(MintContractError::InvalidPeginData { // @audit example of early return
                error: format!(
                    "pegin height {} greater than checkpoint of {}",
                    pegin_data.bitcoin_block_height, bitcoin_checkpoint.1,
                ),
                revert_address: pegin_data.account,
                revert_amount: pegin_data.amount,
            });
        }
        // ... snipped
    }
    // ... snipped
}
```
The impact is that, the receiver's balance is only decremented for the proofs that were checked and failed, any balances from proofs that were not checked are not decremented. An attacker may exploit this by calling mint() twice or more in a single transaction with invalid proofs. Only the ﬁrst proof will be marked as invalid and the attacker can mint free BTC during the subsequent calls. Macbeth Review

## Recommendation
All events from a single transaction should be validated and balances adjusted accordingly.
