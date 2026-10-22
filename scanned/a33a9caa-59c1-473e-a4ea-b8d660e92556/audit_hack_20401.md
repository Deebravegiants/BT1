# [M] 5.3.6 Unsafe casting inRewardsDistributorleads to underflow ofveForAt.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** RewardsDistributor.sol#L121-L127
**Description:** Solidity does not revert when casting a negative number touint. Instead, it underflows to a large
number. In theRewardDistributorcontract, the balance of a token at specific time is calculated as follows
IVotingEscrow.Point memory pt = IVotingEscrow(_ve).userPointHistory(_tokenId, epoch);
Math.max(uint256(int256(pt.bias - pt.slope * (int128(int256(_timestamp - pt.ts))))), 0);

This supposes to return zero when the calculated balance is a negative number. However, it underflows to a large
number.
This would lead to incorrect reward distribution if third-party protocols depend on this function, or when further
updates make use of this codebase.
**Recommendation:** Recommend following other parts of the codebase and returning zero for a negative number.
int256 result = int256(pt.bias - pt.slope * int128(int256(_timestamp - pt.ts)));
if (result < 0) return 0;
return uint256(result);

Also, recommend applying the fix to other parts ofrewardDistributorRewardsDistributor.sol#L196 RewardsDis-
tributor.sol#L254 RewardsDistributor.sol#L145
**Velodrome:** Fixed in commit 6485ef.
**Spearbit:** Verified.
