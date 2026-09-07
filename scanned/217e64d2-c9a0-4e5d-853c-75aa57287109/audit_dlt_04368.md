# [M] debtWriteOff() Not updated #lastUpdated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/111
Type: sherlock-finding

## Details
bin2chen

medium

# debtWriteOff() Not updated #lastUpdated

## Summary
when debtWriteOff() will modify vouch.locked ,but don't modify vouch.lastUpdated

## Vulnerability Detail
UserManager.sol#debtWriteOff
```solidity
    function debtWriteOff(
        address staker,
        address borrower,
        uint96 amount
    ) external {
...
            // update vouch trust amount
        vouch.trust -= amount;
        vouch.locked -= amount;/**** update locked ,but don't update lastUpdated *****/

```

## Impact
getFrozenInfo() and other use lastUpdated will error

## Code Snippet

https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/user/UserManager.sol#L755

## Tool used

Manual Review

## Recommendation

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/111_
