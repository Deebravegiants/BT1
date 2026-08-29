# [M] Unbounded for loops with array inputs can consume block gas limit

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-07
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/17
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x54e5d4e931b62cec0c40fa98bf4c26a548c5f5bf3f83ddf311c1514b46860048
**Severity:** medium

**Description:**
## Impact
Loss of significant gas fees for the user

## Description
Many functions through the codebase use an unbounded for loop with an array input. Most of these functions consume relatively high amounts of gas, so if a long enough input is provided by users the functions can consume the whole block gas limit which would mean a very expensive reverting transaction for the user.

### Affected functions
`contracts/Loot.sol` - `claimMultipleLoot()`
`contracts/LootCreator.sol` - `createMultipleLoot()`
`contracts/LootVoteController.sol` - `voteForManyGaugeWeights()` & `voteForManyGaugeWeightsFor()`
`contracts/MultiMerkleDistributorV2.sol` - `multiClaim()` & `claimQuest()`

Note that `view` functions with for loops are not listed, they will simply revert because they do not consume any gas as so impact is non-significant.


## Proof of Concept
1. User calls `voteForManyGaugeWeights()` with `13` `gauge` and `userPower` params.
2. Since `_voteForGauge` consumes very high amount of gas, this relatively low amount of function calls consume the whole block gas limit
3. The transaction reverts and the user has to pay large amount of gas fees for all of the transaction execution

## Recommendation
Instead of allowing to pass an arbitrary length array to these functions, consider to define a maximum allowed length (either on each function, or a general maximum) and enforce the safety length checks on the above mentioned functions. This way the user would only have to pay gas for the reverting transaction up to the length check.

```solidity
    function voteForManyGaugeWeights(address[] memory gauge, uint256[] memory userPower) external nonReentrant {
        uint256 length = gauge.length;
        if(length != userPower.length) revert Errors.ArraySizeMismatch();
+      if(length == 0 || length > MAX_VOTE_GAUGE_LENGTH) revert Errors.InvalidLength();
        for(uint256 i; i < length; i++) {
            _voteForGauge(msg.sender, gauge[i], userPower[i], msg.sender);
        }
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/17_
