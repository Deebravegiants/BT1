# [H] Admin Can Bypass Checks for Privileged Modules

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-09
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/77
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xd6ef0f1df575f57412c35b4ac1f81ecd4a27c17442794d7f783110a31972640c
**Severity:** high

**Description:**
**Description**:
When an admin wants to add a new module to the orchestrator, if the module is `IFundingManager_v1`, `IAuthorizer_v1`, or `IPaymentProcessor_v1`, it must pass `_enforcePrivilegedModuleInterfaceCheck` and an additional check. The issue here is that the admin can bypass these checks.

**Scenario**:
1. The admin calls `initiateSetFundingManagerWithTimelock` and passes the check:
    ```solidity
    _enforcePrivilegedModuleInterfaceCheck(
        fundingManagerContract, fundingManagerInterfaceId
    );

    if (fundingManager.token() != fundingManager_.token()) {
    ```
2. The admin calls `cancelFundingManagerUpdate` (just cancel adding a new module)
3. The admin calls `initiateAddModuleWithTimelock` with a new funding manager module address. (bypass checks here)
4. The admin calls `executeSetFundingManager`.

**Impact**:
The admin can bypass important checks and gain more control over the system than it should.

**Mitigation**:

Ensure `cancelFundingManagerUpdate` also cancels the module removal process.
```diff
    function cancelFundingManagerUpdate(IFundingManager_v1 fundingManager_)
        external
        onlyOrchestratorAdmin
    {
        _cancelModuleUpdate(address(fundingManager_));
+        _cancelModuleUpdate(address(fundingManager));
    }
```
