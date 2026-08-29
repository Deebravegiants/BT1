# [M] There may be a lesser amount of Aave aTokens than what is tracked in the OrigamiAaveV3BorrowAndLend.

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-03-01
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/52
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x710b245526ff7b98f3a018e697215f57c7f0451d132e35e912f4bfe7ea657837
**Severity:** medium

**Description:**
**Description**\
In any `protocol`, certain main `invariants` are expected to be maintained. 
During normal `audit` competitions in many platforms , a list of these `invariants` is typically established, and any violation is considered a vulnerability, at least of `medium` severity.

Likewise, I believe the `Origami protocol` also has some key `invariants`. 
One of the important `main invariants` of the `Origami protocol`, in my view, is as follows:

`The suppliedBalance tracked in the OrigamiAaveV3BorrowAndLend should never be less than the actual balance.` 

The `actual balance` comprises the sum of the `balance tracked manually` and the `donated tokens`. 
Thus, it is essential that there always exists a larger actual `balance` than the `suppliedBalance`.
Several functions within the `protocol` including `reservesBalance`, `_maxRedeemFromReserves` and `_validateAfterRebalance` functions rely on `suppliedBalance` value, and in the worst-case scenario, a `withdrawal` could potentially be reverted due to a lack of `1 wei`.

While I cannot enumerate all the `potential impacts` here, I firmly believe that maintaining this `main invariant` is crucial and should receive an appropriate level of attention.

**Attack Scenario**\
I will describe the process through an example accompanied by mathematical calculations.

In `AaveAToken`, the following relationship exists between the `balance` and `scaledBalance`.
```
function balanceOf(
    address user
  ) public view virtual override(IncentivizedERC20, IERC20) returns (uint256) {
    return super.balanceOf(user).rayMul(POOL.getReserveNormalizedIncome(_underlyingAsset));
  }
```
The `POOL.getReserveNormalizedIncome(_underlyingAsset)` represents the `current index`, and the `rayMul` formula is as follows:
```
function rayMul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    // to avoid overflow, a <= (type(uint256).max - HALF_RAY) / b
    assembly {
      if iszero(or(iszero(b), iszero(gt(a, div(sub(not(0), HALF_RAY), b))))) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/52_
