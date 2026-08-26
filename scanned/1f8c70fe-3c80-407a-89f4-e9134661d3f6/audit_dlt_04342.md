# [M] Using `removeReserves`, `admin` can withdraw all `lenders` funds.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/154
Type: sherlock-finding

## Details
Picodes

medium

# Using `removeReserves`, `admin` can withdraw all `lenders` funds.

## Summary
Using `removeReserves`, `admin` can withdraw all `lenders` funds as there is no safeguard on what can be withdrawn.

## Vulnerability Detail
This is a vulnerability regarding admin privileges and the fact that here, all assets deposited using the `mint` function of `UToken` can be withdrawn by the `admin` at any time.

*Side note: why the `whenNotPaused` modifier in `removeReserves` ? It's `onlyAdmin` anyway*.

## Impact

## Code Snippet
```solidity
function removeReserves(address receiver, uint256 reduceAmount)
    external
    override
    whenNotPaused
    nonReentrant
    onlyAdmin
{
    if (!accrueInterest()) revert AccrueInterestFailed();

    totalReserves -= reduceAmount;

    if (!IAssetManager(assetManager).withdraw(underlying, receiver, reduceAmount)) revert WithdrawFailed();

    emit LogReservesReduced(receiver, reduceAmount, totalReserves);
}
```

## Tool used

Manual Review

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/154_
