# [H] Underflow in `FSD.burn` breaks withdrawals and could allow stealing reserve

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-26
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/51
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

## Vulnerability Details
The `FSD.burn` function performs the following computation to determine the `tokenAmount` that a user must own which is then burned 

```solidity
function burn(uint256 capitalDesired, uint256 tokenMaximum) external {
    uint256 tokenAmount =
        calculateDeltaOfFSD(etherBalanceAtBurn, -int256(capitalDesired));
}
```

An attacker can acquire a few tokens using `mint`.
They then call `burn(type(uint256).max, ...)` and as `type(uint256).max == int256(-1)` the `tokenAmount` will be: `uint256 tokenAmount = calculateDeltaOfFSD(etherBalanceAtBurn, -(-1)=1);`, i.e. the attacker only needs to own a few `FSD` tokens.
However, their withdrawal increases by `2^256 * (1 - 0.0375)` as it uses the `capitalDesired = type(uint256).max = 2^256` as a base.
There's another underflow that determines the amount of tokens that will be minted to the contract which is not important for this attack.

Calling it with `capitalDesired=-1` will most likely fail in the `_increaseWithdrawal` function that uses SafeMath:

```
pendingWithdrawals = pendingWithdrawals.add(amount);
```

However, calling `burn` with `2^256 - pendingWithdrawals - 1` will succeed due to a similar type-cast issue where one needs to pay `calculateDeltaOfFSD(etherBalanceAtBurn, pendingWithdrawals);` FSD tokens.

## Impact
It will at least break the contract when called with `2^256 - pendingWithdrawals - 1` because `pendingWithdrawals` may not be increased afterwards anymore due to overflow checks.
It might be possible to also steal the reserve if the parameters are chosen in a smart way such that `withdraw` does not fail later.

## Recommendation
Use SafeMath everywhere. As the ranges of `uint256` and `int256` are different, one may not simply cast an `uint256` to `int256`. Check that the `uint256` fits into the `int256` first by `require(capitalDesired <= uint256(type(int256).max))`.
