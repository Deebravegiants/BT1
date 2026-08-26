# [M] The First User To Borrow a Particular Token Can Drain Funds In MarginSwap by Making An Undercollateralized Borrow Using Flash Loans

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/66
Type: code-finding

## Details
# Handle

jvaqa


# Vulnerability details

The First User To Borrow a Particular Token Can Drain Funds In MarginSwap by Making An Undercollateralized Borrow Using Flash Loans

## Impact

This attack can be performed with any two ERC20 tokens, where one of them has not yet been borrowed on MarginSwap.
Since any newly added token must first be loaned before it can be borrowed, there will always be a window of time where this attack is possible for any newly added asset.
The magnitude of the attack will be limited by the size of MarginSwap.CrossMarginAccounts.tokenCaps[borrowToken], but could potentially allow an attacker to drain one particular token from MarginSwap if it has been lent but not yet borrowed.

## Proof of Concept

For the sake of argument, let's assume two ERC20 tokens called Token0 and Token1, who have a current market price of 1:1.

Expected Behavior:
Alice can only borrow 900 Token1 if she puts up 1,000 Token0 as collateral.

Actual Behavior:
Using this attack, Alice can borrow 9,000 Token1 when using 1,000 Token0 as collateral. She can leave her 1,000 Token0 behind in MarginSwap, and sell the 9,000 Token1 for an 8,000 token profit.
It should be noted that this attack can be larger than what is shown here: we demonstrate a 10x attack for simplicity, but it only depends on how much liquidity is in the Uniswap pool, determining how much it will cost to skew the price.

(0) Alice begins with 1,000 Token0 and 1,000 Token1
(1) Alice calls AliceAttackerContract.functionOneOfTwo(), which performs the following calls:
  (1.1) Calls Token0.approve(MarginSwap, UINT256MAX) to allow MarginSwap to spend her Token0
  (1.2) Calls MarginSwap.MarginRouter.crossDeposit(Token0Address, 1000 * 1e18)
(2) Alice waits for n + 1 blocks to pass, where n is specified in MarginSwap.CrossMarginTrading.coolingOffPeriod (currently set at 20 blocks)
(3) Alice calls AliceAttackerContract.functionTwoOfTwo(), which performs the following calls:
  (3.1) Flashloan Token1
  (3.2) Trade Token1 for Token0 on Uniswap to make Token1's price on Uniswap appear cheaper. For argument's sake let's skew the price to 10:1
  (3.3) Calls Token1.approve(MarginSwap, UINT256MAX) to allow MarginSwap to spend her Token1
  (3.3) Call MarginRouter.crossBorrow(Token1Address, 9000 * 1e18);
  (3.4) Call MarginRouter.crossWithdraw(Token1Address, 9000 * 1e18);
  (3.5) Trade Token0 for Token1 on Uniswap to return the Uniswap price to market price, minus fees

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-04-marginswap-findings/issues/66_
