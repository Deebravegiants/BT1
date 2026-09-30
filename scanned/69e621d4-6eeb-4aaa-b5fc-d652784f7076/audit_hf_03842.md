# [H] Pool deviation check in SimpleManager on re- balancing

## Summary
Severity: High
Contest weight: 0.3758
Dataset id: 20092
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In SimpleManager a price deviation check is enforced to prevent an operator to add
liquidity to a UniV3 pool at a really unfavorable price during rebalance and backrun
to extract vault funds. We will show here that this check can be entirely bypassed
by a malicious operator.
Rebalance context
During a call to SimpleManger.rebalance, the following operations are run:
• 1/ Enforce price deviation not too large for mint pools:
mplates/contracts/SimpleManager.sol#L366-L385
and correct slippage parameter for swap:
es/contracts/SimpleManager.sol#L318-L354
• 2/ Remove liquidity on specified UniV3 ranges (we are not going to use it here)
• 3/ Use a low level call to a whitelisted Router to execute a swap
cts/ArrakisV2.sol#L334-L336
• 4/ Enforce received amounts from the swap
• 5/ Provide liquidity on specified UniV3 ranges
• 6/ Enforce provided amounts during addLiquidity (these parameters are
provided by operator and unbounded, so they can be (0, 0), and check is a
noop).
Exploit description
We are going to use the swap step (3/) to imbalance the pools after the check of
price deviation (1/) is passed, so the liquidity provided in 5/ is done at a really
unfavorable price, and can be backrun by the operator to extract funds from the
vault.
To not trigger the slippage protection after the swap, we are going to use the router
to swap on a totally unrelated pool of tokens controlled by the malicious operator:
PSN/PSN2 (PSN stands for Poison).
PSN token has a callback in the _transfer function to make a large swap on UNIv3
pool where the operator is going to provide liquidity in 5/, to deviate it a lot.
after the call to the router is done, no changes to the balances of the vault have
been made, the slippage checks out.
Liquidity provided at 5/ is done at a terrible price for some of the ranges, and the
operator backruns for a nice profit.
NB: All these steps can be run inside a flashloan callback, to not use attacker own
funds
An arbitrary amount can be drained from the vault by an operator

## Recommendation
Ideally the check on price deviation should be enforced right before the liquidity
providing.
