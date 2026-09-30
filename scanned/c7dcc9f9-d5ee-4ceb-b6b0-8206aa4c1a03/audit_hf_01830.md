# [M] Incorrect amount taken

## Summary
Severity: Medium
Contest weight: 0.1479
Dataset id: 10194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the repayment pathway of the CNote contract, specifically within the repayBorrowFresh function. When a borrower attempts to clear their debt, the contract expects a special sentinel value – type(uint).max – to signal a full repayment. The implementation, however, mistakenly uses the original repayAmount variable when calling the token transfer routine, rather than the calculated repayAmountFinal that represents the actual outstanding balance. This mismatch means that, in a full‑repayment scenario, the contract will try to transfer the maximum possible uint256 value (2^256‑1 tokens) instead of the precise amount owed. The root cause is an oversight in handling the sentinel value, leading to an incorrect transfer amount being passed to doTransferIn. An attacker or a careless user can trigger this condition simply by submitting a repayment request with the max uint sentinel, causing the contract to attempt an absurdly large token transfer. The EVM will revert the transaction due to insufficient balance, resulting in a denial‑of‑service for the borrower who cannot repay and may face liquidation. In a less defensive token implementation, the contract could actually move an excessive amount of tokens, effectively stealing funds from the user. The issue manifests only when the repayAmount equals type(uint).max, which is a common pattern for indicating "pay everything" in DeFi protocols, making it easy to overlook during code review. All borrowers of the CNote protocol are affected because they rely on the repayment function to settle their loans; the protocol itself is at risk of reputation damage and potential loss of liquidity. The problem was identified during a Code4rena audit through manual inspection of the repayment logic and a proof‑of‑concept that demonstrated the faulty call to doTransferIn with repayAmount. Because the bug results in a revert rather than a silent loss, it can be subtle to notice during normal operation, especially if the contract rarely processes full‑repayment requests. To remediate, the contract must replace the call to doTransferIn with the correctly calculated repayAmountFinal (or store the transferred amount in actualRepayAmount) so that only the exact debt is transferred. This aligns the implementation with the intended business logic that a borrower should never be charged more than the amount they owe, preserving accounting integrity and preventing unexpected zero balances or failed repayments.

## Proof of Concept
1. User is making a repayment which eventually calls repayBorrowFresh function
  2. Assuming repayAmount == type(uint).max, so repayAmountFinal becomes accountBorrowsPrev
  3. This means User should only transfer in accountBorrowsPrev instead of repayAmount but that is not true. Contract is transferring repayAmount instead of repayAmountFinal as seen at CNote.sol#L129

    uint actualRepayAmount = doTransferIn(payer, repayAmount);

## Recommendation
Revise CNote.sol#L129 to below:
    
    uint actualRepayAmount = doTransferIn(payer, repayAmountFinal);

The warden has showed how, due to an oversight, using `type(uint).max` to signify a complete repayment will actually attempt to transfer 2^256-1 units of token.

While I think High severity would have been reasonable had the tokens gotten transferred, because what will actually happen is a revert, I think Medium Severity to be more appropriate.

Remediation requires using `actualRepayAmount` or re-assigning the value of `repayAmount`
