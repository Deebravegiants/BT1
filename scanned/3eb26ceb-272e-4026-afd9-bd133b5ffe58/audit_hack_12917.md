# [M] Distributing the trading fee can force the liquidations to always revert

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L205
Type: audit-issue

## Details
# Distributing the trading fee can force the liquidations to always revert

## Summary
The protocol transfers the protocol fees to the fee receiver in the same transaction that executes the liquidations. In some cases, those transfers can fail, making those liquidations to revert and making the protocol to accrue bad debt.

## Vulnerability Detail
There are situations where a token is paused (for example, `BNB` can be paused) or some address is blacklisted (for example, `USDC` was famous for doing it).

When executing the functions[ `open_position`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L205) and [`liquidate`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L373), both of them call the function [`_distribute_trading_fee`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1342).

That function distributes a small fee of the debt token used in the position to the protocol fee receiver address set by the protocol. But if the transfer fails for some reason, like by having the protocol fee receiver address blacklisted by the debt token (for example by `USDC` or if the token is paused; this transfer will fail and cause the parent functions to also revert.

That is not dangerous in the `open_position` function but in the `liquidate` function is very dangerous since it would make positions that should be liquidated to accrue bad debt in the protocol.

Other similar issues: https://github.com/sherlock-audit/2023-01-cooler-judging/issues/23

## Impact
It is dangerous as I stated because it can break the liquidation process and accrue bad debt in the protocol but since it is not very frequent to be blacklisted or have a token paused, I set this as a med issue; it is a very dangerous issue but not very likely to happen.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1355

## Tool used
Manual Review

## Recommendation
Instead of transferring the protocol fee amount right in the same transaction, store in a variable the accumulated fee of each debt token and implement another withdraw method that sends the fee to the protocol fee receiver address.
