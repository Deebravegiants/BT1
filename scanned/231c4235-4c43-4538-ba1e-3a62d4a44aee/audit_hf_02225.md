# [M] Improper Logic of Exchanger::calculateAmountAfterSettlement()

## Summary
Severity: Medium
Contest weight: 0.4483
Dataset id: 12284
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Horizon protocol has a key Exchanger contract that makes use of the pooled collateral model and allows users to perform conversions between synths directly, avoiding the need for counterparties. As a result, this mechanism solves the liquidity and slippage issues experienced by DEXs. While examining one helper routine calculateAmountAfterSettlement(), we notice its logic can be improved. To elaborate, we show below the related calculateAmountAfterSettlement() implementation. As the name indicates, this routine calculates the balance of a synth after the settlement. Note the settlement may result in extra funds being reclaimed or refunded. And the reclaimed or refunded amount will be reflected in the token balance of the give from account. With that, the addition of possible refunded needs to be added to amountAfterSettlement before the resulting sum is compared with the current balance in balanceOfSourceAfterSettlement.

```solidity
function calculateAmountAfterSettlement(address from, bytes32 currencyKey, uint amount, uint refunded) public view returns (uint amountAfterSettlement) {
    amountAfterSettlement = amount;
    // balance of a synth will show an amount after settlement
    uint balanceOfSourceAfterSettlement = IERC20(address(issuer().synths(currencyKey))).balanceOf(from);
    // when there isn't enough supply (either due to reclamation settlement because the number is too high)
    if (amountAfterSettlement > balanceOfSourceAfterSettlement) {
        // then the amount to exchange reduced to their remaining supply
        amountAfterSettlement = balanceOfSourceAfterSettlement;
        if (refunded > 0) {
            amountAfterSettlement = amountAfterSettlement.add(refunded);
        }
    }
}
```

## Recommendation
Revisit the above logic to properly calculate the synth amount after the settlement to properly account for possible synth reclamation and refund.
