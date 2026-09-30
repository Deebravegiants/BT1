# [M] Incorrect check in Distribution.editPool() allows modifying pool configurations and reward parameter changes can lock stakes

## Summary
Severity: Medium
Contest weight: 0.4536
Dataset id: 10537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Distribution.editPool() function both incorrectly considers the new pool config, i.e., pool_, and performs an incorrect check > block.timestamp to determine if the Pool payout has started. This allows the modification of pool.payoutStart, pool.withdrawLockPeriod, and
pool.withdrawLockPeriodAfterStake while the payout period has already started.
```solidity
if (pool_.payoutStart > block.timestamp) {
    require(pool.payoutStart == pool_.payoutStart, "DS: invalid payout start value");
    require(pool.withdrawLockPeriod == pool_.withdrawLockPeriod, "DS: invalid WLP value");
    require(pool.withdrawLockPeriodAfterStake == pool_.withdrawLockPeriodAfterStake,
    "DS: invalid WLPAS value");
}
```
Another problem is that the remaining pool parameters, like initialReward, are not checked at all. It
also lead to stakes being locked.
The pool.initialReward variable for a given pool can be set by an admin through
Distribution.editPool()
to
a
large
number
such
that
a
call
to
Distribution._getCurrentPoolRate() will revert because of an overflow in functions such as
LinearDistributionIntervalDecrease.calculateMaxEndTime() and LinearDistributionIntervalDecrease.calculateFullPeriodReward().
Since Distribution._getCurrentPoolRate()
is invoked during Distribution.claim(), Distribution.stake(), Distribution.withdraw(), and
Distribution.editPool() the user's funds can remain locked in the contract without the
possibility for the pool to be edited back in a state that can recover the funds.

## Recommendation
The Distribution.editPool() function should check against the current pool
configuration to determine if the payout period has started.
```diff
@@ -84,7 +84,7 @@ contract Distribution is IDistribution, OwnableUpgradeable {
    Pool storage pool = pools[poolId_];
    require(pool.isPublic == pool_.isPublic, "DS: invalid pool type");
    if (pool_.payoutStart > block.timestamp) {
+
    if (pool.payoutStart <= block.timestamp) {
```
It must also be determined which permissions exactly the Distribution owner should have. Providing
sanity checks is a much weaker requirement than ensuring no stakes can be locked. If no stakes
should be locked, then all pool parameters must be checked and by testing it must be ensured that
changing the parameters to their limits cannot break calculations.
Morpheus: Fixed by removing the Distribution.editPool() function.
is created with. After the pool creation, the protocol owner cannot edit the pool and prevent users
from withdrawing their stETH.
