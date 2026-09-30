# [M] Potential Underflow For tierId

## Summary
Severity: Medium
Contest weight: 0.4326
Dataset id: 11857
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, a tax is charged on selling DARK token. To support different tax tiers, the token contract defines two arrays (taxTiersTwaps[] and taxTiersRates[]) and a helper routine (_updateTaxRate()) to update tax rate automatically. To illustrate, we show below the _updateTaxRate() helper routine. This helper routine is internally used to update tax by the price of DARK. Specifically, it is called in every single transferFrom() operation.
```solidity
function _updateTaxRate(uint256 _darkPrice) internal returns (uint256) {
    if (autoCalculateTax) {
        for (uint8 tierId = uint8(getTaxTiersTwapsCount()).sub(1); tierId >= 0; tierId--) {
            if (_darkPrice >= taxTiersTwaps[tierId]) {
                require(taxTiersRates[tierId] < 10000, "tax equal or bigger to 100%");
                taxRate = taxTiersRates[tierId];
                return taxTiersRates[tierId];
            }
        }
    }
}
```
The analysis with the above helper routine shows there is a loop from the end to the start of the taxTiersTwaps[] array to find who is the first slot that has a value smaller than _darkPrice. The above algorithm works on the assumption that at least taxTiersTwaps[0] will be smaller than or equal to _darkPrice so the loop could stop when tierId equals to 0. However, there is no guarantee that the operation of --tierId will not cause underflow and lead to an infinite loop, which finally cause a revert transaction in every single transferFrom() operation.

## Recommendation
Apply the SafeMath to block unintended underflow.
