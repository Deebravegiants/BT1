# [?] fix: switch chain crashed (#1671)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2023-08-18
Source: https://github.com/RabbyHub/Rabby/commit/e1a2f452fa6c747ca91991ffafda77b642bbfc24
Type: security-commit

## Details
fix: switch chain crashed (#1671)

## Patch
### src/background/service/notification.ts
```diff
@@ -287,7 +287,9 @@ class NotificationService extends Events {
           : undefined;
 
         const isSwitchMainOrTest =
-          chain && currentChain && chain.isTestnet !== currentChain.isTestnet;
+          chain &&
+          currentChain &&
+          !!chain.isTestnet !== !!currentChain.isTestnet;
 
         if (!isSwitchMainOrTest && chain) {
           this.resolveApproval(null);
```
