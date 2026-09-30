# [?] fix race condition

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2026-04-17
Source: https://github.com/NomicFoundation/hardhat/commit/96ac17816521263483b95bb680db4d3e05c1ead6
Type: security-commit

## Details
fix race condition

## Patch
### packages/hardhat-viem/test/gas-config.ts
```diff
@@ -7,7 +7,7 @@ import type { EthereumProvider } from "hardhat/types/providers";
 import assert from "node:assert/strict";
 import { after, before, describe, it } from "node:test";
 
-import { useFixtureProject } from "@nomicfoundation/hardhat-test-utils";
+import { useEphemeralFixtureProject } from "@nomicfoundation/hardhat-test-utils";
 import { createHardhatRuntimeEnvironment } from "hardhat/hre";
 import { encodeFunctionData } from "viem";
 
@@ -20,7 +20,7 @@ interface InitResult {
 }
 
 describe("gas config behavior", () => {
-  useFixtureProject("default-ts-project");
+  useEphemeralFixtureProject("default-ts-project");
 
   let hre: HardhatRuntimeEnvironment;
 
```
