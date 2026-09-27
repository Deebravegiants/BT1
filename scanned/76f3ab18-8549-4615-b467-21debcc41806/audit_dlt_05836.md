# [?] fix: Address permission delegation vulnerability (#5825)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2025-10-31
Source: https://github.com/XRPLF/rippled/commit/fa6991812471bdde0d771754e8b7e688d774c81f
Type: security-commit

## Details
fix: Address permission delegation vulnerability (#5825)

This change introduces the `featurePermissionDelegationV1_1` amendment, which is designed to supersede both `featurePermissionDelegation` and `fixDelegateV1_1 amendments, which should be considered deprecated. The `checkPermission` function will now return `terNO_DELEGATE_PERMISSION` when a delegate transaction lacks the necessary permissions.
