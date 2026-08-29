# [M] contract unavailability attack

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/62
Type: sherlock-finding

## Details
bin2chen

medium

# contract unavailability attack

## Summary
It is possible to construct a huge "pointsPerShare" when the contract has not yet been deposited, leading to subsequent deposit overflows

## Vulnerability Detail

At the beginning, there are no shares.
Assume:
1.depositToken's decimal = 18
2.rewardToken's decimal = 18
3. if User_A calls deposit( amount = 1) ,after totalShare = 2 (very small)
4. and User_A calls distributeRewards(_amount= 1e18), which is 1 token (because decimal = 18)
5. At this point
pointsPerShare = _amount * POINTS_MULTIPLIER / shares
pointsPerShare = 1e18 * type(uint128).max / 2
pointsPerShare = 170141183460469231731687303715884105727500000000000000000

Thus, when the user deposit(), only 680 tokens can be deposit , and then the larger will overflow
type(uint256).max / (pointsPerShare * 1e18) = 680 (tokens)

## Impact
Contracts not working properly

## Code Snippet
https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/base/AbstractRewards.sol#L96

```solidity
 function _distributeRewards(uint256 _amount) internal {
....

    if (_amount > 0) {
      pointsPerShare = pointsPerShare + (_amount * POINTS_MULTIPLIER / shares); /*** when shares very small , pointsPerShare wil huge***/
      emit RewardsDistributed(msg.sender, _amount);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/62_
