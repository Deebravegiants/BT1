# [M] execute in VoteProxy should be payable

## Summary
Severity: Medium
Contest weight: 0.6617
Dataset id: 1588
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in a governance proxy contract that provides an `execute` function intended to forward arbitrary calls, optionally with ether, to a target address. The function accepts a `_value` argument and uses low‑level `call{value: _value}` to transfer the supplied amount, but it lacks the `payable` mutability specifier. Because Solidity rejects any transaction that supplies non‑zero ether to a non‑payable function, any attempt to invoke `execute` with `msg.value > 0` will cause the whole call to revert before the internal forwarding logic runs. The root cause is a mismatch between the intended behavior (acting as a payable proxy) and the function’s declaration, which does not permit receiving ether. Exploitation does not require sophisticated tooling; a user simply calls `execute` with a non‑zero value, either intentionally to forward funds or inadvertently by sending ether along with the transaction. When this occurs, the transaction reverts, the forwarded call never executes, and any expected state changes or fund transfers are aborted. From a functional perspective, this means that proposals or administrative actions that rely on moving ether through the proxy cannot succeed, leading to a broken governance flow. Users observing the UI may see that their transaction fails with a generic revert message, that no funds are transferred, or that a proposal that should have executed remains pending. The issue was discovered during a manual audit of the contract’s source code, where the auditor noticed the absence of the `payable` keyword despite the presence of a value‑forwarding call. The bug can be subtle because the function compiles without warnings and the call pattern appears correct; only when a non‑zero ether amount is supplied does the revert surface. To remediate, the function should be marked as `payable`, allowing it to accept ether and forward it as intended. Conceptually, the fix aligns the function’s signature with its purpose as a value‑forwarding proxy, restoring the expected business logic that funds can be moved through the governance contract. This class of problem falls under "missing payable modifier" or "incorrect function mutability", a common source of runtime reverts that break financial flows in smart contracts.

## Proof of Concept
Lacking `payable` mutability specifier.

[VoteProxy.sol#L28-L35](https://github.com/code-423n4/2022-02-concur/blob/main/contracts/VoteProxy.sol#L28-L35)  
```solidity
        function execute(
            address _to,
            uint256 _value,
            bytes calldata _data
        ) external onlyOwner returns (bool, bytes memory) {
            (bool success, bytes memory result) = _to.call{value: _value}(_data);
            return (success, result);
        }
```

## Recommendation
```solidity
Add `payable` mutability specifier.
```
@leekt Can you tell me what you’d need [`execute`](https://github.com/code-423n4/2022-02-concur/blob/72b5216bfeaa7c52983060ebfc56e72e0aa8e3b0/contracts/VoteProxy.sol#L28) to be used for?

Do you really need it to be payable?

After some thinking, I do believe that it would be wise to allow for payable calls.

Will mark as valid and because this is contingent on a specific usage, I think Medium Severity to be appropriate.
