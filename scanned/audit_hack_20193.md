# [M] 6.3.6 Avoid multiple divisions when calculatingoperatorRewards

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** River.1.sol#L277

**Description/Recommendation:** In _onEarnings, we calculate thesharesToMint andoperatorRewardsby div-
ing 2 numbers. We can reduce the number of divisions to 1 and also delegate this division to_rewardOperators.
This would further avoid the rounding errors that we would get when we divide two numbers inEVM. So in:

```
uint256 globalFee = GlobalFee.get();
uint256 numerator = _amount * currentTotalSupply * globalFee;
uint256 denominator = (_assetBalance() * BASE) - (_amount * globalFee);
uint256 sharesToMint = denominator == 0? 0 : (numerator / denominator);
```
```
uint256 operatorRewards = (sharesToMint * OperatorRewardsShare.get()) / BASE;
```
```
uint256 mintedRewards = _rewardOperators(operatorRewards);
```
Instead of passingoperatorRewardswe can pass 2 values, one for the numerator and one for the denominator.
This way we can avoid extra rounding errors introduced in_rewardOperators._rewardOperatorsalso need to be
changed slightly to account for these 2 new values.

```
uint256 globalFee = GlobalFee.get();
uint256 numerator = _amount * currentTotalSupply * globalFee * OperatorRewardsShare.get();
uint256 denominator = ((_assetBalance() * BASE) - (_amount * globalFee)) * BASE;
```
```
uint256 mintedRewards;
```
```
if(denominator != 0) {// note: this was added to avoid calling`_rewardOperators`if`denominator == 0`
mintedRewards = _rewardOperators(numerator, denominator);
}
```
Without this correction, the rounding errors are in favor of the general users/stakers and thetreasuryof theRiver
protocol (not the operators).

**Alluvial:** The whole operator rewarding system has been removed in SPEARBIT/8.

**Spearbit:** Acknowledged.
