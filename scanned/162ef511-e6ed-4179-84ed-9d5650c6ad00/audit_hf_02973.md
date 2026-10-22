# [M] M-4 Incorrect slippage check

## Summary
Severity: Medium
Contest weight: 0.0172
Dataset id: 16499
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect slippage validation in the trade execution component of the protocol. The contract is supposed to compare the observed price impact of a swap against a user‑provided maximum slippage limit and reject the trade if the impact exceeds that limit. However, the logical condition is reversed: the code treats a slippage value that is greater than the allowed maximum as acceptable and may reject trades that are actually within the limit. This reversal stems from a simple operator mistake in the slippage check, causing the contract to approve trades with excessive price impact. An attacker can exploit this by submitting a swap request with a deliberately high slippage value; the contract will consider the request valid and execute it, resulting in the user receiving far fewer output tokens than expected. From the user’s perspective the symptoms are a sudden loss of value: the transaction completes, but the received amount is much lower than the quoted price, sometimes appearing as if the funds have vanished or the balance becomes unexpectedly small. The impact includes direct financial loss for users, distortion of the protocol’s accounting, and potential arbitrage opportunities for malicious actors. The bug manifests whenever the TradeFactoryExecutor component processes a trade and evaluates the slippage condition, affecting any participant who relies on that contract for token swaps. It was discovered during a security audit performed by the developers, who noticed that the slippage guard behaved opposite to its intended purpose. The issue can be hard to notice because the surrounding code may appear to perform a standard safety check, and typical test cases that use modest slippage values may not trigger the faulty branch. To remediate the problem the slippage comparison must be inverted so that the contract only proceeds when the observed slippage is less than or equal to the user‑specified maximum, restoring the intended protection against unfavorable price movements. In broader terms this is a classic example of a reversed conditional check that undermines input validation and leads to financial mis‑execution.

## Recommendation
Note: this issue was found by the developers 2.4 Low
