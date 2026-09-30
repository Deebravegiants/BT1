# [M] Revisited check_b_token_consistency() Logic in gateway

## Summary
Severity: Medium
Contest weight: 0.4206
Dataset id: 11917
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For gas efficiency and code management, the gateway contract in Deri-V4 maintains a local data cache that has the common need of validating the tokenB for synchronization. While examining the related data cache validation logic, we notice an issue that should be fixed.
To elaborate, we show below the implementation of the related check_b_token_consistency() routine. As the name indicates, it is used to validate the tokenB consistency. By design, the tokenB may be changed only when the previous tokenB, if any, does not have any remaining balance. With that, the zero-balance validation should be performed on the vault associated with the previous tokenB, not current one (line 1712).
```solidity
fun check_b_token_consistency(
    d_token_state: &DTokenState,
    b_token_state: &BTokenState,
    d_token_id: u256,
    b_token: Object<Metadata>
) {
    let pre_b_token = d_token_state.b_token;
    let pre_b_token_addr = object::object_address(&pre_b_token);
    if (pre_b_token_addr != ZERO_ADDRESS && pre_b_token != b_token) {
        let vault_address = b_token_state.vault;
        let st_amount = vault::st_amounts(object::address_to_object(vault_address), d_token_id);
        assert!(st_amount == 0, EINVALID_BTOKEN);
    }
}
```

## Recommendation
Revise the above logic to properly validate the tokenB consistency.
