# [M] DoS in `initiateSetFundingManagerWithTimelock`, `initiateSetAuthorizerWithTimelock`, `initiateSetPaymentProcessorWithTimelock` Due to Module Limit

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/56
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0xeb12709a8a8dda461393c9a6bdfe561bfdc7289d9404bd90b585218a68f12381
**Severity:** medium

**Description:**
**Description**:
The `initiateSetFundingManagerWithTimelock`, `initiateSetAuthorizerWithTimelock`, and `initiateSetPaymentProcessorWithTimelock` functions add a new module and remove the old module without changing the length of the modules. However, if the modules length has reached the maximum limit, these functions will revert. The owner would then need to remove a module first to replace these modules, which introduces a delay due to the additional timelock required for the module removal.

**Impact**

This issue can cause a Denial of Service (DoS) in the `initiateSetFundingManagerWithTimelock`, `initiateSetAuthorizerWithTimelock`, and `initiateSetPaymentProcessorWithTimelock` functions. The owner must remove a module before calling these functions, and they must wait an additional timelock period for the second module to be deleted.

**Mitigation**

To mitigate this issue, the `moduleLimitNotExceeded` check should not be applied to these three functions since they remove one module and add another one, thus maintaining the same length of modules.
