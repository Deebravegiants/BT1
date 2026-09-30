# [M] `estimatedAPR`

## Summary
Severity: Medium
Contest weight: 0.6261
Dataset id: 18770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the view function that reports an estimated annual percentage rate (APR) for the SavingsVest contract. The function calculates the APR by multiplying the current vesting profit by a yearly time factor and dividing by a weighted asset amount derived from the vesting period and total assets. However, it never checks whether any profit is actually locked at the moment of the call. Because the contract’s accrue() routine only updates vestingProfit and the timestamp when the collateralisation ratio deviates more than 0.1%, the vestingProfit variable can remain unchanged after the vesting period has fully elapsed. When the collateral ratio stays within the narrow safe band, accrue() is not triggered, leaving vestingProfit stale while lockedProfit() becomes zero. Consequently, estimatedAPR() continues to return a non‑zero value that reflects a past profit rate, even though no profit is currently available. From a user’s perspective the interface displays a positive APR, leading the user to expect earnings that never materialise; balances may appear to grow in the UI while the actual token balance remains unchanged. This discrepancy can cause confusion, erode trust in the protocol, and potentially influence investment decisions based on inaccurate yield information. The issue was discovered during a manual audit that compared the behaviour of accrue() with the APR estimation logic and observed that the APR did not drop to zero after the vesting period ended. The bug is subtle because the function is read‑only, does not revert, and the incorrect value only becomes apparent after a period of inactivity, making it easy to overlook in routine testing. The proper mitigation is to guard the APR calculation with a check that returns zero whenever the locked profit is zero, or to base the APR on the current locked profit rather than the stale vestingProfit value. By ensuring the function reflects the real profit state, the protocol restores accurate user expectations and aligns the displayed APR with the underlying accounting model.

## Proof of Concept
`SavingsVest.estimatedAPR()` returns the APR using the current `vestingProfit` and `vestingPeriod`.

```solidity
    function estimatedAPR() external view returns (uint256 apr) {
        uint256 currentlyVestingProfit = vestingProfit;
        uint256 weightedAssets = vestingPeriod * totalAssets();
        if (currentlyVestingProfit != 0 && weightedAssets != 0)
            apr = (currentlyVestingProfit * 3600 * 24 * 365 * BASE_18) / weightedAssets;
    }
```

First of all, it uses the current `vestingRatio = vestingProfit / vestingPeriod` for 1 year even if `vestingPeriod < 1 year`. I think it might be an intended behavior to estimate the APR with the current vesting ratio.

But it’s wrong to use the same vesting ratio after the vesting period is finished already.

In [accrue()](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/savings/SavingsVest.sol#L110), it updates the `vestingProfit` and `lastUpdate` only when it’s overcollateralized/undercollateralized more than 0.1%.

So `lastUpdate` wouldn’t be changed for a certain time while [collatRatio](https://github.com/AngleProtocol/angle-transmuter/blob/9707ee4ed3d221e02dcfcd2ebaa4b4d38d280936/contracts/savings/SavingsVest.sol#L110) is in range (99.9%, 100.1%).

1. At the first time, `vestingProfit = 100, vestingPeriod = 10 days` and `estimatedAPR()` returns the correct value.
2. After 10 days, all vestings are unlocked and there is no locked profit. But `accrue()` has never been called due to the stable collateral ratio.
3. In `estimatedAPR()`, `vestingProfit` will be 100 and it will return the same APR as 10 days before.
4. But the APR should be 0 as there is no locked profit now.

## Recommendation
`estimatedAPR()` should return 0 when `lockedProfit() == 0`.

```solidity
    function estimatedAPR() external view returns (uint256 apr) {
        if (lockedProfit() == 0) return 0; //check locked profit first

        uint256 currentlyVestingProfit = vestingProfit;
        uint256 weightedAssets = vestingPeriod * totalAssets();
        if (currentlyVestingProfit != 0 && weightedAssets != 0)
            apr = (currentlyVestingProfit * 3600 * 24 * 365 * BASE_18) / weightedAssets;
    }
```

Valid, although this function isn’t really useful as what matters in the end is how much a call to `accrue` would give. `estimatedAPR` should return an approximation of the current APR but is an approximation on the long run

@Picodes - It looks like a middle of Medium and Low as it’s a view function. Will keep as Medium because it will be used to estimate the profit rate for users.

PR: <https://github.com/AngleProtocol/angle-transmuter/commit/337c65d005bbd8ed6dfa76929d2cae475066756a>  
Applies the suggested fix.
