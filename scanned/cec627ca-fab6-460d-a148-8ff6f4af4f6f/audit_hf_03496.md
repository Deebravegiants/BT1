# [M] `AdminImpl::ownerWithdrawExcessTokens` does not check the solvency of given market before attempting to withdraw excess tokens

## Summary
Severity: Medium
Contest weight: 0.3373
Dataset id: 19120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`AdminImpl::ownerWithdrawExcessTokens`](https://github.com/feat/dolomite-margin/blob/e10f14320ece20d7492e8e68400333c5c7dec656/contracts/protocol/impl/AdminImpl.sol#L152-L181) allows the protocol admin to withdraw excess tokens in Dolomite Margin for a specific market. Excess tokens are calculated using the following formula:

Excess tokens = Token Balance (L) + Total Borrowed (B) - Total Supplied (S)

Here, `L` represents the real liquidity, which is the actual token balance in Dolomite Margin. `B` and `S` are virtual Dolomite balances. Over time, excess tokens increase as the protocol earns fees after passing the borrowers' interest fee to suppliers. The extent of these fees depends on the total outstanding borrowing in the market and the earnings rate.

However, in certain scenarios, the admin's withdrawal of `numExcessTokens` can lead to temporary insolvency in the protocol. This occurs when the token balance remaining after withdrawal is lower than the maximum withdrawable value for that market after adjusting for collateralization. This situation is especially likely in less liquid markets or in markets with high concentration risk, where a single entity has provided a significant portion of liquidity.

In this situation, withdrawal actions might cause a denial-of-service (DoS) due to the protocol's inadequate balance. While the consequences could be significant, the chance of this happening is minimal since fees are typically much lower than pool balances. As a result, we assess the severity level as MEDIUM.

## Proof of Concept
Assumptions:
- The interest rate on USDC is 10% per year
- Earnings rate = 80% (20% of borrowing interest is the protocol fee)

Consider a simplified scenario below:

| Time  | Action | Alice | Bob  | Pete | USDC Balance | ETH Balance |  Excess USDC  |
|------|--------|---------|------|------| ------------| --------------| -------------- |
| T =0 | Alice deposits 2 ETH, Bob 5000 USDC    | 2   | 5000  | -  | 5000 | 2 |  0 |
| T=0 | Alice borrows 2000 USDC    | 2 , -2000    | 5000  | -  | 5000 | 2 |  0 |
| T=1yr | 200 USDC interest accrued    | 2, -2200  | 5160  | -  | 5000 | 2 |  40 |
| T=1yr | Pete deposits 1000 USDC    | 2, -2200  | 5160  | 1000  | 6000 | 2 |  40 |
| T=1yr | Bob withdraws 5160 USDC    | 2, -2200  | 0  | 1000  | 840 | 2 |  40 |
| T=1yr | Protocol withdraws 40 USDC    | 2, -2200  | 0  | 1000  | 800 | 2 |  0 |

At this stage, Pete cannot withdraw his deposit even though there is no loan against his account. This is because the protocol is temporarily insolvent until another liquidity provider deposits fresh liquidity.

## Recommendation
To address this issue, it is recommended to introduce solvency checks for each market in the `AdminImpl::ownerWithdrawExcessTokens` function before completing withdrawals. The protocol should ensure that withdrawing excess tokens does not result in temporary insolvency.
