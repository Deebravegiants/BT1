# [M] Lack of timelock for router fee change and total weight change in DODORouterProxy.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/22
Type: sherlock-finding

## Details
ctf_sec

medium

# Lack of timelock for router fee change and total weight change in DODORouterProxy.sol

## Summary

Lack of timelock for router fee change and total weight change

## Vulnerability Detail

In DODOApprove, we have the timelock to change the proxy address.

But we are missing the timelock when setting router fee and total weight in DODORouterProxy.sol

```solidity
function changeRouteFeeRate(uint256 newFeeRate) public onlyOwner {
    require(newFeeRate < 10**18, "DODORouteProxy: newFeeRate overflowed");
    routeFeeRate = newFeeRate;
}

function changeTotalWeight(uint256 newTotalWeight) public onlyOwner {
    require(newTotalWeight < 2 ** 8, "DODORouteProxy: totalWeight overflowed");
    totalWeight = newTotalWeight;
}
```

the admin can call the function above to modify the parameter any time.

## Impact

I think it is user that use DODO are traders and they care about trading fee charged. Changing the fee setting is crucial change because it can impact their trading decision, then it make sense to set timelock to give them time to prepare for the adjustment.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L129-L134


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/22_
