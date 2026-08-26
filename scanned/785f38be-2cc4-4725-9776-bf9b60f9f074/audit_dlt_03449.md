# [M] CompoundConnector.sol misses unclaimed rewards in getPositionTVL, resulting in undervalued positionTVL/TVL

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1228
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L130-L131


# Vulnerability details

## Impact
CompoundConnector.sol misses unclaimed rewards in getPositionTVL, resulting in undervalued positionTVL/TVL.

## Proof of Concept
CompoundV3 has reward accrual tracking for base asset suppliers, see [doc](https://docs.compound.finance/protocol-rewards/). CompoundConnector provides method to supply base assets([supply()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L29)) and also claim rewards([claimRewards()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L63)).

The problem is accumulated but unclaimed rewards will not be counted in getPositionTVL. Current CompoundConnector::getPositionTVL will only account for collateral and debt values.
```solidity
//contracts/connectors/CompoundConnector.sol
    function _getPositionTVL(
        HoldingPI memory p,
        address base
    ) public view override returns (uint256) {
...
        uint256 positiveBalance = getCollBlanace(IComet(market), false);
        uint256 negativeBalance = getBorrowBalanceInBase(IComet(market));
        uint256 balance = positiveBalance - negativeBalance; 
        //@audit this only accounts for collateral and debt value, but will miss claimable rewards in comet
|>        return (
            valueOracle.getValue(IComet(market).baseToken(), base, balance)
        );
```
(https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/CompoundConnector.sol#L130-L131)

This result in positionTVL and total [TVL()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L628) undervalued due to missed claimable rewards valuation. 

## Tools Used
Manual

## Recommended Mitigation Steps
Compound provides [getRewardOwed()](https://docs.compound.finance/protocol-rewards/#get-reward-accrued) method to query reward accrued but no yet claimed for an account. Consider using this method to add unclaimed rewards value to position TVL.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1228_
