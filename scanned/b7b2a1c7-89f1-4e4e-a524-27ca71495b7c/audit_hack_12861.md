# [H] DOS protocol by continuely triggering the `is_accepting_new_orders` false state by passing a low `min_amount_out`

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L266
Type: audit-issue

## Details
# DOS protocol by continuely triggering the `is_accepting_new_orders` false state by passing a low `min_amount_out`

## Summary
DOS protocol by continuely triggering the `is_accepting_new_orders` false state by passing a low `min_amount_out`


## Vulnerability Detail

When a trader opens a position, they are able to DOS the protcol by specifying a low enough `min_amount_out` (slippage) and getting slightly less funds back than what he initialy borrowed, increasing the bad debt from the protocol.

Everything starts on the `def close_trade(_trade_uid: bytes32, _min_amount_out: uint256) -> uint256:` function in `marginDex`. A trader is able to specify themselves the `_min_amount_out` for their closed position, allowing traders to specify whatever amount they want. 

If the slippage specified is high enough, it will automatically attrack sandwitch bots from uniswap itself, returning to the trader less position than they actually borrowed by getting sandwitched. Specifying a lot of slippage can be done (purpusely (in bath faith) to DOS `unstoppable`, or even without wanting). This is an scenario where `unstoppable` will find themselves a lot because it is very easy to arrive to.

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L266

Getting to the `is_accepting_new_orders` false state will almost completely pause the margin module. 
This can be done as many times as wanted, at it literally costs 1$ to perform the attack. You only have to receive less than you borrowed, it can be as low as a dollar.


## Impact
Almost a complete DOS of the entire protocol can be done at almost not cost.


## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L266


## Tool used

Manual Review

## Recommendation
Have some kind of cooldown to when a position can be closed after being open or change the architecture of `is_accepting_new_orders`
