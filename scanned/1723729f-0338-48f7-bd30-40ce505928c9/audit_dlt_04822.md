# [H] setParam() cooldown can cause loss of fund to liquidity providers

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/17
Type: sherlock-finding

## Details
koxuan

high

# setParam() cooldown can cause loss of fund to liquidity providers

## Summary
Cooldown changed by admin intentionally or unintentionally during the active period can cause liquidity providers to be unable to withdraw from liquidity pool after maturity without slippages. 

## Vulnerability Detail
A malicious party can roll the AutoRoller immediately  if cooldown is set to zero or an arbitrary small value just before sponsor settles the series which triggers `cooldown`, causing a loss of fund to liquidity providers who are not aware of the change in cooldown value.
`else if (lastSettle + cooldown > block.timestamp)` will always be false when cooldown is set to zero.

## Impact
Loss of fund to liquidity providers as they have to exit the liquidity with slippages.
## Code Snippet
[AutoRoller.sol#L154-L167](https://github.com/sherlock-audit/2022-11-sense/blob/main/contracts/src/AutoRoller.sol#L154-L167)



```solidity

    function roll() external {
        if (maturity != MATURITY_NOT_SET) revert RollWindowNotOpen();

        if (lastSettle == 0) {
            // If this is the first roll, lock some shares in by minting them for the zero address.
            // This prevents the contract from reaching an empty state during future active periods.
            deposit(firstDeposit, address(0));
        } else if (lastSettle + cooldown > block.timestamp) {
            revert RollWindowNotOpen();
        }

        lastRoller = msg.sender;
        adapter.openSponsorWindow();
    }

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/17_
