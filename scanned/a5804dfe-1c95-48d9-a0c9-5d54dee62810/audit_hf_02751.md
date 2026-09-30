# [C] transaction.value Is Used To Refund Invalid Burns

## Summary
Severity: Critical
Contest weight: 0.2638
Dataset id: 15106
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user may set a transaction value diﬀerent to the amount attached to burn() to refund excess BTC tokens during a peg-out. If a burn() operation is deemed invalid, for example if metadata has the wrong format, the user is refunded their burned amount. However, this amount is set to transaction.value which is not always equal to the amount that was burned. An attacker can call a smart contract and attach a large value to the transaction to inﬂate the transaction value. If the contract then calls burn() with only a small value and invalid data such that the proof fails, the user will be refunded the entire transaction value without having to burn those funds. The impact and likelihood are rated as high as arbitrary attackers may exploit this vulnerability to mint an unbounded amount of tokens. ```rust
let pegout_amount = transaction.value(); // @audit set `pegout_amount` to transaction.value' rather than burnt amount
MintContractError::InvalidPegoutData(_) => {
    Self::increment_balance_by_address(
        *sender,
        EthersU256::from_little_endian(pegout_amount.as_le_slice()), // @audit refunds `pegout_amount`'
        &mut state,
```

## Recommendation
To mitigate the issue refund the actual amount that was burned instead of the transaction value.
