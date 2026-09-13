# [H] 6.1 Staking Rewards Incorrect Trimming

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

In the StakingRouter, the getStakingRewardsDistribution assigns fees to recipient addresses. It
then trims the resulting arrays so that there are no recipients that receive an amount of zero. However,
this trimming does not work correctly.

The recipients and moduleFees arrays are filled left-to-right, using the same index as the
modulesCache. This means that the "empty" entries, where the module fees are zero, occur
non-deterministically throughout the array. Hence, when the last entries are trimmed, some modules that
would otherwise receive fees are not being returned. Likely, the intent was to use the
rewardedModulesCount as an index for these arrays, so that modules which receive no fee would not
increment the index.

As such, the results returned by getStakingRewardsDistribution have the potential to be very
incorrect, distributing far less fees than intended, and only distributing fees to the recipients "lucky"
enough to be stored early in the modulesCache array.

Code corrected

The issue was fixed by using the rewardedModulesCount as an index for the resulting arrays, thereby
ensuring that the modules receiving rewards are stored contiguously at the start of the returned arrays.
Thus, the trimming is now done correctly.
