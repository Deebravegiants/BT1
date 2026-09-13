# [H] Vault.vy: Malicious user can create bad debt and steal the protocol's funds

## Summary
Severity: High
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L279
Type: audit-issue

## Details
# Vault.vy: Malicious user can create bad debt and steal the protocol's funds

## Summary
Malicious user to intentionally create bad debt and potentially extract funds from the protocol.

## Vulnerability Detail
A characteristic of leveraged trading platforms is the risk of bad debt, where the amount received from closing a position is less than the borrowed amount, especially if liquidation is delayed or prices change rapidly. 

In the `Vault.vy` contract, a malicious user could exploit this to intentionally create bad debt using the following scenario:

Assume 1 ETH = 2000 USDC.

1. Open a trade with 1000 USDC margin and 9000 USDC debt. (Position: 5 ETH)
2. Borrow ETH via a flash loan and sell it into the pool. (Current exchange rate: 1 ETH == 1000 USDC)
3. Set 'min_amount_out' to 1, and perform 'close_position'. (Receive roughly 5000 USDC)
4. Sell the USDC borrowed via flash loan back to the pool. (Current exchange rate: 1 ETH < 2000 USDC)
5. Repay the flash loan.

The `close_position` function doesn't check whether the position is eligible for liquidation. Positions that are liquidatable shouldn't be closed by users.

While `min_amount_out` is set for slippage control in both `close_position` and `reduce_position` functions, a malicious user can easily bypass this by setting it to a small value like 1.

Although `reduce_position` checks for liquidation availability, it does so through the chainlink oracle price, so it does not reflect the case where the price of the pool is manipulated by flashloan. Since the oracle price has not changed, it returns that it is not liquidated, but the actual pool price may be manipulated to create bad debt.

## Impact
The vulnerability could be exploited by malicious users to intentionally create bad debt and potentially extract funds from the protocol. This could affect the solvency and trustworthiness of the protocol, negatively impacting all users.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L279
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290-L336
## Tool used

Manual Review

## Recommendation
It is not common for a user to incur bad debt when closing a position (it should already be liquidatable), so it is recommended to revert in such cases. And check liquidatable before and after close position.
