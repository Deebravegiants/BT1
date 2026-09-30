# [?] Fix underflow in gas calculation (#794)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2022-07-18
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/cd7dded55336d8c5caa7ae0a4b708a3437822b8c
Type: security-commit

## Details
Fix underflow in gas calculation (#794)

## Patch
### typescript/helloworld/src/app/app.ts
```diff
@@ -31,7 +31,7 @@ export class HelloWorldApp<
       message,
       chainConnection.overrides,
     );
-    const gasLimit = estimated.mul(1.1).toNumber();
+    const gasLimit = estimated.mul(11).div(10);
 
     const tx = await sender.sendHelloWorld(toDomain, message, {
       ...chainConnection.overrides,
```
