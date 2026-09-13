# [M] Trader orders can be frontrun and users can be denied from trading

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-tracer
Published: 2021-06-30
Source: https://github.com/code-423n4/2021-06-tracer-findings/issues/100
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `Trader` contract accepts two signed orders and tries to match them.
Once they are matched and become filled, they can therefore not be matched against other orders anymore.

This allows for a griefing attack where an attacker can deny any other user from trading by observing the mempool and front-running their trades by creating their own order and match it against the counter order instead.

## Impact
A trader can be denied from trading.
The cost of the griefing attack is that the trader has to match the order themselves, however depending on the liquidity of the order book and the spread, they might be able to do the counter-trade again afterwards, basically just paying the fees.

It could be useful if the attacker is a liquidator and is stopping a user who is close to liquidation from becoming liquid again.

## Recommended Mitigation Steps
This seems hard to circumvent in the current design.
If the order book is also off-chain, the `executeTrade` could also be a bot-only function.
