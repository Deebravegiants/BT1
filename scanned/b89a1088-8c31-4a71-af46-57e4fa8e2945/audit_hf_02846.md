# [H] Lack of Slippage Protection in buy_with_sol() function

## Summary
Severity: High
Contest weight: 0.1674
Dataset id: 15853
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The buy_with_sol() function allows users to purchase ICO tokens using SOL. The function retrieves the current SOL/USDC price from a price feed and calculates the value of the SOL the user is spending in USDT. After this, the number of ICO tokens is determined based on the equivalent USDT value. The problem here is that this function does not incorporate slippage protection. Given the inherent volatility of cryptocurrency prices, this absence could result in users paying more or receiving fewer tokens than expected if the price fluctuates between the time the price is fetched and the transaction is executed.

## Recommendation
Introduce a maximum allowable slippage percentage that users can set before executing the transaction.
