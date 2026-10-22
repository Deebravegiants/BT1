# [M] Improper MaxTP Increase Position Creation in OrderManager

## Summary
Severity: Medium
Contest weight: 0.4239
Dataset id: 12427
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the LogX protocol has a built-in OrderManager contract to manager user orders. While reviewing the order creation process, we notice the current implementation has attached a maxTP order to limit possible max profit. However, the current approach to compute associated take-profit price should be improved. In the following, we show the code snippet of the related getTPPrice() routine. This routine is used to compute the take-profit price to meet the maxProfitMultiplier requirement. However, it comes to our attention that profitDelta should be computed as (_maxTPAmount * markPrice * getMinPrice(collateralToken))/(sizeDelta * 10**vault.tokenDecimals(collateralToken)), not current (_maxTPAmount * markPrice * 10**(30 - vault.tokenDecimals(collateralToken)))/sizeDelta (line 828).
```solidity
function getTPPrice(uint256 sizeDelta, bool isLong, uint256 markPrice, uint256 _maxTPAmount, address collateralToken) view public returns(uint256) {
    uint256 profitDelta = (_maxTPAmount * markPrice * 10**(30 - vault.tokenDecimals(collateralToken)))/sizeDelta;
    if(isLong){
        return markPrice + profitDelta;
    }
    return markPrice - profitDelta;
}
```
Moreover, the maxTP order should be instantiated with the parameter _isLong, not using the hardcoded true (line 354).

## Recommendation
Revise the above routine to properly manage the attached maxTP order.
