# [H] Liquidation of PartyA will fail due to underflow

## Summary
Severity: High
Contest weight: 0.7928
Dataset id: 20167
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidation of PartyA will fail due to underflow errors. As a result, assets will be stuck, and there will be a loss of assets for the counterparty (the creditor) since they cannot receive the liquidated assets.
ontracts/facets/liquidation/LiquidationFacetImpl.sol#L126
File: LiquidationFacetImpl.sol
```solidity
function liquidatePositionsPartyA(
    address partyA,
    uint256[] memory quoteIds
) internal returns (bool) {
    // ...SNIP...
    (bool hasMadeProfit, uint256 amount) = LibQuote.getValueOfQuoteForPartyA(
        accountLayout.symbolsPrices[partyA][quote.symbolId].price,
        LibQuote.quoteOpenAmount(quote),
        quote
    );
    // ...SNIP...
    if (
        accountLayout.liquidationDetails[partyA].liquidationType == LiquidationType.NORMAL
    ) {
        accountLayout.partyBAllocatedBalances[quote.partyB][partyA] += quote.lockedValues.cva;
        if (hasMadeProfit) {
            accountLayout.partyBAllocatedBalances[quote.partyB][partyA] -= amount;
        } else {
            accountLayout.partyBAllocatedBalances[quote.partyB][partyA] += amount;
        }
    } else if (
        accountLayout.liquidationDetails[partyA].liquidationType == LiquidationType.LATE
    ) {
        accountLayout.partyBAllocatedBalances[quote.partyB][partyA] += quote.lockedValues.cva - ((quote.lockedValues.cva * accountLayout.liquidationDetails[partyA].deficit) / accountLayout.lockedBalances[partyA].cva);
        if (hasMadeProfit) {
            accountLayout.partyBAllocatedBalances[quote.partyB][partyA] -= amount;
        } else {
            accountLayout.partyBAllocatedBalances[quote.partyB][partyA] += amount;
        }
    } else if (
        accountLayout.liquidationDetails[partyA].liquidationType == LiquidationType.OVERDUE
    ) {
        if (hasMadeProfit) {
            accountLayout.partyBAllocatedBalances[quote.partyB][partyA] -= amount;
        } else {
            accountLayout.partyBAllocatedBalances[quote.partyB][partyA] += amount - ((amount * accountLayout.liquidationDetails[partyA].deficit) / uint256(-accountLayout.liquidationDetails[partyA].totalUnrealizedLoss));
        }
    }
```
Assume that at this point, the allocated balance of PartyB (accountLayout.partyBAllocatedBalances[quote.partyB][partyA]) only has 1000 USD.
In Line 152 above, the getValueOfQuoteForPartyA function is called to compute the PnL of a position. Assume the position has a huge profit of 3000 USD due to a sudden spike in price. For this particular position, PartyA will profit 3000 USD while PartyB will lose 3000 USD.
In this case, 3000 USD needs to be deducted from PartyB's account. However, when the `accountLayout.partyBAllocatedBalances[quote.partyB][partyA] -= amount;` code at Line 170, 182, or 190 gets executed, an underflow error will occur, and the transaction will revert. This is because partyBAllocatedBalances is an unsigned integer, and PartyB only has 1000 USD of allocated balance, but the code attempts to deduct 3000 USD.
Liquidation of PartyA will fail. Since liquidation cannot be completed, the assets that are liable to be liquidated cannot be transferred from PartyA (the debtor) to the counterparty (the creditor). Assets will be stuck, and there will be a loss of assets for the counterparty (the creditor) since they cannot receive the liquidated assets.

## Recommendation
Consider implementing the following fixes to ensure that the amount to be deducted will never exceed the allocated balance of PartyB to prevent underflow errors from occurring.
```solidity
if (hasMadeProfit) {
    uint256 amountToDeduct = amount > accountLayout.partyBAllocatedBalances[quote.partyB][partyA] ? accountLayout.partyBAllocatedBalances[quote.partyB][partyA] : amount;
    accountLayout.partyBAllocatedBalances[quote.partyB][partyA] -= amountToDeduct;
} else {
    accountLayout.partyBAllocatedBalances[quote.partyB][partyA] += amount;
}
```
