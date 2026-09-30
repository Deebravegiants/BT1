# [M] Pre-check is not correct

## Summary
Severity: Medium
Contest weight: 0.1240
Dataset id: 15131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability lies in an overly restrictive pre‑condition that guards the `fillCriteriaBid` function. The contract checks that the total amount offered (`o.totalAmt`) must be greater than or equal to the sum of the exchange payment amount (`o.exchange.paymentAmt`) and the pre‑payment amount (`o.prePayment.paymentAmt`). This check is applied regardless of whether a referral amount is present and whether the referral address is set. When a bid includes a non‑zero referral amount (`o.refererrAmt > 0`) but the `referrer` address is the zero address, the arithmetic relationship can satisfy the internal settlement logic (`_settleBalances`) while simultaneously violating the pre‑check. Specifically, if `o.refererrAmt` exceeds `(p.paymentAmt + protocolfee) / amount`, the condition `o.totalAmt < o.exchange.paymentAmt + o.prePayment.paymentAmt + o.refererrAmt` can be true even though the later expression `(o.totalAmt - protocolfee - o.exchange.paymentAmt - o.prePayment.paymentAmt) * amount - p.paymentAmt >= 0` holds. As a result, `fillCriteriaBid` reverts on a transaction that would otherwise execute correctly, breaking the protocol’s bidding flow.

The root cause is a logical error in the pre‑validation logic: it does not account for the special case where a referral amount is present but the referrer address is unset. By insisting that the total amount cover the referral component, the check mistakenly rejects valid bids. The issue was discovered during a static audit where the analyst examined the conditional statements around line 342 and constructed a concrete scenario that triggered the mismatch.

From a user’s perspective, the symptoms are a sudden transaction revert with no obvious reason – the user attempts to place a bid that includes a small referral fee, expects the transaction to succeed, but receives a generic revert error and sees no change in their balance. The protocol appears to lose functionality because legitimate bids are silently blocked, potentially leading to missed trading opportunities and reduced liquidity.

The impact is primarily functional: it creates a denial‑of‑service condition for a subset of bids that meet the described arithmetic criteria. While funds are not directly stolen, the protocol’s economic model is undermined because users cannot rely on the bid mechanism working as documented. In worst‑case scenarios, an attacker could deliberately craft transactions that trigger the faulty pre‑check, preventing competitors from bidding and biasing market outcomes.

The vulnerability manifests only under the combined conditions of a positive referral amount, a zero‑address referrer, and a specific relationship between the referral amount, payment amount, protocol fee, and the scaling factor `amount`. Outside of these edge cases, the contract behaves as intended, which makes the bug hard to notice during standard testing that does not cover zero‑address referral scenarios.

To remediate the problem, the pre‑check should be revised to compare the total amount only against the exchange payment and pre‑payment amounts, i.e., `require(o.totalAmt >= o.exchange.paymentAmt + o.prePayment.paymentAmt)`. This aligns the guard with the actual requirements of the settlement logic and restores correct execution for bids that include referrals with an unset referrer. Implementing the corrected condition will prevent unnecessary reverts, preserve protocol functionality, and eliminate the denial‑of‑service vector introduced by the original check.

## Proof of Concept
When `refererrAmt > 0` and `referrer` address is not set (is 0), `(o.totalAmt - protocolfee - o.exchange.paymentAmt - o.prePayment.paymentAmt) * amount - p.paymentAmt >= 0` and `o.totalAmt < o.exchange.paymentAmt + o.prePayment.paymentAmt + o.refererrAmt` can hold true at the same time.

It is when `o.refererrAmt > (p.paymentAmt + protocolfee) / amount`.  
In that case, `_settleBalances` can work, but fillCriteriaBid will be reverted due to the check in line 342.

## Recommendation
I think `require(o.totalAmt >= o.exchange.paymentAmt + o.prePayment.paymentAmt)` is correct.

Nice catch.

This tracks as a medium for me… it breaks protocol functionality given external factors.
