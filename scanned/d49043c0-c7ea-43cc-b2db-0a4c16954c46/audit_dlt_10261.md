# [?] fix: AddChain crash (#1271)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2023-02-26
Source: https://github.com/RabbyHub/Rabby/commit/7e8c01c7643eb1ad08f9ef543e0f2c1e4ad30249
Type: security-commit

## Details
fix: AddChain crash (#1271)

## Patch
### src/ui/views/Approval/components/AddChain.tsx
```diff
@@ -121,7 +121,7 @@ const AddChain = ({ params }: { params: AddChainProps }) => {
   const init = async () => {
     const site = await wallet.getConnectedSite(session.origin)!;
     setDefaultChain(site?.chain || null);
-    if (rpcUrls.length > 0) {
+    if (rpcUrls?.length > 0) {
       setRpcUrl(rpcUrls[0]);
     }
     setInited(true);
```
