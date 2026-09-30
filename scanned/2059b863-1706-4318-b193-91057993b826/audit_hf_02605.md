# [M] YieldManager can stake locked funds

## Summary
Severity: Medium
Contest weight: 0.3842
Dataset id: 13996
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the YieldManager component of a cross‑chain bridge that handles L2 withdrawals. When a withdrawal is finalized in the WithdrawalQueue, the corresponding funds become locked – they are earmarked for the user and should only be withdrawable through the queue. However, the two YieldProvider contracts (DSRYieldProvider and LidoYieldProvider) expose a stake(uint256 amount) function that determines whether the requested amount is available by comparing it to the value returned by YIELD_MANAGER.getTokenBalance() (or the older lockedValue() function). This value represents the total token balance held by the YieldManager, which includes both freely available tokens and the locked tokens that are pending user withdrawal. Because the check does not differentiate between locked and unlocked funds, an attacker or any caller can invoke stake with an amount that consumes the locked portion. The call then forwards the amount to the underlying yield protocol (DSR or Lido), effectively moving user‑reserved tokens into a yield‑earning contract. From the user’s perspective the UI may still display a normal balance, but when they attempt to withdraw they receive nothing or experience a zero‑balance error, as the funds have been re‑allocated. The impact is that users lose immediate access to their withdrawn assets; the funds are not destroyed but become trapped in the yield contract until the protocol implements a recovery path, which may never happen. This breach of accounting logic violates the core business assumption that locked funds remain withdrawable and isolates the protocol from its promised liquidity guarantees. The issue was discovered during a manual audit by Spearbit, who noted that the naming of lockedValue and getTokenBalance is ambiguous and that the stake functions lack a proper “available balance” guard. The flaw is subtle because the contract does not emit explicit errors when locked funds are moved, and the balance‑checking code appears superficially correct. To remediate, the stake functions should compare the requested amount against a dedicated available‑balance metric that excludes locked tokens, revert if the amount exceeds that metric, and the naming should be clarified (e.g., rename lockedValue to totalBalance and getTokenBalance to getAvailableBalance). This change restores the invariant that only free tokens can be staked, preserving user withdrawal rights and preventing accidental or malicious fund capture.

## Recommendation
Consider reverting if locked funds are staked:
```solidity
// DSRYieldProvider
/// @inheritdoc YieldProvider
function stake(uint256 amount) external override onlyDelegateCall {
    - uint256 daiBalance = DAI.balanceOf(address(YIELD_MANAGER));
    + uint256 daiBalance = YIELD_MANAGER.getTokenBalance();
    if (amount > daiBalance) {
        revert InsufficientStakableFunds();
    }
    if (amount > 0) {
        DSR_MANAGER.join(address(YIELD_MANAGER), amount);
    }
}

// LidoYieldProvider
/// @inheritdoc YieldProvider
function stake(uint256 amount) external override onlyDelegateCall {
    - if (amount > YIELD_MANAGER.lockedValue()) {
    + if (amount > YIELD_MANAGER.getTokenBalance()) {
        revert InsufficientStakableFunds();
    }
    LIDO.submit{value: amount}(address(0));
}
```
Additionally, consider renaming lockedValue to totalBalance and getTokenBalance to getAvailableBalance or similar names as the current names are ambiguous.
