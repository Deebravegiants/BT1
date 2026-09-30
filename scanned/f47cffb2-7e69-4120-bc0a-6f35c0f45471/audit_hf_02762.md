# [H] Base Fee Burned For Legacy and EIP-2930 Transactions

## Summary
Severity: High
Contest weight: 0.1983
Dataset id: 15136
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the miner tip, it is adjusted to avoid burning the base fee. However, for Legacy and EIP-2930 transactions, the base fee will still be burned.
src/gas/fee.rs
```rust
pub fn effective_tip_per_gas(&self, base_fee: Option<u64>) -> Option<u128> {
    //...snipped
    let fee = max_fee_per_gas - base_fee;
    if let Some(priority_fee) = self.max_priority_fee_per_gas() {
        Some(fee.min(priority_fee) + base_fee)
    } else {
        Some(fee) // @audit Not adding back base_fee which will be burnt
    }
}
```
For Legacy and EIP-2930 transactions, self.max_priority_fee_per_gas() returns None. As a result, the else branch simply returns Some(fee), meaning the base fee is not added back to the miner tip calculation. Therefore, the base_fee ends up being burned.

## Recommendation
Add base_fee when calculating the tip for Legacy and EIP-2930 transactions.
