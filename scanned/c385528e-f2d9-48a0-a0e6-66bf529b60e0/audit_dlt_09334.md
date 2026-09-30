# [?] fix: avoid race condition between poll and timeout

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2026-03-05
Source: https://github.com/NomicFoundation/hardhat/commit/d3eef666666cbe4300ad1fdfbc96513e30c25585
Type: security-commit

## Details
fix: avoid race condition between poll and timeout

## Patch
### v-next/hardhat-ethers/src/internal/hardhat-ethers-provider/hardhat-ethers-provider.ts
```diff
@@ -481,21 +481,29 @@ export class HardhatEthersProvider implements HardhatEthersProviderI {
     }
 
     return new Promise<ethers.TransactionReceipt | null>((resolve, reject) => {
+      let cancelled = false;
       let timeoutTimer: NodeJS.Timeout | undefined;
       let pollingTimeout: NodeJS.Timeout | undefined;
 
       if (timeout !== undefined && timeout > 0) {
         timeoutTimer = setTimeout(() => {
+          cancelled = true;
           clearTimeout(pollingTimeout);
           resolve(null);
         }, timeout);
       }
 
       const poll = async () => {
+        if (cancelled) {
+          return;
+        }
+
         try {
           const receipt = await this.getTransactionReceipt(hash);
 
           if (receipt !== null) {
+            cancelled = true;
+
             if (timeoutTimer !== undefined) {
               clearTimeout(timeoutTimer);
             }
@@ -513,6 +521,8 @@ export class HardhatEthersProvider implements HardhatEthersProviderI {
         } catch (e) {
           ensureError(e);
 
+          cancelled = true;
+
           if (timeoutTimer !== undefined) {
             clearTimeout(timeoutTimer);
           }
```
