# [M] `balanceOf` will return an incorrect amount if stream is unfunded or partially funded

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/30
Type: sherlock-finding

## Details
adriro

medium

# `balanceOf` will return an incorrect amount if stream is unfunded or partially funded

## Summary

The function `balanceOf` present in the `Stream` will return a technically incorrect amount in case the stream hasn't been funded yet or is partially funded.

## Vulnerability Detail

The `balanceOf` function is used to report the amount of tokens available to be withdrawn by each party (payer or recipient). For the recipient, this is the amount available at the current block timestamp (given the rate per second) minus the amount already withdrawn. For the payer, it's the `remainingBalance` minus the amount that corresponds to the recipient.

The main issue is that, for both cases, the calculation doesn't take into account how many tokens are actually in the contract, since the stream can be created without actually funding it, or can be created and then be partially funded too.

## Impact

For the payer case, the impact isn't big since the `balanceOf` function isn't used within the contract (it's only used internally for the recipient address), and will be mostly informational to the outside. 

In the recipient case, the `balanceOf` function is used in the `withdraw` function, but the `safeTransfer` will eventually fail to transfer the tokens (assuming a well behaved ERC20 implementation that won't silently fail) if those aren't available in the contract.

However other parts of the protocol (or other protocols) that integrate with this particular function can eventually receive an inaccurate value.

Since the comment attached to the function states the following, the implementation isn't technically correct:

> @notice Returns the available funds to withdraw.

## Code Snippet

https://github.com/sherlock-audit/2022-11-nounsdao/blob/main/src/Stream.sol#L289-L294

```solidity
function balanceOf(address who) public view returns (uint256) {
    uint256 recipientBalance = _recipientBalance();

    if (who == recipient()) return recipientBalance;
    if (who == payer()) {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/30_
