# [H] Malformed equate statement

## Summary
Severity: High
Contest weight: 0.5405
Dataset id: 20613
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains two access‑control modifiers that are intended to restrict function execution to privileged accounts, but the implementation is flawed. Each modifier evaluates a boolean expression – `msg.sender == owner` for the onlyOwner modifier and `managers[msg.sender] == true` for the onlyManager modifier – without using a require or revert statement. Because the expression result is not checked, the modifiers do not enforce any restriction; they simply compute a value that is discarded. This logical omission means that any address can call functions guarded by these modifiers, effectively bypassing the intended ownership or manager checks. An attacker can exploit the bug by invoking a protected function directly; the transaction will not revert even if the caller is not the owner or a registered manager. The impact is severe: privileged operations such as fund withdrawals, parameter changes, or administrative actions can be performed by unauthorized parties, leading to potential loss of assets, protocol state corruption, or complete takeover of contract governance. The vulnerability manifests whenever a function is marked with onlyOwner or onlyManager, which is common in contracts that rely on role‑based access control. All users of the contract, as well as the protocol operators, are affected because the security guarantees promised by the contract’s interface are broken. The issue was discovered during a manual audit review where the modifier bodies were inspected and found to lack a require statement. It can be hard to notice because the syntax looks superficially correct – the modifiers are declared and referenced – yet the missing require is a subtle logical error that does not produce a compiler warning. From a user’s perspective, actions that should be restricted (for example, only the owner can pause the contract or withdraw fees) appear to work for any address, leading to unexpected behavior such as unauthorized withdrawals or configuration changes. The bug violates the fundamental business logic that only trusted roles may perform sensitive operations, breaking accounting assumptions and trust in the system. The recommended remediation is to replace the bare equality checks with explicit require statements that revert when the caller is not authorized, thereby restoring proper access control enforcement.

## Recommendation
To fix this, the modifier should enforce the ownership check using a `require` statement:
    
    modifier onlyOwner() {
      require(msg.sender == owner, "Caller is not the owner");
      _;
    }

With this correction, the modifier effectively ensures that only the account designated as `owner` can access the function. If a non-owner attempts to call the function, the transaction is reverted, maintaining the intended access control and contract integrity.
    
    ```solidity
    8:     modifier onlyOwner() { // <= FOUND
    9:         msg.sender == owner; // <= FOUND
    10:         _;
    11:     }
    
    13:     modifier onlyManager() { // <= FOUND
    14:         managers[msg.sender] == true; // <= FOUND
    15:         _;
    16:     }
    ```
