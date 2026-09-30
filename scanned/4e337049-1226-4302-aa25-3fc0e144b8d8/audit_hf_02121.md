# [H] Incorrect transfer_out() Logic in gateway

## Summary
Severity: High
Contest weight: 0.6356
Dataset id: 11919
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Deri-V4 protocol allows users to deposit supported assets and get in return the share to represent the vault pool ownership. While examining the logic to redeem their shares, we notice an issue that may incorrectly compute the amount for withdrawal.
To elaborate, we show below the code snippet from the transfer_out() routine, which is used for participating users to withdraw their liquidity or margins. The issue occurs when the vault has an insufficient balance, which results in the minting of IOU tokens. When IOU tokens are minted, the data.b0_amount state needs to be computed as data.b0_amount = i256::sub(data.b0_amount, i256::add(i256::from(b0_out), i256::from(iou_amount))), not current data.b0_amount = i256::sub(data.b0_amount, i256::from(iou_amount)) (line 2055).
```solidity
if (amount > 0) {
    let b0_out;
    if (amount > b0_amount_in) {
        // Redeem B0 tokens from vault0
        let b0_redeemed_fungible_asset = vault::redeem(
            object::address_to_object<Vault>(gateway_param.vault0),
            amount - b0_amount_in
        );
        let b0_redeemed = (fungible_asset::amount(&b0_redeemed_fungible_asset) as u256);
        fungible_asset::deposit(
            get_gateway_store(gateway_param, gateway_param.token_b0).store,
            b0_redeemed_fungible_asset
        );
        if (b0_redeemed < amount - b0_amount_in) {
            // b0 insufficient
            if (is_td) {
                // Issue IOU for trader when B0 insufficient
                iou_amount = amount - b0_amount_in - b0_redeemed;
            } else {
                // Revert for Lp when B0 insufficient
                abort error::aborted(EINSUFFICIENT_B0_BALANCE);
            }
        }
        b0_out = b0_amount_in + b0_redeemed;
        b0_amount_in = 0;
    } else {
        b0_out = amount;
        b0_amount_in = b0_amount_in - amount;
    }
    b0_amount_out = b0_out;
    data.b0_amount = i256::sub(data.b0_amount, i256::from(b0_out + iou_amount));
}
```

## Recommendation
Revise the above logic to properly compute the amount for withdrawal.
