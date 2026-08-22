# [M] Auctions run at significantly different speeds for different prize tiers

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-21
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/15
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L76-L78
https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L136
https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L262-L264
https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L223-L250
https://github.com/GenerationSoftware/pt-v5-claimer/blob/main/src/Claimer.sol#L289


# Vulnerability details

## Comments

The V5 implementation delegates the task of claiming prizes to a network of claimers. The fees received by a claimer are calculated based on a dutch auction and limited based on the prize size of the highest tier (the smallest prize). As a result, it is possible that the gas price could exceed the fee received by claimers, leading to prizes not being claimed. If any high value prizes happen to be drawn during this period then they will go unclaimed.

## Mitigation

The new implementation only computes the max fee size based on the prize tier that is being claimed for. As a result the fees received by claimers are now larger for larger prize tiers, thereby incentivising lower tiers (i.e. those with higher prizes) to be claimed first and resulting in more fees paid to claimers.

## New issue

Because all the tiers run on the same auction, each auction will now run at a completely different speed

## Impact
If the `_maximumFee` parameter specified in the constructor is relatively small, then the max fee for the lower prize tiers (higher prizes) will never be reached anyway. If the `_maximumFee` is relatively large to give sufficient range for the auctions, the auctions for higher tiers (lower prizes) will ramp up very quickly to the max limit based on the prize tier. The real impact of this is that auctions are now running inefficiently, where fees are likely to be higher than they could be for the higher tiers (i.e. the bots are getting more fees than they would be willing to accept).

## Proof of Concept
Based on the updated implementation, the maximum fee to be paid is now a function of the tier being claimed for, not the total number of active tiers:

```
  function _computeMaxFee(uint8 _tier) internal view returns (uint256) {
    return UD60x18.unwrap(maxFeePortionOfPrize.intoUD60x18().mul(UD60x18.wrap(prizePool.getTierPrizeSize(_tier))));
  }
```

The return value of this call is used as the first parameter for calls to `_computeFeePerClaim` and in turn the last parameter of `_computeFeeForNextClaim `:

```
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/15_
