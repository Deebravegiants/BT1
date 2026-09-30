# [M] Wrong assignment ofcumulativeBid for Range-

## Summary
Severity: Medium
Contest weight: 0.6780
Dataset id: 20107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Wrong assignment of cumulativeBid for RangeOrder state. In D3Trading, the getRangeOrderState function is returning RangeOrder (get swap status for internal swap) which is assinging wrong toTokenMMInfo.cumulativeBid which suppose to be cumulativeBid not cumulativeAsk. The error lies in the assignment of roState.toTokenMMInfo.cumulativeBid. Instead of assigning tokenCumMap[toToken].cumulativeAsk, it should be assigning tokenCumMap[toToken].cumulativeBid.
File: D3Trading.sol
```solidity
roState.toTokenMMInfo.cumulativeBid =
    allFlag >> (toTokenIndex) & 1 == 0 ? 0 : tokenCumMap[toToken].cumulativeAsk;
```
This wrong assignment value definitely will mess up accounting balance, resulting unknown state will occure, which is not expected by the protocol. For one case, this getRangeOrderState is being used in querySellTokens & queryBuyTokens which may later called from sellToken and buyToken. The issue is when calling _contructTokenState which can be reverted from PMMRangeOrder when buy or sell token.
File: PMMRangeOrder.sol
```solidity
// B
tokenState.B = askOrNot ? tokenState.B0 - tokenMMInfo.cumulativeAsk : tokenState.B0 - tokenMMInfo.cumulativeBid;
```
When the tokenMMInfo.cumulativeBid (which was wrongly assign from cumulativeAsk) is bigger than tokenState.B0, this will revert. This wrong assignment value definitely will mess up accounting balance, resulting unknown state will occure, which is not expected by the protocol. For example reverting state showing a case above.

## Recommendation
Fix the error to
File: D3Trading.sol
```solidity
roState.toTokenMMInfo.cumulativeBid =
    allFlag >> (toTokenIndex) & 1 == 0 ? 0 : tokenCumMap[toToken].cumulativeBid;
```
