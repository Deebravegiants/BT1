# [M] Improper request_add_margin_b0() Logic in gateway

## Summary
Severity: Medium
Contest weight: 0.4298
Dataset id: 11916
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deri-V4 protocol also has the essential needs in allowing users to add margin for their positions. While examining the logic to add user margin in tokenB0, we notice an issue that may deposit into the wrong vault.
To elaborate, we show below the implementation of the affected request_add_margin_b0() routine. As the name indicates, this routine is used to top up the margin for a user position. With that, the user funds need to be deposited into the intended vault with credit to d_token_id = 0, not current p_token_id (line 969).
```solidity
public entry fun request_add_margin_b0(
    user: &signer,
    p_token_id: u256,
    b0_amount: u256
) acquires GatewayParam, GatewayStorage {
    let user_addr = signer::address_of(user);
    assert!(b0_amount > 0, EINVALID_BTOKEN_AMOUNT);
    check_p_token_id_owner(p_token_id, user_addr);
    let gateway_storage = borrow_global_mut<GatewayStorage>(@deri);
    let gateway_param = borrow_global<GatewayParam>(@deri);
    let token_b0 = gateway_param.token_b0;
    let b0_asset = primary_fungible_store::withdraw(user, token_b0, (b0_amount as u64));
    vault::deposit(
        object::address_to_object(gateway_param.vault0),
        0,
        b0_asset
    );
    let d_token_state = smart_table::borrow_mut(&mut gateway_storage.d_token_states, p_token_id);
    d_token_state.b0_amount = i256::wrapping_add(d_token_state.b0_amount, i256::from(b0_amount));
}
```

## Recommendation
Revise the above logic to properly deposit into the intended vault.
