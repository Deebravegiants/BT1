# [M] Protection can be bought in late pools, allow multiple times

## Summary
Severity: Medium
Contest weight: 0.2488
Dataset id: 19914
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A buyer can buy a protection for a pool that's already late on a payment. The buyer can pay the minimal premium and get a higher chance of getting a compensation. Protection sellers may bear higher losses due to reduced premium amounts and the increased chance of protection payments.
The protocol allows lenders on Goldfinch to get an insurance on the funds they lent. The insurance is paid after a repayment was late. The protocol doesn’t allow protection buyers to buy protections for pools that’s already late to disallow buyers abusing the protections payment mechanism. To do this, the _verifyLendingPoolIsActive function checks the current status of a pool and reverts if it’s late.
However, poolStatus is cached and can be outdated when the function is called, since it's not updated in the call. Pool statuses are updated in assessStates and assessStateBatch, which are triggered on schedule separately. This allows buyers to buy protections in pools that's already late in Goldfinch but still active in Carapace.
Consider this scenario:
1. A pool is in the active state after assessStates is run.
2. Before the next assessStates call, the pool gets into the late state, due to a missed repayment. However, in the protocol, the pool is still in the active state since assessStates hasn't been called.
3. The malicious buyer front runs the next assessStates call and submits their transactions that buys a protection with the minimal duration for the pool. The _verifyLendingPoolIsActive function passes because the pool's state hasn't been updated in the contracts yet.
4. The assessStates call changes the status of the pool to LateWithinGracePeriod, which disallows buying protections for the pool.
5. If the pool eventually gets into the default state (chances of that is higher since there's already a late payment), the malicious buyer will be eligible for a compensation.
Protection buyers can increase their chances of getting a compensation, while buying protections with the minimal duration and paying the minimal premium. Protection sellers will bear increased losses due to reduced premium amounts and the increased chance of a compensation.
1. _verifyLendingPoolIsActive checks the current status of a pool and reverts if it's not active: ProtectionPoolHelper.sol#L412-L415
2. Pool statuses are cached and are stored in DefaultStateManager: DefaultStateManager.sol#L278-L280
3. Pool statuses are updated in DefaultStateManager.assessStates: DefaultStateManager.sol#L119
4. DefaultStateManager.assessStates is not called by ProtectionPool.buyProtection: ProtectionPool.sol#L162

## Recommendation
In ProtectionPoolHelper._verifyLendingPoolIsActive, consider calling DefaultStateManager._assessState to update the status of the pool for which a protection is bought.
