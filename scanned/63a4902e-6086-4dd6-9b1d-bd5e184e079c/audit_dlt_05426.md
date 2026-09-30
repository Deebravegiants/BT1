# [?] Integrate Frontier's fix for `eth_getTransactionReceipt` race condition (#3651)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2026-02-03
Source: https://github.com/moonbeam-foundation/moonbeam/commit/0cbbef04b83b130f5372aed36564b2d4b6ee4797
Type: security-commit

## Details
Integrate Frontier's fix for `eth_getTransactionReceipt` race condition (#3651)

* chore: :pushpin: upgrade frontier

* feat: :sparkles: implement block_hash_by_number

* fix: :bug: fix return type

* test: :white_check_mark: add getBlockWithRetry test util

## Patch
### Cargo.lock
```diff
@@ -4164,7 +4164,7 @@ dependencies = [
 [[package]]
 name = "fc-api"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "async-trait",
  "fp-storage",
@@ -4176,7 +4176,7 @@ dependencies = [
 [[package]]
 name = "fc-consensus"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "async-trait",
  "fp-consensus",
@@ -4192,7 +4192,7 @@ dependencies = [
 [[package]]
 name = "fc-db"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "async-trait",
  "ethereum",
@@ -4222,7 +4222,7 @@ dependencies = [
 [[package]]
 name = "fc-mapping-sync"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "fc-db",
  "fc-storage",
@@ -4245,7 +4245,7 @@ dependencies = [
 [[package]]
 name = "fc-rpc"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum",
  "ethereum-types",
@@ -4299,7 +4299,7 @@ dependencies = [
 [[package]]
 name = "fc-rpc-core"
 version = "1.1.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum",
  "ethereum-types",
@@ -4315,7 +4315,7 @@ dependencies = [
 [[package]]
 name = "fc-rpc-v2-api"
 version = "0.1.0"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum-types",
  "fc-rpc-v2-types",
@@ -4325,7 +4325,7 @@ dependencies = [
 [[package]]
 name = "fc-rpc-v2-types"
 version = "0.1.0"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "const-hex",
  "ethereum-types",
@@ -4336,7 +4336,7 @@ dependencies = [
 [[package]]
 name = "fc-storage"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum",
  "ethereum-types",
@@ -4529,7 +4529,7 @@ dependencies = [
 [[package]]
 name = "fp-account"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "hex",
  "impl-serde",
@@ -4547,7 +4547,7 @@ dependencies = [
 [[package]]
 name = "fp-consensus"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum",
  "parity-scale-codec",
@@ -4558,7 +4558,7 @@ dependencies = [
 [[package]]
 name = "fp-ethereum"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum",
  "ethereum-types",
@@ -4570,7 +4570,7 @@ dependencies = [
 [[package]]
 name = "fp-evm"
 version = "3.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "environmental",
  "evm",
@@ -4586,7 +4586,7 @@ dependencies = [
 [[package]]
 name = "fp-rpc"
 version = "3.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ethereum",
  "ethereum-types",
@@ -4602,7 +4602,7 @@ dependencies = [
 [[package]]
 name = "fp-self-contained"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "frame-support",
  "parity-scale-codec",
@@ -4614,7 +4614,7 @@ dependencies = [
 [[package]]
 name = "fp-storage"
 version = "2.0.0"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "parity-scale-codec",
  "serde",
@@ -9866,7 +9866,7 @@ dependencies = [
 [[package]]
 name = "pallet-ethereum"
 version = "4.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "environmental",
  "ethereum",
@@ -9921,7 +9921,7 @@ dependencies = [
 [[package]]
 name = "pallet-evm"
 version = "6.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "cumulus-primitives-storage-weight-reclaim",
  "environmental",
@@ -9946,7 +9946,7 @@ dependencies = [
 [[package]]
 name = "pallet-evm-chain-id"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "frame-support",
  "frame-system",
@@ -10024,15 +10024,15 @@ dependencies = [
 [[package]]
 name = "pallet-evm-precompile-blake2"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "fp-evm",
 ]
 
 [[package]]
 name = "pallet-evm-precompile-bls12381"
 version = "1.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "ark-bls12-381 0.4.0",
  "ark-ec 0.4.2",
@@ -10044,7 +10044,7 @@ dependencies = [
 [[package]]
 name = "pallet-evm-precompile-bn128"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "fp-evm",
  "sp-core",
@@ -10200,7 +10200,7 @@ dependencies = [
 [[package]]
 name = "pallet-evm-precompile-modexp"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "fp-evm",
  "num",
@@ -10402,7 +10402,7 @@ dependencies = [
 [[package]]
 name = "pallet-evm-precompile-sha3fips"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "fp-evm",
  "frame-support",
@@ -10413,7 +10413,7 @@ dependencies = [
 [[package]]
 name = "pallet-evm-precompile-simple"
 version = "2.0.0-dev"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "fp-evm",
  "ripemd",
@@ -13344,7 +13344,7 @@ dependencies = [
 [[package]]
 name = "precompile-utils"
 version = "0.1.0"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "derive_more 1.0.0",
  "environmental",
@@ -13373,7 +13373,7 @@ dependencies = [
 [[package]]
 name = "precompile-utils-macro"
 version = "0.1.0"
-source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#ba163563b1e1157fdf9f539faeedead520dda8e2"
+source = "git+https://github.com/moonbeam-foundation/frontier?branch=moonbeam-polkadot-stable2506#a9b04a63153837646b87c0af612d6539a7a7ed13"
 dependencies = [
  "case",
  "num_enum 0.7.3",
```

