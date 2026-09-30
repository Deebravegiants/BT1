# [?] Fix Chopsticks runtime-upgrade test panic (`InvalidNumberOfDescendants`) (#3800)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2026-06-22
Source: https://github.com/moonbeam-foundation/moonbeam/commit/8d4a50b6822459d795a67e9353c50dd051a155c6
Type: security-commit

## Details
Fix Chopsticks runtime-upgrade test panic (`InvalidNumberOfDescendants`) (#3800)

* Fix Chopsticks fork-block selection for Moonbeam/Moonriver

* Fix Chopsticks runtime-upgrade test panic ()

## Patch
### .github/workflows/build.yml
```diff
@@ -806,10 +806,6 @@ jobs:
       - name: "Install and run upgrade test"
         run: |
           pnpm install
-      - name: Select stable Chopsticks fork block
-        run: |
-          cd test
-          pnpm tsx scripts/select-chopsticks-fork-block.ts --chain ${{ matrix.chain }} --github-env "$GITHUB_ENV"
       - name: Run Upgrade Test (with retry)
         uses: nick-fields/retry@ad984534de44a9489a53aefd81eb77f87c70dc60
         with:
```

### test/configs/alphanet.yml
```diff
@@ -1,5 +1,4 @@
 endpoint: wss://trace.api.moonbase.moonbeam.network
-block: ${env.CHOPSTICKS_BLOCK}
 mock-signature-host: true
 db: ./tmp/db_mba.sqlite
 
```

### test/configs/moonbeam.yml
```diff
@@ -1,5 +1,4 @@
 endpoint: wss://trace.api.moonbeam.network
-block: ${env.CHOPSTICKS_BLOCK}
 mock-signature-host: true
 db: ./tmp/db_mb.sqlite
 
```

### test/configs/moonriver.yml
```diff
@@ -1,5 +1,4 @@
 endpoint: wss://wss.moonriver.moonbeam.network
-block: ${env.CHOPSTICKS_BLOCK}
 mock-signature-host: true
 db: ./tmp/db_mr.sqlite
 
```

### test/scripts/select-chopsticks-fork-block.ts
```diff
@@ -1,128 +0,0 @@
-import "@moonbeam-network/api-augment";
-
-import fs from "node:fs";
-import { ApiPromise, WsProvider } from "@polkadot/api";
-import yargs from "yargs";
-import { hideBin } from "yargs/helpers";
-
-const DEFAULT_ENDPOINTS = {
-  moonbase: "wss://trace.api.moonbase.moonbeam.network",
-  moonbeam: "wss://trace.api.moonbeam.network",
-  moonriver: "wss://wss.moonriver.moonbeam.network",
-} as const;
-
-type Chain = keyof typeof DEFAULT_ENDPOINTS;
-
-const argv = yargs(hideBin(process.argv))
-  .usage("Usage: $0 --chain <moonbase|moonbeam|moonriver>")
-  .options({
-    chain: {
-      choices: Object.keys(DEFAULT_ENDPOINTS) as Chain[],
-      demandOption: true,
-      description: "Moonbeam network to inspect",
-    },
-    endpoint: {
-      type: "string",
-      description: "Override websocket endpoint",
-    },
-    "max-depth": {
-      type: "number",
-      default: 250,
-      description: "Finalized blocks to scan backwards",
-    },
-    "min-descendants": {
-      type: "number",
-      default: 2,
-      description: "Minimum relay parent descendants required",
-    },
-    "github-env": {
-      type: "string",
-      description: "Append CHOPSTICKS_BLOCK to this GitHub Actions env file",
-    },
-  })
-  .parseSync();
-
-const getRelayParentDescendantsLength = (extrinsic: any): number | undefined => {
-  if (
-    extrinsic.method?.section !== "parachainSystem" ||
-    extrinsic.method?.method !== "setValidationData"
-  ) {
-    return undefined;
-  }
-
-  const inherentData = extrinsic.method.args[0] as any;
-  const descendants = inherentData?.relayParentDescendants;
-
-  return typeof descendants?.length === "number" ? descendants.length : undefined;
-};
-
-const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
-
-const retryRpc = async <T>(
-  operation: () => Promise<T>,
-  options: { maxAttempts?: number; backoffMs?: number } = {}
-): Promise<T> => {
-  const maxAttempts = options.maxAttempts ?? 4;
-  const backoffMs = options.backoffMs ?? 500;
-
-  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
-    try {
-      return await operation();
-    } catch (error) {
-      if (attempt === maxAttempts) {
-        throw error;
-      }
-
-      await wait(backoffMs * 2 ** (attempt - 1));
-    }
-  }
-
-  throw new Error("RPC retry attempts exhausted");
-};
-
-const main = async () => {
-  const endpoint = argv.endpoint ?? DEFAULT_ENDPOINTS[argv.chain];
-  const provider = new WsProvider(endpoint);
-  const api = await ApiPromise.create({ provider, noInitWarn: true });
-
-  try {
-    const finalizedHash = await retryRpc(() => api.rpc.chain.getFinalizedHead());
-    const finalizedHeader = await retryRpc(() => api.rpc.chain.getHeader(finalizedHash));
-    const finalizedNumber = finalizedHeader.number.toNumber();
-
-    const oldestNumber = Math.max(0, finalizedNumber - argv.maxDepth);
-
-    for (let number = finalizedNumber; number >= oldestNumber; number--) {
-      const hash = await retryRpc(() => api.rpc.chain.getBlockHash(number));
-      const block = await retryRpc(() => api.rpc.chain.getBlock(hash));
-      const descendantsLength = block.block.extrinsics
-        .map(getRelayParentDescendantsLength)
-        .find((length) => length !== undefined);
-
-      if (descendantsLength === undefined) {
-        continue;
-      }
-
-      if (descendantsLength >= argv.minDescendants) {
-        console.log(
-          `Selected ${argv.chain} block #${number} with ${descendantsLength} relay parent descendants`
-        );
-        console.log(`CHOPSTICKS_BLOCK=${number}`);
-
-        if (argv.githubEnv) {
-          fs.appendFileSync(argv.githubEnv, `CHOPSTICKS_BLOCK=${number}\n`);
-        }
-
-        return;
-      }
-    }
-
-    throw new Error(
-      `No finalized ${argv.chain} block with at least ${argv.minDescendants} relay parent descendants found in the last ${argv.maxDepth} blocks`
-    );
-  } finally {
-    await api.disconnect();
-  }
-};
-
-await main();
```

### test/suites/chopsticks/test-upgrade-chain.ts
```diff
@@ -25,61 +25,21 @@ const upgradeRestrictionSignal = (paraId: u32) => {
   return hash(prefix, paraId.toU8a());
 };
 
