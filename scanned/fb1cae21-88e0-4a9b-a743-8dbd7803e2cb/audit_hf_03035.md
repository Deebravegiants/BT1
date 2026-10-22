# [H] Call to `declareInsolvent`

## Summary
Severity: High
Contest weight: 0.3258
Dataset id: 17017
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The modifier `whileBorrowing()` is used along in the call to LineOfCredit.declareInsolvent(). However this check reverts when count == 0 or `credits[ids[0]].principal == 0` . Within the contract, any lender can add credit which adds an entry in credits array, credits[ids].

Assume, when borrower chooses lender positions including credits[ids[0]] to draw on, and repays back the loan fully for credits[ids[1]], then the call to declareInsolvent() by the arbiter would revert since it does not pass the `whileBorrowing()` modifier check due to the ids array index shift in the call to stepQ(), which would shift ids[1] to ids[0], thereby making the condition for `credits[ids[0]].principal == 0` be true causing the revert.

## Proof of Concept
1. LineOfCredit contract is set up and 5 lenders have deposited into the contract.
2. Alice, the borrower borrows credit from these 5 credit positions including by calling `LineOfCredit.borrow()` for the position ids.
3. Later Alice pays back the loan for credit position id 1 just before the contract gets liquidated.
4. At the point where `ids.stepQ()` is called in `\_repay()`, position 1 is moved to ids[0]
5. When contract status is LIQUIDATABLE, no loan drawn on credit position 0 and arbiter calls declareInsolvent() , the call would revert since `credits[ids[0]].principal == 0`

## Recommendation
The modifier `whileBorrowing()` would need to be reviewed and amended.
