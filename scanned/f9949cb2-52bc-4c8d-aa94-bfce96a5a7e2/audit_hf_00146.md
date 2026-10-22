# [M] Claim liquidation escrow

## Summary
Severity: Medium
Contest weight: 0.5648
Dataset id: 603
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A liquidator can always claim the liquidation escrow in the following way:

* create a second account
* setup a complimentary trade in that second account, which will result in a large slippage when executed
* call `executeTrade` (which everyone can call), to execute a trade between his own two accounts with a large slippage
* the slippage doesn’t hurt because the liquidator owns both accounts
* call `claimReceipt` with the receiptId of the executed order, within the required period (e.g. 15 minutes)

[L67](https://github.com/code-423n4/2021-06-tracer/blob/main/src/contracts/Trader.sol#L67)

```solidity
function executeTrade(Types.SignedLimitOrder[] memory makers, Types.SignedLimitOrder[] memory takers) external override {
```

[L394](https://github.com/code-423n4/2021-06-tracer/blob/main/src/contracts/Liquidation.sol#L394)

```solidity
function claimReceipt( uint256 receiptId, Perpetuals.Order[] memory orders, address traderContract) external override {
```

Recommend to perhaps limit who can call `executeTrade`.

Valid issue which would allow someone to get reimbursed for slippage against themselves.

The Trader contract will have whitelisted relayers added to prevent issues like this (similar to #119)

## Recommendation
No recommendation
