# [M] Collateral Calculation Rounding Down Allows Persistence of Dust Trades

## Summary
Severity: Medium
Contest weight: 0.6967
Dataset id: 11163
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OstiumTrading smart contract exhibits an issue in its collateral calculation mechanism during the trade closure process, specifically within the closeTradeMarket() function of the OstiumTrading contract and the corresponding closeTradeMarketCallback() function in the OstiumTradingCallbacks contract. This issue arises from the way collateral is calculated and rounded, leading to unintended bypassing of essential leverage checks. In the OstiumTrading::closeTradeMarket() function, the calculation of remainingCollateral is performed using the following line of code:  
```solidity
uint256 remainingCollateral = t.collateral * (100e2 - closePercentage) / 100e2;
```  
When a trade is initiated with a closePercentage near to 100%, for example, 99.99% (represented as 9999 in the contract) and a collateral amount of for example 5,500 units, the computation proceeds as follows:  
```solidity
remainingCollateral = 5500 * (10000 - 9999) / 10000 = 5500 * 1 / 10000 = 0
```  
Due to Solidity's integer division, remainingCollateral truncates to zero. This outcome erroneously bypasses the subsequent conditional check intended to ensure that the remaining collateral maintains a minimum leveraged position:  
```solidity
if (
    remainingCollateral > 0
    && remainingCollateral * t.leverage / 100
    < IOstiumPairsStorage(registry.getContractAddress('pairsStorage')).pairMinLevPos(pairIndex)
) {
    revert BelowMinLevPos();
}
```  
Since remainingCollateral is zero, the condition evaluates to false, allowing the trade to proceed without satisfying the minimum leverage requirement. This flaw is further exacerbated in the OstiumTradingCallbacks::closeTradeMarketCallback() function, where collateralToClose is calculated as follows:  
```solidity
uint256 collateralToClose = t.collateral * closePercentage / 100e2;
// Substituting the example values:
collateralToClose = 5500 * 9999 / 10000 = 5499
```  
This results in a remainingCollateral of 1 unit (i.e., 5,500 - 5,499), effectively creating a dust trade. Although such minimal collateral may appear inconsequential and unlikely to pose significant operational risks, it disrupts the contract's invariant by leaving a position smaller than the mandated minimum. Over time, the accumulation of these dust trades could undermine the system's integrity and reliability, potentially leading to unforeseen vulnerabilities and inconsistencies within the trading platform.

## Recommendation
To address this vulnerability, it is recommended to modify the conditional check within the OstiumTrading::closeTradeMarket() function. The condition should be adjusted to ensure that the remainingCollateral is only subjected to the minimum leveraged position check if the closePercentage is not equal to 100%. This adjustment prevents scenarios where a high closePercentage, such as 99.99%, inadvertently results in a zero remainingCollateral, thereby maintaining the contract's integrity. The revised condition can be implemented as follows:  
```solidity
if (
    closePercentage != 100e2
    && remainingCollateral * t.leverage / 100
    < pairMinLevPos(pairIndex)
) {
    revert BelowMinLevPos();
}
```
