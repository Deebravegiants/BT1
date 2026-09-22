# [M] Traders can still close positions even if they are liquidable

## Summary
Severity: Medium
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L266
Type: audit-issue

## Details
# Traders can still close positions even if they are liquidable

## Summary
Traders can still close positions even if they are liquidable.

## Vulnerability Detail
Currently any trader can close their order at any time, even if the order is liquidable, because there is no check for it.

There are so many things that can go bad during liquidations. I have submitted several issues in this contest, but also if the keepers do decide to not liquidate because it is not profitable or the transaction reverts, a trader can still close their position incurring in bad debt for the protocol and  a paused state because `is_accepting_new_orders` will be set to false


## Impact
Penalty fees will not be earned by the protocol and the protocol will fail in a paused new orders state
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L266

## Tool used

Manual Review

## Recommendation
Add a check whether the position is liquidable before closing it `def _is_liquidatable(_position_uid: bytes32) -> bool:`
