# [M] Setting totalWeight to 0 will make `dodoMutliSwap()` unusable

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/35
Type: sherlock-finding

## Details
8olidity

medium

# Setting totalWeight to 0 will make `dodoMutliSwap()` unusable

## Summary
Setting totalWeight to 0 will make `dodoMutliSwap()` unusable
## Vulnerability Detail
To set a limit on `totalweight`, less than 256 must be required to qualify. So it can be set to 0
```solidity
    function changeTotalWeight(uint256 newTotalWeight) public onlyOwner {
        require(newTotalWeight < 2 ** 8, "DODORouteProxy: totalWeight overflowed");
        totalWeight = newTotalWeight;
    }
```

But in `_multiSwap()` the value of `totalWeight` is used as the denominator, but if it is 0 then the error of dividing by 0 occurs. Failure to swap

```solidity
    function _multiSwap(
        address[] memory midToken,
        uint256[] memory splitNumber,
        bytes[] memory swapSequence,
        address[] memory assetFrom
    ) internal {

            uint256 curTotalWeight = totalWeight;
                if (assetFrom[i - 1] == address(this)) {
                    uint256 curAmount = curTotalAmount * curPoolInfo.weight / curTotalWeight;
```

## Impact
Setting totalWeight to 0 will make `dodoMutliSwap()` unusable
## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L142
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L416
## Tool used

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/35_
