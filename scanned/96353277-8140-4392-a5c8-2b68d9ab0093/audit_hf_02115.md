# [H] Incorrect Account Cache During Margin Removal

## Summary
Severity: High
Contest weight: 0.6141
Dataset id: 11909
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Deri-V4 protocol has the built-in support of allowing traders to provide or withdraw margins. While reviewing current logic to withdraw the user margin, we notice a possible issue that uses the wrong account address for margin adjustment.
To elaborate, we show below the code snippet from the related finish_remove_margin_internal() routine. As the name indicates, this routine is designed to remove user margin. We notice the user account in current implementation is directly derived from the signing user user, which is incorrect.
The intended user account should be the owner of the given p_token_id, i.e., ptoken::owner(p_token_id) (line 1358).
```solidity
fun finish_remove_margin_internal(
    user: &signer,
    request_id: u256,
    p_token_id: u256,
    required_margin: u256,
    cumulative_pnl_on_engine: I256,
    b_amount_to_remove: u256
) acquires GatewayStorage, GatewayParam {
    let user_addr = signer::address_of(user);
    let gateway_storage = borrow_global_mut<GatewayStorage>(@deri);
    let gateway_param = borrow_global<GatewayParam>(@deri);
    let d_token_state = smart_table::borrow_mut(&mut gateway_storage.d_token_states, p_token_id);
    let b_token = d_token_state.b_token;
    let b_token_state = smart_table::borrow(&gateway_storage.b_token_states, object::object_address(&b_token));
    check_request_id(d_token_state, request_id);
    let data = get_data_and_check_b_token_consistency(
        &gateway_storage.gateway_state,
        b_token_state,
        d_token_state,
        ptoken::owner(p_token_id),
        p_token_id,
        b_token
    );
}
```

## Recommendation
Properly revise the above routine to ensure the correct user account address is used.
