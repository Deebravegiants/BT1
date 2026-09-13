# [H] Admin Can Bypass Important Checks and Timelock Mechanism

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-09
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/78
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x97dd6e2f45b62becf0ad8c03012469d46862ec64fad47ab8f5f39daad6c9bc2b
**Severity:** high

**Description:**
**Description**:
The admin can bypass `_enforcePrivilegedModuleInterfaceCheck` checks and other important checks and Timelock. The issue arises because `executeSetAuthorizer`, `executeSetFundingManager`, and `executeSetPaymentProcessor` do not verify that the provided address matches the one specified in `initiateSetAuthorizerWithTimelock`, `initiateSetFundingManagerWithTimelock`, and `initiateSetPaymentProcessorWithTimelock`.

**Scenario 1**:
1. The admin calls `initiateSetAuthorizerWithTimelock` with address A.
2. The admin calls `initiateAddModuleWithTimelock` (without any check) with address B.
3. The admin calls `executeSetAuthorizer` with address B.

**Impact**:
The admin can bypass important checks, potentially gaining more control over the system than intended and compromising the system's integrity and security.

**Scenario 2**:
1. The admin calls `initiateAddModuleWithTimelock` with address B on day 1.
2. The admin calls `initiateSetAuthorizerWithTimelock` with address A on day 4.
3. The admin calls `cancelAuthorizerUpdate` with address A.
4. This notifies users that the authorization update is canceled and if users want to add a new authorizer, they must call `initiateSetAuthorizerWithTimelock` and wait for 72 hours.
5. Whenever the admin wants, they can call `executeSetAuthorizer` with address B, without calling `initiateSetAuthorizerWithTimelock`.

**Impact**:
The admin can bypass the timelock mechanism, as they do not need to call `initiateSetAuthorizerWithTimelock` again.

**Mitigation**:
Ensure that the address provided in `executeSetAuthorizer`, `executeSetFundingManager`, and `executeSetPaymentProcessor` is the same as the one specified in `initiateSetAuthorizerWithTimelock`, `initiateSetFundingManagerWithTimelock`, and `initiateSetPaymentProcessorWithTimelock`.
