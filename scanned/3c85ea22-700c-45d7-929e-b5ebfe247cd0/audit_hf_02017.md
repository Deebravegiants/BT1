# [M] Calls To `Swivel.initiate

## Summary
Severity: Medium
Contest weight: 0.2062
Dataset id: 11495
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Swivel `lend()` does not validate the `o.exit` and `o.vault` for each order before making the external call to Swivel. These values determine which internal functions is [called in Swivel](https://github.com/Swivel-Finance/swivel/blob/2471ea5cda53568df5e5515153c6962f151bf358/contracts/v2/swivel/Swivel.sol#L64-L77).

The intended code path is `initiateZcTokenFillingVaultInitiate()` which takes the underlying tokens and mints zcTokens to the `Lender`. If one of the other functions is called the accounting in `lend()`. Swivel may transfer more tokens from `Lender` to `Swivel` than paid for by the caller of `lend()`.

The impact is that underlying tokens may be stolen from `Lender`.

## Proof of Concept
Consider the example where [initiateZcTokenFillingZcTokenExit()](https://github.com/Swivel-Finance/swivel/blob/2471ea5cda53568df5e5515153c6962f151bf358/contracts/v2/swivel/Swivel.sol#L162) is called. This will transfer `a - premiumFilled + fee` from `Lender` to `Swivel` rather than the expected `a + fee`.

## Recommendation
In `lend()` restrict the values of `o.exit` and `o.vault` so only one case can be triggered in `Swivel.initiate()`.

While it is true that a user could get better execution by submitting certain orders, we don’t think this is a problem. Invalid orders would be rejected by Swivel, and users should be free to execute the best possible orders.

So reviewing this, there is an issue though it may not be high-risk.

The user _can_ manipulate the method by sending it an order that is not the correct type to go down the intended order path.

That said, the result on line [297](https://github.com/code-423n4/2022-06-illuminate/blob/912be2a90ded4a557f121fe565d12ec48d0c4684/lender/Lender.sol#L297) is still that the calculated lent value is sent to the contract.

So the result is that the user inputting this manipulation actually still pays for their iPTs, and their underlying just sits in lender.sol until maturity with no personal benefit. The attack would none-the-less leak value and with that in mind I’d probably just drop it down to medium?

Judging as Med Risk as no fund is lost (after maturity).
