# [?] fix: walletconnect will crash when retry as safe admin (#1291)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2023-03-29
Source: https://github.com/RabbyHub/Rabby/commit/0802ceec6f31678767c87f5099a653eff0e8d34b
Type: security-commit

## Details
fix: walletconnect will crash when retry as safe admin (#1291)

## Patch
### src/ui/views/Approval/components/WatchAddressWaiting.tsx
```diff
@@ -349,7 +349,9 @@ const WatchAddressWaiting = ({ params }: { params: ApprovalParams }) => {
   };
 
   const handleRetry = async () => {
-    const account = (await wallet.syncGetCurrentAccount())!;
+    const account = params.isGnosis
+      ? params.account!
+      : (await wallet.syncGetCurrentAccount())!;
     await wallet.killWalletConnectConnector(account.address, account.brandName);
     await initWalletConnect();
     setConnectStatus(WALLETCONNECT_STATUS_MAP.PENDING);
```