### node/service/src/lazy_loading/frontier_backend.rs
```diff
@@ -107,4 +107,16 @@ where
 	async fn latest_block_hash(&self) -> Result<Block::Hash, String> {
 		self.frontier_backend.latest_block_hash().await
 	}
+
+	async fn block_hash_by_number(&self, block_number: u64) -> Result<Option<H256>, String> {
+		let block = self
+			.rpc_client
+			.block_by_number(
+				fc_rpc_v2_api::types::BlockNumberOrTag::Number(block_number),
+				false,
+			)
+			.map_err(|e| format!("failed to get block by number: {:?}", e))?;
+
+		Ok(block.and_then(|b| b.header.hash))
+	}
 }
```

### node/service/src/lazy_loading/rpc_client.rs
```diff
@@ -222,6 +222,22 @@ impl RPC {
 		self.block_on(request)
 	}
 
+	pub fn block_by_number(
+		&self,
+		block_number: fc_rpc_v2_api::types::BlockNumberOrTag,
+		full: bool,
+	) -> Result<Option<fc_rpc_v2_api::types::Block>, jsonrpsee::core::ClientError> {
+		let request = &|| {
+			fc_rpc_v2_api::eth::EthBlockApiClient::block_by_number(
+				&self.http_client,
+				block_number.clone(),
+				full,
+			)
+		};
+
+		self.block_on(request)
+	}
+
 	fn block_on<F, T, E>(&self, f: &dyn Fn() -> F) -> Result<T, E>
 	where
 		F: Future<Output = Result<T, E>>,
```

### test/helpers/eth-transactions.ts
```diff
@@ -123,6 +123,49 @@ export async function getTransactionReceiptWithRetry(
   throw lastError || new Error(`Failed to get transaction receipt after ${maxAttempts} attempts`);
 }
 
+export async function getBlockWithRetry(
+  context: DevModeContext,
+  options?: {
+    blockHash?: `0x${string}`;
+    blockNumber?: bigint;
+    maxAttempts?: number;
+    delayMs?: number;
+  }
+) {
+  const maxAttempts = options?.maxAttempts ?? 4;
+  const delayMs = options?.delayMs ?? 100;
+
+  let lastError: Error | undefined;
+
+  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
+    try {
+      if (options?.blockHash) {
+        return await context.viem().getBlock({ blockHash: options.blockHash });
+      } else if (options?.blockNumber !== undefined) {
+        return await context.viem().getBlock({ blockNumber: options.blockNumber });
+      } else {
+        return await context.viem().getBlock();
+      }
+    } catch (error: any) {
+      lastError = error;
+
+      if (
+        error.name === "BlockNotFoundError" ||
+        error.message?.includes("Block could not be found")
+      ) {
+        if (attempt < maxAttempts) {
+          await new Promise((resolve) => setTimeout(resolve, delayMs));
+          continue;
+        }
+      }
+
+      throw error;
+    }
+  }
+
+  throw lastError || new Error(`Failed to get block after ${maxAttempts} attempts`);
+}
+
 export async function getTransactionFees(context: DevModeContext, hash: string): Promise<bigint> {
   const receipt = await getTransactionReceiptWithRetry(context, hash as `0x${string}`);
 
```

