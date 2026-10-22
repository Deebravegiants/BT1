# [M] User will lose funds

## Summary
Severity: Medium
Contest weight: 0.5961
Dataset id: 5225
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the claim‑extra logic of the AuraClaimZap contract. When a user invokes the claimRewards function with the lock‑CVX option disabled, the contract still evaluates the depositCvxMaxAmount condition, calculates the user’s CVX balance, and proceeds to pull the CVX tokens from the caller via safeTransferFrom. Only after the transfer does the contract check the Options.LockCvx flag to decide whether to lock the received CVX. Because the transfer happens before the flag is evaluated, a false flag results in the CVX being moved into the contract without any subsequent locking or redistribution step. Consequently, the transferred tokens become permanently trapped in the contract’s balance, effectively disappearing from the user’s perspective. The root cause is a missing guard or else clause that should prevent the token pull when the lock option is not selected, or at least revert the transaction after a failed lock condition. The bug can be exploited simply by a user calling claimRewards with Options.LockCvx set to false while still having a positive CVX balance and a non‑zero depositCvxMaxAmount. The contract then executes the transfer, the lock call is skipped, and the user’s CVX remains locked inside the contract with no mechanism to retrieve it. The impact is a direct loss of funds for any user who follows this specific call pattern; the protocol as a whole is not compromised because no external actor can force another user’s funds into this state. The issue manifests only under the precise condition that the caller supplies a false lock flag while the contract’s internal deposit limit permits a positive CVX pull. It was discovered during a manual audit that traced the execution path of claimRewards and noted the absence of a revert or alternative handling after the lock check. The problem can be difficult to notice because the transaction does not fail – it succeeds, but the user’s token balance on the frontend shows a reduction with no corresponding reward or locked position, which may be mistaken for a normal fee or burn. To fix the issue, the contract should verify the Options.LockCvx flag before initiating the safeTransferFrom, or it should include an explicit else branch that either refunds the transferred CVX or reverts the transaction if the lock is not requested. This aligns the implementation with the intended business logic that CVX may only be transferred when the user explicitly opts into locking, preserving accounting consistency and preventing accidental fund disappearance.

## Proof of Concept
1. User call claimRewards at ClaimZap.sol#L103 with Options.LockCvx as false
2. claimRewards internally calls _claimExtras
3. Everything goes good until AuraClaimZap.sol#L218

```solidity
if (depositCvxMaxAmount > 0) {
    uint256 cvxBalance = IERC20(cvx).balanceOf(msg.sender).sub(removeCvxBalance);
    cvxBalance = AuraMath.min(cvxBalance, depositCvxMaxAmount);
    if (cvxBalance > 0) {
        //pull cvx
        IERC20(cvx).safeTransferFrom(msg.sender, address(this), cvxBalance);
        if (_checkOption(options, uint256(Options.LockCvx))) {
            IAuraLocker(locker).lock(msg.sender, cvxBalance);
        }
    }
}
```

4. Since user cvxBalance>0 so cvxBalance is transferred from user to the contract.
5. Now since Options.LockCvx was set to false in options so if (_checkOption(options, uint256(Options.LockCvx))) does not evaluate to true and does not execute
6. This means User cvx funds are stuck in contract

## Recommendation
The condition should check if user has enabled lock for cvx, otherwise cvx should not be transferred from user

```solidity
if (depositCvxMaxAmount > 0 && _checkOption(options, uint256(Options.LockCvx))) {
    uint256 cvxBalance = IERC20(cvx).balanceOf(msg.sender).sub(removeCvxBalance);
    cvxBalance = AuraMath.min(cvxBalance, depositCvxMaxAmount);
    if (cvxBalance > 0) {
        //pull cvx
        IERC20(cvx).safeTransferFrom(msg.sender, address(this), cvxBalance);

        IAuraLocker(locker).lock(msg.sender, cvxBalance);
    }
}
```

This is valid, although it:

* relies on user function input
* does not affect user deposits
* requires pre-approval of tokens

Therefore, I don’t think this should be a 3 severity. 2 at most.

This is a tough one, but I agree that medium severity makes more sense here since we’re talking about a user acting on their own behalf in a very specific way. This does not open up an attack vector which would allow a malicious actor to lock a user’s funds.

[0xMaharishi (Aura Finance) resolved](https://github.com/code-423n4/2022-05-aura-findings/issues/108):

[code4rena aurafinance/aura-contracts#84](https://github.com/aurafinance/aura-contracts/pull/84)  
[All code4rena fixes code-423n4/2022-05-aura#6](https://github.com/code-423n4/2022-05-aura/pull/6)