-const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
-
-const isRetriableChopsticksBlockError = (error: unknown): boolean => {
-  const message = error instanceof Error ? error.message : String(error);
-  return (
-    message.includes("Failed to apply inherents") ||
-    message.includes("InvalidNumberOfDescendants") ||
-    message.includes("Unable to verify provided relay parent descendants")
-  );
-};
-
-const createEmptyBlockWithRetry = async (
-  context: ChopsticksContext,
-  api: ApiPromise,
-  options?: { maxAttempts?: number; delayMs?: number }
-) => {
-  const maxAttempts = options?.maxAttempts ?? 5;
-  const delayMs = options?.delayMs ?? 500;
-
-  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
-    const currentHeight = (await api.rpc.chain.getHeader()).number.toNumber();
-
-    try {
-      await context.createBlock();
-    } catch (error) {
-      if (attempt < maxAttempts && isRetriableChopsticksBlockError(error)) {
-        await wait(delayMs * attempt);
-        continue;
-      }
-
-      throw error;
-    }
-
-    const newHeight = (await api.rpc.chain.getHeader()).number.toNumber();
-    if (newHeight > currentHeight) {
-      return;
-    }
-
-    if (attempt < maxAttempts) {
-      await wait(delayMs * attempt);
-      continue;
-    }
-
-    expect(newHeight - currentHeight).to.be.equal(1);
-  }
-};
-
-const createEmptyBlocksWithRetry = async (
-  context: ChopsticksContext,
-  api: ApiPromise,
-  count: number
-) => {
-  for (let i = 0; i < count; i++) {
-    await createEmptyBlockWithRetry(context, api);
-  }
+// Chopsticks builds blocks against a mocked relay chain and cannot supply the
+// relay-parent descendant headers that `parachain-system` verifies whenever
+// `RelayParentOffset > 0`. The upgraded runtime enables `pallet_async_backing`,
+// whose `RelayParentOffset` storage value defaults to 1, so the empty descendant
+// set produced by Chopsticks makes block production panic with
+// `InvalidNumberOfDescendants { expected: 2, received: 0 }`.
+//
+// Forcing the offset to 0 in the forked chain skips that check. The real network
+// is unaffected: its collators source the descendants from the live relay chain.
+const disableRelayParentOffset = async (context: ChopsticksContext) => {
+  await context.setStorage({
+    module: "asyncBacking",
+    method: "relayParentOffset",
+    methodParams: "0x00000000", // u32 little-endian 0
+  });
 };
 
 const upgradeRuntime = async (context: ChopsticksContext) => {
@@ -101,7 +61,7 @@ const upgradeRuntime = async (context: ChopsticksContext) => {
     method: "authorizedUpgrade",
     methodParams: `${rtHash}01`, // 01 is for the RT ver check = true
   });
-  await createEmptyBlockWithRetry(context, api);
+  await context.createBlock();
 
   await api.tx.system.applyAuthorizedUpgrade(rtHex).signAndSend(signer);
 
@@ -111,6 +71,10 @@ const upgradeRuntime = async (context: ChopsticksContext) => {
     count: 3,
     relayChainStateOverrides: [[upgradeRestrictionSignal(paraId), null]],
   });
+
+  // The upgraded runtime now enforces relay-parent descendants which Chopsticks
+  // cannot provide; disable the offset before any further blocks are built.
+  await disableRelayParentOffset(context);
 };
 
 describeSuite({
@@ -147,7 +111,7 @@ describeSuite({
       title: "Can create new blocks",
       test: async () => {
         const currentHeight = (await api.rpc.chain.getHeader()).number.toNumber();
-        await createEmptyBlocksWithRetry(context, api, 2);
+        await context.createBlock({ count: 2 });
         const newHeight = (await api.rpc.chain.getHeader()).number.toNumber();
         expect(newHeight - currentHeight).to.be.equal(2);
       },
@@ -166,7 +130,7 @@ describeSuite({
           // Some multi-migration might take a lot of blocks to complete, so we wait for 16 blocks to be safe.
           // Note that we must wait for one block at a time otherwise the request will timeout.
           for (let i = 0; i < 16; i++) {
-            await createEmptyBlockWithRetry(context, api);
+            await context.createBlock();
           }
 
           const balanceBefore = (
@@ -175,7 +139,7 @@ describeSuite({
           await api.tx.balances
             .transferAllowDeath(DUMMY_ACCOUNT, parseEther("1"))
             .signAndSend(alith);
-          await createEmptyBlocksWithRetry(context, api, 2);
+          await context.createBlock({ count: 2 });
           const balanceAfter = (await api.query.system.account(DUMMY_ACCOUNT)).data.free.toBigInt();
           expect(balanceBefore < balanceAfter).to.be.true;
         }
```
