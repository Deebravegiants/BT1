# [H] Overly restrictive balance consistency check in TotalBalanceChange class of enforcers can cause potential DoS

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23363
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TotalBalanceChange class of enforcers contain a defensive check in beforeAll hook that can cause DoS attacks in cross‑execution batch scenarios and prevents legitimate balance‑modifying enforcers from being used.  
The issue stems from overly restrictive validation that assumes balance immutability during the beforeAll hook phase.

```solidity
function beforeAllHook(...) public override {
    // ... setup code ...
    uint256 currentBalance_ = IERC20(token_).balanceOf(recipient_);
    if (balanceTracker_.expectedDecrease == 0 && balanceTracker_.expectedIncrease == 0) {
        balanceTracker_.balanceBefore = currentBalance_;
        emit TrackedBalance(msg.sender, recipient_, token_, currentBalance_);
    } else {
        // @audit Overly restrictive check can prevent legitimate enforcers
        require(balanceTracker_.balanceBefore == currentBalance_,
            "ERC20TotalBalanceChangeEnforcer:balance-changed");,!
    }
    // ...
}
```

The check above assumes that there would not be any enforcers that can change state in the beforeAll hook.  
Imagine a prepaymentEnforcer implemented in the future that requires upfront token transfer before execution (e.g., fees or collateral moved to an escrow account) – current balance validation will make the TotalBalanceChange enforcers incompatible with such enforcers.

Consider the following batch execution scenario:  

1. Exec1 TotalBalanceChangeEnforcer.beforeAllHook: Sets `balanceBefore` = Alice's current balance  
2. Exec2 PrepaymentEnforcer.beforeAllHook: Collects 1 ETH from Alice → Alice balance changes  
3. Exec2 TotalBalanceChangeEnforcer.beforeAllHook: `require(old_balance == new_balance)` → REVERT  
4. Entire batch transaction fails  

Impact: Overly restrictive validation can DoS entire batch transactions when specific enforcer combinations are at play.

## Recommendation
Consider replacing the restrictive balance consistency check with simple overwriting. Overwriting would mean that the last TotalBalanceChangeEnforcer becomes the baseline for all afterAllHook operations. Current balance check is not adding any value from a "security" standpoint but adds DoS and enforcer incompatibility risks.

```solidity
function beforeAllHook(...) public override {
    // ... setup code ...
    uint256 currentBalance_ = IERC20(token_).balanceOf(recipient_);
    if (balanceTracker_.expectedDecrease == 0 && balanceTracker_.expectedIncrease == 0) {
        balanceTracker_.balanceBefore = currentBalance_;
        emit TrackedBalance(msg.sender, recipient_, token_, currentBalance_);
    } else {
        // @audit Update baseline to current balance instead of requiring equality
        balanceTracker_.balanceBefore = currentBalance_;
    }
    // ...
}
```
