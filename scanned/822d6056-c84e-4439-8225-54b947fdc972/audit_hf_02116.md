# [M] Possibly Incorrect Removal Amount in Liquidity Update

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 11910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deri-V4 protocol has the essential logic in allowing users to withdraw their deposited liquidity.
While examining the logic to redeem their liquidity, we notice an issue that may incorrectly finalize the withdrawal amount.
To elaborate, we show below the code snippet from the finish_update_liquidity_internal() routine, which is used for finalizing the user request of liquidity withdrawal. The internal b0_amount_removed_asset variable keeps track of the removed assets in tokenB0 and the amount should be safe_math256::min(b_amount_to_remove, i256::as_u256(data.b0_amount)) not current safe_math256::min(b_amount_removed, i256::as_u256(data.b0_amount)) (line 1266).
```solidity
if (object::object_address(&data.b_token) == operate_token) {
    get_ex_params(&mut data, b_token_state, gateway_param);
    let transfer_out_amount = if (liquidity == 0) {
        MAX_AS_U256
    } else {
        b_amount_to_remove
    };
    let b_amount_removed = transfer_out(&mut data, gateway_param, transfer_out_amount, false);
} else {
    assert!(operate_token == object::object_address(&gateway_param.token_b0), EINVALID_OPERATE_TOKEN);
    if (i256::is_greater_than_zero(data.b0_amount)) {
        let b0_amount_removed_asset = vault::redeem(
            object::address_to_object<Vault>(gateway_param.vault0),
            safe_math256::min(b_amount_to_remove, i256::as_u256(data.b0_amount))
        );
        let b0_amount_removed = (fungible_asset::amount(&b0_amount_removed_asset) as u256);
        data.b0_amount = i256::wrapping_sub(data.b0_amount, i256::from(b0_amount_removed));
        let b_amount_to_remove_asset = fungible_asset::extract(
            &mut b0_amount_removed_asset,
            (b_amount_to_remove as u64)
        );
        primary_fungible_store::deposit(data.account, b_amount_to_remove_asset);
        let gateway_store = smart_table::borrow(&gateway_param.gateway_stores, gateway_param.token_b0);
        fungible_asset::deposit(gateway_store.store, b0_amount_removed_asset);
    }
}
```

## Recommendation
Revise the above logic to properly compute the amount for withdrawal.
