# [M] Wrong function signature for Convex Booster Signature Deposit

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-12-sentiment
Published: 2022-12-02
Source: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/9
Type: sherlock-finding

## Details
chainNue

medium

# Wrong function signature for Convex Booster Signature Deposit

## Summary

Wrong function signature for Convex Booster Signature Deposit

## Vulnerability Detail

In `ConvexBoosterController.sol` the function signature being used is not same as the Convex Booster implementation, resulting a failed call to the contract.

```solidity
    /// @notice deposit(uint256,uint256)
    bytes4 constant DEPOSIT = 0xe2bbb158;
```

deployed mainnet convex booster:
https://etherscan.io/address/0xf403c135812408bfbe8713b5a23a04b3d48aae31#writeContract
deposit using 0x43a0d066 

convex docs & repo:
https://docs.convexfinance.com/convexfinanceintegration/booster
[0x43a0d06](https://github.com/convex-eth/platform/blob/main/contracts/contracts/Booster.sol#L250)
```solidity
function deposit(uint256 _pid, uint256 _amount, bool _stake) public returns(bool){
...
}
```

the pull request using two argument function meanwhile the ConvexBooster is using ` deposit(uint256 _pid, uint256 _amount, bool _stake)`

## Impact

User can't call deposit for ConvexBooster


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-12-sentiment-judging/issues/9_
