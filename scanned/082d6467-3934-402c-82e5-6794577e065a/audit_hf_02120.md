# [M] Improved Liquidity Addition Logic in gateway

## Summary
Severity: Medium
Contest weight: 0.5906
Dataset id: 11918
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deri-V4 protocol has the built-in support of allowing LPs to provide funds into vaults for rewards.
And LP share is accounted inside each individual vault. While reviewing current logic of minting and redeeming LP share, we notice a possible issue in a corner case when handling the native coin addition (e.g., SupraCoin).
To elaborate, we show below the code snippet from the related request_add_liquidity() routine. As the name indicates, this routine is designed to add liquidity into the protocol vault in exchange for possible gains and rewards. When the user indicates the underlying asset amount in the native coin, the respective b_amount is always equal to request_add_liquidity_fee, which is incorrect. In fact, we need to withdraw request_add_liquidity_fee + b_amount, instead of request_add_liquidity_fee (line 842). Moreover, we need to avoid withdrawing from the user-specific primary_fungible_store (line 855) when the underlying asset amount is in the native coin.
```solidity
let apt_fee_asset = coin_wrapper::wrap(coin::withdraw<SupraCoin>(user, (request_add_liquidity_fee as u64)));
let apt_amount = receive_execution_fee(
    d_token_state,
    gateway_state,
    gateway_param,
    request_add_liquidity_fee,
    apt_fee_asset
);
if (get_aptos_coin_wrapper() == b_token) {
    b_amount = apt_amount;
    assert!(b_amount != 0, EINVALID_BTOKEN_AMOUNT);
    let b_token_asset = primary_fungible_store::withdraw(user, b_token, (b_amount as u64));
    deposit(&mut data, b_token_asset, gateway_param);
}
get_ex_params(&mut data, b_token_state, gateway_param);
```

## Recommendation
Properly revise the above routine to ensure the native coin addition as liquidity is properly supported. An example (incomplete) revision of the above code snippet is shown as below:
```solidity
let apt_amount = if (get_aptos_coin_wrapper() == b_token) {
    receive_execution_fee + b_amount
} else { receive_execution_fee };
let apt_fee_asset = coin_wrapper::wrap(coin::withdraw<SupraCoin>(user, (apt_amount as u64)));
receive_execution_fee(
    d_token_state,
    gateway_state,
    gateway_param,
    request_add_liquidity_fee,
    apt_fee_asset
);
assert!(b_amount != 0, EINVALID_BTOKEN_AMOUNT);
if (get_aptos_coin_wrapper() != b_token) {
    let b_token_asset = primary_fungible_store::withdraw(user, b_token, (b_amount as u64));
    deposit(&mut data, b_token_asset, gateway_param);
} else {
    /// TODO - deposit remaining native coins as well
}
get_ex_params(&mut data, b_token_state, gateway_param);
```
