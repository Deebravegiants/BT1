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
  function _computeFeeForNextClaim(
    uint256 _minimumFee,
    SD59x18 _decayConstant,
    SD59x18 _perTimeUnit,
    uint256 _elapsed,
    uint256 _sold,
    uint256 _maxFee
  ) internal pure returns (uint256) {
    uint256 fee = LinearVRGDALib.getVRGDAPrice(
      _minimumFee,
      _elapsed,
      _sold,
      _perTimeUnit,
      _decayConstant
    );
    return fee > _maxFee ? _maxFee : fee;
  }
```

As you can see, the fee is capped based on the max fee for the prize tier being claimed for. This seems to be doing what was intended, however there is only one auction for all the tiers, and thus the auction decay constant is consistent across all the tiers:

```
  constructor(
    PrizePool _prizePool,
    uint256 _minimumFee,
    uint256 _maximumFee,
    uint256 _timeToReachMaxFee,
    UD2x18 _maxFeePortionOfPrize
  ) {
    if (_minimumFee >= _maximumFee) {
      revert MinFeeGeMax(_minimumFee, _maximumFee);
    }
    prizePool = _prizePool;
    maxFeePortionOfPrize = _maxFeePortionOfPrize;
    decayConstant = LinearVRGDALib.getDecayConstant(
      LinearVRGDALib.getMaximumPriceDeltaScale(_minimumFee, _maximumFee, _timeToReachMaxFee)
    );
    minimumFee = _minimumFee;
    timeToReachMaxFee = _timeToReachMaxFee;
  }
```

Whichever is the lowest of the auction `_maximumFee` and the tier `maxFee` is the max fee that could possibly be collected. In order to allow all prize tiers to be claimed it is likely that the `_maximumFee` in the constructor will be increased, however this now means the decay constant is greater and therefore the auctions ramp up faster. For tiers with a lower max fee, this means the max fee is reached significantly faster, leading to inefficient auctions.

## Tools used
Manual review

## Recommendation
Potentially there is another angle to resolve the issue reported in the original contest by having a mechanism that allows the max fee to be increased if not enough prizes have been redeemed in the last draw, although this introduces additional complexity.

Alternatively there needs to be an auction for each tier with its own decay constant (i.e. min and max fees) to ensure that all the auctions are ramping up in a similar (but not necessarily identical) manner. In my opinion this option makes the most sense and is the least complex and therefore also the hardest to manipulate (if at all).






## Assessed type

Other