### test/suites/dev/moonbase/test-chain/test-fork-chain.ts
```diff
@@ -2,6 +2,7 @@ import "@moonbeam-network/api-augment";
 import { beforeEach, describeSuite, expect, TransactionTypes } from "@moonwall/cli";
 import { createRawTransfer } from "@moonwall/util";
 import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";
+import { getBlockWithRetry } from "../../../../helpers/eth-transactions";
 
 describeSuite({
   id: "D020401",
@@ -46,7 +47,7 @@ describeSuite({
           (await context.viem().getBlock({ blockNumber: 2n })).hash,
           "Ethereum blocks should have changed"
         ).to.not.equal(ethHash2);
-        expect((await context.viem().getBlock()).number).toBe(currentHeight + 1n);
+        expect((await getBlockWithRetry(context)).number).toBe(currentHeight + 1n);
       },
     });
 
```

### test/suites/dev/moonbase/test-txpool/test-txpool-limits.ts
```diff
@@ -1,6 +1,7 @@
 import "@moonbeam-network/api-augment";
 import { describeSuite, expect } from "@moonwall/cli";
 import { BALTATHAR_ADDRESS, createRawTransfer, sendRawTransaction } from "@moonwall/util";
+import { getBlockWithRetry } from "../../../../helpers/eth-transactions";
 
 describeSuite({
   id: "D023803",
@@ -19,7 +20,7 @@ describeSuite({
         }
 
         await context.createBlock();
-        const maxTxnLen = (await context.viem().getBlock()).transactions.length;
+        const maxTxnLen = (await getBlockWithRetry(context)).transactions.length;
         log(`out ${maxTxnLen}`);
         expect(maxTxnLen).toBeGreaterThan(2300);
       },
```

### test/suites/dev/moonbase/test-txpool/test-txpool-limits2.ts
```diff
@@ -2,6 +2,7 @@ import "@moonbeam-network/api-augment";
 import { describeSuite, expect, fetchCompiledContract } from "@moonwall/cli";
 import { createEthersTransaction } from "@moonwall/util";
 import { encodeDeployData } from "viem";
+import { getBlockWithRetry } from "../../../../helpers/eth-transactions";
 
 describeSuite({
   id: "D023804",
@@ -32,7 +33,7 @@ describeSuite({
         }
 
         await context.createBlock();
-        expect((await context.viem().getBlock()).transactions.length).toBe(284);
+        expect((await getBlockWithRetry(context)).transactions.length).toBe(284);
       },
     });
   },
```

### test/suites/dev/moonbase/test-txpool/test-txpool-limits3.ts
```diff
@@ -2,6 +2,7 @@ import "@moonbeam-network/api-augment";
 import { beforeAll, describeSuite, expect, fetchCompiledContract } from "@moonwall/cli";
 import { ALITH_ADDRESS, createEthersTransaction } from "@moonwall/util";
 import { encodeDeployData } from "viem";
+import { getBlockWithRetry } from "../../../../helpers/eth-transactions";
 
 describeSuite({
   id: "D023805",
@@ -82,7 +83,7 @@ describeSuite({
           ).length;
           log(`Transactions left in pool: ${txPoolSize}`);
 
-          if ((await context.viem().getBlock()).transactions.length === 0) {
+          if ((await getBlockWithRetry(context)).transactions.length === 0) {
             break;
           }
           blocks++;
```

### test/suites/dev/moonbase/test-txpool/test-txpool-limits4.ts
```diff
@@ -2,6 +2,7 @@ import "@moonbeam-network/api-augment";
 import { describeSuite, expect, fetchCompiledContract } from "@moonwall/cli";
 import { ALITH_ADDRESS, createEthersTransaction } from "@moonwall/util";
 import { encodeDeployData } from "viem";
+import { getBlockWithRetry } from "../../../../helpers/eth-transactions";
 
 describeSuite({
   id: "D023806",
@@ -54,7 +55,7 @@ describeSuite({
           ).length;
           log(`Transactions left in pool: ${txPoolSize}`);
 
-          if ((await context.viem().getBlock()).transactions.length === 0) {
+          if ((await getBlockWithRetry(context)).transactions.length === 0) {
             break;
           }
           blocks++;
```
