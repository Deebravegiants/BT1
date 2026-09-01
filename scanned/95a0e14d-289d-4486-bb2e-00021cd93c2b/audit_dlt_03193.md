# [H] Direct theft of buyers ETH funds.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-non-fungible
Published: 2022-11-14
Source: https://github.com/code-423n4/2022-11-non-fungible-findings/issues/96
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-11-non-fungible/blob/323b7cbf607425dd81da96c0777c8b12e800305d/contracts/Exchange.sol#L168
https://github.com/code-423n4/2022-11-non-fungible/blob/323b7cbf607425dd81da96c0777c8b12e800305d/contracts/Exchange.sol#L565
https://github.com/code-423n4/2022-11-non-fungible/blob/323b7cbf607425dd81da96c0777c8b12e800305d/contracts/Exchange.sol#L212
https://github.com/code-423n4/2022-11-non-fungible/blob/323b7cbf607425dd81da96c0777c8b12e800305d/contracts/Exchange.sol#L154


# Vulnerability details

## Impact

Most severe issue: 
**A Seller or Fee recipient can steal ETH funds from the buyer when he is making a single or bulk execution. (Direct theft of funds).**

Additional impacts that can be caused by these bugs:
1. Seller or Fee recipient can cause next in line executions to revert in `bulkExecute` (by altering `isInternal`, insufficient funds, etc..)
2. Seller or Fee recipient can call `_execute` externally 
3. Seller or Fee recipient can set a caller `_remainingETH` to 0 (will not get refunded)

## Proof of Concept
Background:
* The protocol added a `bulkExecute` function that allows multiple orders to execute. The implementation is implemented in a way that if an `_execute` of a single order reverts, it will not break additional or previous successful `_execute`s. It is therefore very important to track actual ETH used by the function. 
* The protocol has recognized the need to track buyers ETH in order to refund unused ETH by implementing the `_returnDust` function and `setupExecution` modifier. This ensures that calls to `_execute` must be internal and have proper accounting of remainingETH. 
* Fee recipient is controlled by the seller. The seller determines the recipients and fee rates.

The new implementations creates an attack vectors that allows the Seller or Fee recipient to steal ETH.

There are three main bugs that can be exploited to steal the ETH:
1. Reentrancy is possible by feeRecipient as long as `_execute` is not called (`_execute` has a reentrancyGuard)
2. `bulkExecute` can be called with an empty parameter. This allows the caller to not enter `_execute` and call `_returnDust`
3. `_returnDust` sends the entire balance of the contract to the caller.

(Side note: I issued the 3 bugs together in this one report in order to show impact and better reading experience for sponsor and judge. If you see fit, these three bugs can be split to three different findings)

There are two logical scenarios where the heist could originate from:
1. Malicious seller: The seller can set the fee recipient to a malicious contract.
2. Malicious fee recipient: fee recipient can steal the funds without the help of the seller. 

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-11-non-fungible-findings/issues/96_
