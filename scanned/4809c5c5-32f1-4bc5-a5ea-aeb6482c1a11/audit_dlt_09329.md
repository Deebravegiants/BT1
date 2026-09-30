# [?] fix(network-manager): Validate initialDate as a parseable date string to avoid run-time crash

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2026-06-02
Source: https://github.com/NomicFoundation/hardhat/commit/5f6aff268841e947a2dd32a72a18885adf3d78de
Type: security-commit

## Details
fix(network-manager): Validate initialDate as a parseable date string to avoid run-time crash

## Patch
### .changeset/wide-ants-blow.md
```diff
@@ -0,0 +1,5 @@
+---
+"hardhat": patch
+---
+
+Validate `initialDate` is a parseable date string at config-load time, avoids BigInt(NaN) crash.
```

### packages/hardhat/src/internal/builtin-plugins/network-manager/type-validation.ts
```diff
@@ -322,7 +322,12 @@ const edrNetworkUserConfigSchema = z.object({
   hardfork: z.optional(z.string()),
   initialBaseFeePerGas: z.optional(gasUnitUserConfigSchema),
   initialDate: z.optional(
-    unionType([z.string(), z.instanceof(Date)], "Expected a string or a Date"),
+    unionType([z.string(), z.instanceof(Date)], "Expected a string or a Date")
+      .refine(
+        (val) =>
+          typeof val !== "string" || !Number.isNaN(Date.parse(val)),
+        { message: "initialDate must be a parseable date string" },
+      ),
   ),
   loggingEnabled: z.optional(z.boolean()),
   minGasPrice: z.optional(gasUnitUserConfigSchema),
```
