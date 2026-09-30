# [?] Use non-capturing regex for data to prevent memory exhaustion for long strings (#4741).

## Summary
Severity: Unknown
Chain: Tooling
Component: ethers-io/ethers.js
Published: 2024-05-29
Source: https://github.com/ethers-io/ethers.js/commit/5463aa03eacde45322a1e05693ce90e4d7abcaa7
Type: security-commit

## Details
Use non-capturing regex for data to prevent memory exhaustion for long strings (#4741).

## Patch
### src.ts/utils/data.ts
```diff
@@ -31,7 +31,7 @@ function _getBytes(value: BytesLike, name?: string, copy?: boolean): Uint8Array
         return value;
     }
 
-    if (typeof(value) === "string" && value.match(/^0x([0-9a-f][0-9a-f])*$/i)) {
+    if (typeof(value) === "string" && value.match(/^0x(?:[0-9a-f][0-9a-f])*$/i)) {
         const result = new Uint8Array((value.length - 2) / 2);
         let offset = 2;
         for (let i = 0; i < result.length; i++) {
```
