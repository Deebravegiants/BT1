# [H] H-02 Unmitigated

## Summary
Severity: High
Chain: Smart contract
Component: 2024-09-karak-mitigation
Published: 2024-09-12
Source: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/8
Type: code-finding

## Details
# Lines of code

https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/NativeVault.sol#L81


# Vulnerability details

### H-02:**The operator can create a `NativeVault` that can be silently unslashable.**

[Link to issue](https://github.com/code-423n4/2024-07-karak-findings/issues/55)

## **Comments**

The original implementation allows operators to set `manager`, `slashStore`, and `nodeImplementation` to arbitrary values. This flexibility enables operators to create an unslashable vault by setting the `slashStore` to an address other than the whitelisted slashing handler for ETH

## **Mitigation**

 [Fix link](https://github.com/karak-network/karak-arena-mitigations/commit/fdef9d25e2b7c0a528d5a6dfcce64a3a518165af#diff-940446432243a929cd0f5ea691c4e90d60ee655723e2d5d8fcafc7b7504cfe98R429)

The mitigation does not fully address all potential risks:

- The `slashStore` issue has been correctly handled by removing the component.
- The initial `nodeImplementation` appears acceptable, as users and the DSS owner can review it before joining the vault.

However, a vulnerability remains with the `manager` role. The manager, designated by the operator during deployment, retains the ability to call the `changeNodeImplementation` function and change the implementation to anything without delay. 

This setup could lead to a scenario where a vault, initially functioning correctly and trusted by users, becomes rogue as the operator or manager updates the implementation to a malicious version without warning.

```solidity
    /// @notice Allows the owner to change the NativeNode implementation and upgrade all NativeNodes
    /// @param newNodeImplementation: The address of the new node implementation
    function changeNodeImplementation(address newNodeImplementation)
        external
        onlyOwnerOrRoles(Constants.MANAGER_ROLE)
        whenFunctionNotPaused(Constants.PAUSE_NATIVEVAULT_NODE_IMPLEMENTATION)
    {
        if (newNodeImplementation == address(0)) revert ZeroAddress();

        _state().nodeImpl = newNodeImplementation;
        emit UpgradedAllNodes(newNodeImplementation);
    }
```

## **Recommended additional mitigation:**

A viable solution to further protect users is to modify the `changeNodeImplementation` function to incorporate a request-and-finalize change process, where any proposed changes to the node implementation must go through a time-locked approval phase. This approach allows users who disagree with the proposed changes or detect a potentially malicious implementation to withdraw their funds before the update is finalized. 

- The time lock should exceed the withdrawal time lock, providing users sufficient time to exit safely.

This solution allows operators to update the node implementation while protecting users from unexpected and potentially harmful changes, maintaining trust and security within the system.
