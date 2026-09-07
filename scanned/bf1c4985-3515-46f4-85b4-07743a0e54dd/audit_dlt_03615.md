# [M] H-04 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-karak-mitigation
Published: 2024-09-12
Source: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/6
Type: code-finding

## Details
# Lines of code

https://github.com/karak-network/karak-arena-mitigations/blob/475cfd73744cabe239720feec4a227a739910119/src/Core.sol#L261


# Vulnerability details

### H-04: **Violation of Invariant Allowing DSSs to Slash Unregistered Operators**

[Link to issue](https://github.com/code-423n4/2024-07-karak-findings/issues/4)

## **Comments**

The original implementation does not account for cases where an operator unregisters from a vault before a pending slash is finalized. This oversight allows slashing to occur on unregistered operators, violating the protocol's invariant that only registered operators should be subject to slashing.

## **Mitigation**

 [Fix link](https://github.com/karak-network/karak-arena-mitigations/commit/69644a7b1c3607aea5f876d9ee6be24035c1d9d2)

The mitigation addresses the issue by incorporating the `checkIfOperatorIsRegInRegDSS` function into the `finalizeSlashing` process. This ensures that the function checks whether the operator is still registered in the relevant DSS before finalizing the slash.

```solidity
    function finalizeSlashing(SlasherLib.QueuedSlashing memory queuedSlashing)
        external
        nonReentrant
        whenFunctionNotPaused(Constants.PAUSE_CORE_FINALIZE_SLASHING)
    {
        CoreLib.Storage storage self = _self();
        self.checkIfOperatorIsRegInRegDSS(queuedSlashing.operator, queuedSlashing.dss);
        self.finalizeSlashing(queuedSlashing);

        emit FinalizedSlashing(msg.sender, queuedSlashing);
    }
```

## **New issue**

The current mitigation introduces a new issue: when a slash is requested, the count of queued slashes for that vault is incremented. However, if the `finalizeSlashing` function reverts due to an operator being unregistered, the queued slash remains unaddressed, leading users to believe there are pending slashes when calling `isVaultQueuedForSlashing.` This situation may act as a deterrent for new deposits, as users would assume a pending slash.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-karak-mitigation-findings/issues/6_
