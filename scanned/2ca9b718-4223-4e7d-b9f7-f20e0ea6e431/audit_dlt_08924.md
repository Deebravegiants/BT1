# [?] sdk/js: fix number overflow

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-09-15
Source: https://github.com/wormhole-foundation/wormhole/commit/06984351b8e64fe4aec3043bf97612dd8cc6ada1
Type: security-commit

## Details
sdk/js: fix number overflow

Change-Id: Iba73f620ee8e99737e38eee0246599ca28af7bba

## Patch
### sdk/js/src/migration/addLiquidity.ts
```diff
@@ -1,4 +1,4 @@
-import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token";
+import { Token, TOKEN_PROGRAM_ID, u64 } from "@solana/spl-token";
 import { Connection, PublicKey, Transaction } from "@solana/web3.js";
 import { ixFromRust } from "../solana";
 
@@ -21,7 +21,7 @@ export default async function addLiquidity(
     new PublicKey(authority_address(program_id)),
     new PublicKey(payerAddress),
     [],
-    Number(amount)
+    new u64(amount.toString(16), 16)
   );
   const ix = ixFromRust(
     add_liquidity(
```

### sdk/js/src/migration/claimShares.ts
```diff
@@ -1,4 +1,4 @@
-import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token";
+import { Token, TOKEN_PROGRAM_ID, u64 } from "@solana/spl-token";
 import { Connection, PublicKey, Transaction } from "@solana/web3.js";
 import { ixFromRust } from "../solana";
 
@@ -21,7 +21,7 @@ export default async function claimShares(
     new PublicKey(authority_address(program_id)),
     new PublicKey(payerAddress),
     [],
-    Number(amount)
+    new u64(amount.toString(16), 16)
   );
   const ix = ixFromRust(
     claim_shares(
```

### sdk/js/src/migration/migrateTokens.ts
```diff
@@ -1,4 +1,4 @@
-import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token";
+import { Token, TOKEN_PROGRAM_ID, u64 } from "@solana/spl-token";
 import { Connection, PublicKey, Transaction } from "@solana/web3.js";
 import { ixFromRust } from "../solana";
 
@@ -21,7 +21,7 @@ export default async function migrateTokens(
     new PublicKey(authority_address(program_id)),
     new PublicKey(payerAddress),
     [],
-    Number(amount)
+    new u64(amount.toString(16), 16)
   );
   const ix = ixFromRust(
     migrate_tokens(
```

### sdk/js/src/migration/removeLiquidity.ts
```diff
@@ -1,4 +1,4 @@
-import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token";
+import { Token, TOKEN_PROGRAM_ID, u64 } from "@solana/spl-token";
 import { Connection, PublicKey, Transaction } from "@solana/web3.js";
 import { ixFromRust } from "../solana";
 
@@ -21,7 +21,7 @@ export default async function removeLiquidity(
     new PublicKey(authority_address(program_id)),
     new PublicKey(payerAddress),
     [],
-    Number(amount)
+    new u64(amount.toString(16), 16)
   );
   const ix = ixFromRust(
     remove_liquidity(
```

### sdk/js/src/token_bridge/transfer.ts
```diff
@@ -1,4 +1,4 @@
-import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token";
+import { Token, TOKEN_PROGRAM_ID, u64 } from "@solana/spl-token";
 import { Connection, Keypair, PublicKey, Transaction } from "@solana/web3.js";
 import { MsgExecuteContract } from "@terra-money/terra.js";
 import { ethers } from "ethers";
@@ -128,7 +128,7 @@ export async function transferFromSolana(
     new PublicKey(approval_authority_address(tokenBridgeAddress)),
     new PublicKey(payerAddress),
     [],
-    Number(amount)
+    new u64(amount.toString(16), 16)
   );
   let messageKey = Keypair.generate();
   const isSolanaNative =
```
