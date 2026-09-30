# [M] Arithmetic Underflow Avoidance in gateway

## Summary
Severity: Medium
Contest weight: 0.4408
Dataset id: 11907
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Deri-V4 protocol allows users to flexibly manage their liquidity and margin. While reviewing current logic to remove the user liquidity, we notice the calculation to compute the remaining liquidity has a potential risk that may result in arithmetic underflow.
To elaborate, we show below the related get_d_token_liquidity_with_remove_b0() routine. As the name indicates, this routine is designed to calculate the liquidity if the given bAmount in bToken is removed.
In particular, the internal variable b0_total is computed by directly making use of the arithmetic operation (lines 1871-1875), which should be guarded for possible overflows and underflows. While the overflow case is highly unlikely, the underflow case (line 1874) remains possible.
```solidity
fun get_d_token_liquidity_with_remove_b0(
    self: &Data,
    gateway_param: &GatewayParam,
    b0_amount_to_remove: u256
): u256 {
    let b_amount_in_vault =
        vault::get_balance(object::address_to_object<Vault>(self.vault), self.d_token_id);
    let b0_value_of_b_amount_in_vault =
        b_amount_in_vault * self.b_price / UONE * self.collateral_factor / UONE;
    let b0_total =
        if (!i256::is_neg(self.b0_amount)) {
            b0_value_of_b_amount_in_vault + i256::as_u256(self.b0_amount)
        } else {
            b0_value_of_b_amount_in_vault - i256::abs_u256(self.b0_amount)
        };
    if (b0_total > b0_amount_to_remove) {
        let decimals_b0 = fungible_asset::decimals(gateway_param.token_b0);
        safe_math256::rescale(b0_total - b0_amount_to_remove, decimals_b0, SCALE_DECIMALS)
    } else { 0 }
}
```

## Recommendation
Properly revise the above routine to ensure the arithmetic overflow/underflow risk is completely eliminated.
