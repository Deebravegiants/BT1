# [?] fix(cli): fix submit command crashing with warp id error (#8044)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2026-02-05
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/04b877e031dac340ce3163d7030a1707d1510fe4
Type: security-commit

## Details
fix(cli): fix submit command crashing with warp id error (#8044)

## Patch
### .changeset/fix-submit-chain-resolution.md
```diff
@@ -0,0 +1,5 @@
+---
+"@hyperlane-xyz/cli": patch
+---
+
+Fixed submit command failing with "warp id not provided" error by creating dedicated chain resolver that reads transaction file to determine required chains.
```

### .github/workflows/test.yml
```diff
@@ -271,6 +271,7 @@ jobs:
           # Other commands
           - relay
           - status
+          - submit
           # ICA
           - ica-deploy
           # Warp Apply Commands
```

### typescript/cli/src/context/strategies/chain/chainResolver.ts
```diff
@@ -12,6 +12,7 @@ import { ProtocolType, assert } from '@hyperlane-xyz/utils';
 
 import { CommandType } from '../../../commands/signCommands.js';
 import { readCoreDeployConfigs } from '../../../config/core.js';
+import { getTransactions } from '../../../config/submit.js';
 import { getWarpRouteDeployConfig } from '../../../config/warp.js';
 import {
   filterOutDisabledChains,
@@ -51,7 +52,7 @@ export async function resolveChains(
       return resolveWarpRebalancerChains(argv);
 
     case CommandType.SUBMIT:
-      return resolveWarpRouteConfigChains(argv); // Same as WARP_DEPLOY
+      return resolveSubmitChains(argv);
     case CommandType.CORE_APPLY:
       return resolveCoreApplyChains(argv);
     case CommandType.CORE_DEPLOY:
@@ -302,3 +303,31 @@ async function resolveIcaDeployChains(
   assert(chains.size > 0, 'No chains provided for ICA deploy');
   return Array.from(chains);
 }
+
+async function resolveSubmitChains(
+  argv: Record<string, any>,
+): Promise<ChainName[]> {
+  try {
+    const { multiProvider } = argv.context;
+
+    const transactionFilePath: string | undefined = argv.transactions;
+    assert(
+      transactionFilePath,
+      'Expected transactions file path to be provided for submit command',
+    );
+
+    const transactions = getTransactions(transactionFilePath);
+
+    const chainIds = new Set(transactions.map((tx) => tx.chainId));
+    const chains = Array.from(chainIds).map((chainId) =>
+      multiProvider.getChainName(chainId),
+    );
+
+    assert(chains.length > 0, 'No transactions found in file');
+    return chains;
+  } catch (error) {
+    throw new Error(`Failed to resolve submit command chains`, {
+      cause: error,
+    });
+  }
+}
```

### typescript/cli/src/tests/ethereum/submit/submit.e2e-test.ts
```diff
@@ -119,11 +119,13 @@ describe('hyperlane submit', function () {
     const users = [ALICE, BOB];
     const xerc20Chains = [xerc20Chain2, xerc20Chain3];
 
-    await expectUserBalances(users, xerc20Chains, [0, 0]);
+    const initialBalances = await Promise.all(
+      users.map((user, i) => xerc20Chains[i].balanceOf(user)),
+    );
     await hyperlaneSubmit({ strategyPath, transactionsPath });
     await expectUserBalances(users, xerc20Chains, [
-      chain2MintAmount,
-      chain3MintAmount,
+      initialBalances[0].add(chain2MintAmount).toNumber(),
+      initialBalances[1].add(chain3MintAmount).toNumber(),
     ]);
   });
 
@@ -150,11 +152,13 @@ describe('hyperlane submit', function () {
     const users = [ALICE, BOB];
     const xerc20Chains = [xerc20Chain2, xerc20Chain3];
 
-    await expectUserBalances(users, xerc20Chains, [0, 0]);
+    const initialBalances = await Promise.all(
+      users.map((user, i) => xerc20Chains[i].balanceOf(user)),
+    );
     await hyperlaneSubmit({ transactionsPath });
     await expectUserBalances(users, xerc20Chains, [
-      chain2MintAmount,
-      chain3MintAmount,
+      initialBalances[0].add(chain2MintAmount).toNumber(),
+      initialBalances[1].add(chain3MintAmount).toNumber(),
     ]);
   });
 
```
