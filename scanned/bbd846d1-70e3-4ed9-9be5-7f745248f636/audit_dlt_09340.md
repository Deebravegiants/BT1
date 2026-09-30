# [?] Fix NoneManager race condition (#3812, #3813).

## Summary
Severity: Unknown
Chain: Tooling
Component: ethers-io/ethers.js
Published: 2023-02-23
Source: https://github.com/ethers-io/ethers.js/commit/5a3c10a29c047609a50828adb620d88aa8cf0014
Type: security-commit

## Details
Fix NoneManager race condition (#3812, #3813).

## Patch
### src.ts/providers/signer-noncemanager.ts
```diff
@@ -36,7 +36,9 @@ export class NonceManager extends AbstractSigner {
             if (this.#noncePromise == null) {
                 this.#noncePromise = super.getNonce("pending");
             }
-            return (await this.#noncePromise) + this.#delta;
+
+            const delta = this.#delta;
+            return (await this.#noncePromise) + delta;
         }
 
         return super.getNonce(blockTag);
```
