# [M] [M-10] mitigation error

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/61
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Guard.sol#L399-L407


# Vulnerability details

## Vulnerability
The original vulnerability constituted the ability of rental safe owners to indefinitely use an outdated guard policy contract, even after a newer version has been deployed. This situation arises because the protocol lacked a mechanism to enforce the update of guard policies across all safes, potentially leaving some safes operating under less secure or outdated policies.

## Mitigation
The mitigation introduces a protocol-wide capability to deactivate guard policies, aiming to prevent the continued use of outdated or insecure policies. However, this solution inadvertently introduced a new vulnerability: the potential for "bricking" rental safes if their associated guard policy is deactivated without providing a viable path for these safes to update to a new guard policy.

The only way for a safe owner to update the guard, if the one they are using becomes inactive, would be via a whitelisted DelegateCall, in the same manner as they would upgrade the Stop policy as described in the contest [documentation](https://github.com/code-423n4/2024-01-renft/blob/main/docs/protocol-whitelists.md#delegate-call-whitelist). However, the current implementation triggers a revert when a Guard policy is not active, before they can potentially execute a DelegateCall to upgrade the guard.

## Suggestion
Allow inactive guards to call whitelisted delegates. A potential implementation could look as follows:
```diff
diff --git a/src/policies/Guard.sol b/src/policies/Guard.sol
index c7823ca..1e94943 100644
--- a/src/policies/Guard.sol
+++ b/src/policies/Guard.sol
@@ -395,17 +395,22 @@ contract Guard is Policy, BaseGuard {
         bytes memory,
         address
     ) external override {
+        // Disallow transactions that use delegate call, unless explicitly
+        // permitted by the protocol.
+        if (operation == Enum.Operation.DelegateCall){
+            if (!STORE.whitelistedDelegates(to)) {
+                revert Errors.GuardPolicy_UnauthorizedDelegateCall(to);
+            } else {
+                // no need to check the transaction if it is to a whitelisted delegate
+                return;
+            }
+        }
+
         // Check if this guard is active for the protocol.
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/61_
