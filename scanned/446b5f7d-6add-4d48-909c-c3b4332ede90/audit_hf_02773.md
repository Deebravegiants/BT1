# [H] Peg-Out Amount Lacks Validation

## Summary
Severity: High
Contest weight: 0.2918
Dataset id: 15151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lack of validation of amount in the btc-server peg-out signing process allows the coordinator to drain the multisig wallet holding the locked Bitcoin.
In the validate_psbt_by_output() function, the amount parameter from the PegoutData is not being validated.
crates/consensus/authority/src/utils.rs
```rust
/// Validate psbt contains the correct output
pub fn validate_psbt_by_output(
    psbt: &Psbt,
    destination: &Address,
    _amount: Amount,
    //@audit amount is not being validated
)
```
A malicious coordinator can exploit this vulnerability to drain locked Bitcoin in L1. The attack vector works as follows:
1. The coordinator performs a burn() action for a very small amount in the minting contract, triggering the peg-out flow.
2. Later, they craft a malicious PSBT (Partially Signed Bitcoin Transaction) which includes the pegoutId corresponding to the previous burn() action but modifies the peg-out amount to an unrealistically large value.
3. Since the validation function does not check the amount parameter, the validation will be successful and the signing process will be completed.
4. This allows the coordinator to drain the multisig wallet holding the locked Bitcoin.
The impact is rated as high as it allows the coordinator to drain the BTC tokens. The likelihood is rated as medium as the coordinator is required to perform the attack.

## Recommendation
Ensure the PegoutData.Amount is properly validated.
