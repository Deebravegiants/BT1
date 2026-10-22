# [H] TotalPWPCSB is never decremented

## Summary
Severity: High
Contest weight: 0.7873
Dataset id: 22765
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In FairSideNetwork.sol, the totalPWPCSB variable is never decremented even after
memberships expire or when cost share benefits have been utilized.
The totalPWPCSB variable represents the total Cost Share Benefits (CSB) available
across all memberships. It is incremented via setCoverCounts() when new
memberships are purchased or when existing memberships are topped up or
renewed.
However, there's no mechanism to decrement totalPWPCSB when memberships
expire or when CSBs are claimed.
```solidity
// FairSideNetwork.sol
function setCoverCounts(uint256 costShareBenefit) internal {
    totalPWPCSB += costShareBenefit;
}

function increaseOrDecreaseCSB(
    uint256 amount,
    address account,
    uint256 coverId,
    bool increase
) external override onlyFairSideClaims {
    Membership storage membershipId = membership[coverId];
    if (membershipId.owner != account) {
        revert FSNetwork_InvalidCoverIdForAccount();
    }
    if (increase) {
        membershipId.availableCostShareBenefits += amount;
    } else {
        membershipId.availableCostShareBenefits -= amount;
    }
}
```
1) Whenever a membership is purchased/topup/renewed, the contract checks
that totalPWPCSB does not exceed the getMaxTotalCostShareBenefits(). Since
totalPWPCSB is never decreased, it will eventually hit this cap and prevent new
memberships from being purchased.
2) As totalPWPCSB increases so does fShare (calculated in getTokenFShare())
which is used to calculate FSD token price. As fShare increases, the
denominator of the division (_pow3(fShare).mul(C)) becomes larger. Since x
is raised to the fourth power (_pow3(x).mul(x)) in the numerator, the overall
result of the division decreases. This means that as fShare becomes very
large, the value returned by _f() i.e. FSD token price will approach zero.
```solidity
// FairSideFormula2.sol
function _f(bytes16 x, bytes16 fShare) private pure returns (bytes16) {
    return A.add(_pow3(x).mul(x).div(_pow3(fShare).mul(C)));
}

// f represents the relation between capital and token price
function f(uint256 x, uint256 fShare) public pure returns (uint256) {
    bytes16 _x = denormalize(x);
    bytes16 _fShare = denormalize(fShare);
    return normalize(_f(_x, _fShare));
}
```
3) As totalPWPCSB increases, so does getNetworkFshare() which results in
getFShareRatio() trending towards zero. This impacts
calculateSmartStakingReward() as fShareRatio will never exceed 125%.

## Recommendation
1) totalPWPCSB should be decremented after membership expiry. This should be
handled for expired memberships.
2) totalPWPCSB should be decremented after claims payout via
increaseOrDecreaseCSB()
