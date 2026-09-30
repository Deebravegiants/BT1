# [C] C-03 | Range Orders Arbitraged

## Summary
Severity: Critical
Contest weight: 0.2435
Dataset id: 2386
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The creation of range orders starts from the current pool price using a rounded tick. However the current pool rounded tick at the time in which the user decides to send their range may be significantly different then the current pool price when their order creation transaction is recorded in a block.
The Uniswap V4 pool that is used for Gamma limit orders is distinct from other Uniswap V4 liquidity sources, therefore it is entirely possible that there is little or no liquidity below the current market price when a limit order creation transaction is submitted to the mempool by a user.
A malicious actor can therefore swap with 0 input amount and a sqrtPriceLimit set to an extremely low price to move the pool price very low directly before a user’s range is created.
After the user’s orders are created, liquidity will now be available in the pool at a very low price for the provided token. The malicious actor can now buy up this provided liquidity from the user at a very advantageous price to net a proﬁt.

## Recommendation
Consider allowing users to specify a minimum and maximum tick which they will accept the range, similar to a slippage tolerance.
