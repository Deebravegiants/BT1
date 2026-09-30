# [?] program: avoid underflow on market number of users (#1002)

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2024-04-08
Source: https://github.com/velocity-exchange/protocol-v2/commit/fc149939cfde7ed04c07d421a1f984b73a6846ea
Type: security-commit

## Details
program: avoid underflow on market number of users (#1002)

* program: market-number-of-users-accounting

* add admin update on market number_of_users

* CHANGELOG

---------

Co-authored-by: Chris Heaney <chrisheaney30@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -11,6 +11,8 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ### Fixes
 
+- program: avoid underflow in update pnl ([#1002](https://github.com/drift-labs/protocol-v2/pull/1002))
+
 ### Breaking
 
 ## [2.75.0] - 2024-04-01
```

### programs/drift/src/controller/position.rs
```diff
@@ -554,16 +554,22 @@ pub fn update_quote_asset_amount(
         return Ok(());
     }
 
-    if position.quote_asset_amount == 0 && position.base_asset_amount == 0 {
+    if position.quote_asset_amount == 0
+        && position.base_asset_amount == 0
+        && position.remainder_base_asset_amount == 0
+    {
         market.number_of_users = market.number_of_users.safe_add(1)?;
     }
 
     position.quote_asset_amount = position.quote_asset_amount.safe_add(delta)?;
 
     market.amm.quote_asset_amount = market.amm.quote_asset_amount.safe_add(delta.cast()?)?;
 
-    if position.quote_asset_amount == 0 && position.base_asset_amount == 0 {
-        market.number_of_users = market.number_of_users.safe_sub(1)?;
+    if position.quote_asset_amount == 0
+        && position.base_asset_amount == 0
+        && position.remainder_base_asset_amount == 0
+    {
+        market.number_of_users = market.number_of_users.saturating_sub(1);
     }
 
     Ok(())
```

### programs/drift/src/instructions/admin.rs
```diff
@@ -2310,6 +2310,30 @@ pub fn handle_update_perp_market_fee_adjustment(
     Ok(())
 }
 
+pub fn handle_update_perp_market_number_of_users<'info>(
+    ctx: Context<AdminUpdatePerpMarket>,
+    number_of_users: Option<u32>,
+    number_of_users_with_base: Option<u32>,
+) -> Result<()> {
+    let perp_market = &mut load_mut!(ctx.accounts.perp_market)?;
+
+    if let Some(number_of_users) = number_of_users {
+        perp_market.number_of_users = number_of_users;
+    }
+
+    if let Some(number_of_users_with_base) = number_of_users_with_base {
+        perp_market.number_of_users_with_base = number_of_users_with_base;
+    }
+
+    validate!(
+        perp_market.number_of_users >= perp_market.number_of_users_with_base,
+        ErrorCode::DefaultError,
+        "number_of_users must be >= number_of_users_with_base "
+    )?;
+
+    Ok(())
+}
+
 #[access_control(
     spot_market_valid(&ctx.accounts.spot_market)
 )]
```

### programs/drift/src/lib.rs
```diff
@@ -1128,6 +1128,14 @@ pub mod drift {
         handle_update_perp_market_max_open_interest(ctx, max_open_interest)
     }
 
+    pub fn update_perp_market_number_of_users(
+        ctx: Context<AdminUpdatePerpMarket>,
+        number_of_users: Option<u32>,
+        number_of_users_with_base: Option<u32>,
+    ) -> Result<()> {
+        handle_update_perp_market_number_of_users(ctx, number_of_users, number_of_users_with_base)
+    }
+
     pub fn update_perp_market_fee_adjustment(
         ctx: Context<AdminUpdatePerpMarket>,
         fee_adjustment: i16,
```

### sdk/src/adminClient.ts
```diff
@@ -2905,6 +2905,48 @@ export class AdminClient extends DriftClient {
 		);
 	}
 
+	public async updatePerpMarketNumberOfUser(
+		perpMarketIndex: number,
+		numberOfUsers?: number,
+		numberOfUsersWithBase?: number
+	): Promise<TransactionSignature> {
+		const updatepPerpMarketFeeAdjustmentIx =
+			await this.getUpdatePerpMarketNumberOfUsersIx(
+				perpMarketIndex,
+				numberOfUsers,
+				numberOfUsersWithBase
+			);
+
+		const tx = await this.buildTransaction(updatepPerpMarketFeeAdjustmentIx);
+
+		const { txSig } = await this.sendTransaction(tx, [], this.opts);
+
+		return txSig;
+	}
+
+	public async getUpdatePerpMarketNumberOfUsersIx(
+		perpMarketIndex: number,
+		numberOfUsers?: number,
+		numberOfUsersWithBase?: number
+	): Promise<TransactionInstruction> {
+		return await this.program.instruction.updatePerpMarketNumberOfUsers(
+			numberOfUsers,
+			numberOfUsersWithBase,
+			{
+				accounts: {
+					admin: this.isSubscribed
+						? this.getStateAccount().admin
+						: this.wallet.publicKey,
+					state: await this.getStatePublicKey(),
+					perpMarket: await getPerpMarketPublicKey(
+						this.program.programId,
+						perpMarketIndex
+					),
+				},
+			}
+		);
+	}
+
 	public async updatePerpMarketFeeAdjustment(
 		perpMarketIndex: number,
 		feeAdjustment: number
```

### sdk/src/idl/drift.json
```diff
@@ -4758,6 +4758,40 @@
         }
       ]
     },
+    {
+      "name": "updatePerpMarketNumberOfUsers",
+      "accounts": [
+        {
+          "name": "admin",
+          "isMut": false,
+          "isSigner": true
+        },
+        {
+          "name": "state",
+          "isMut": false,
+          "isSigner": false
+        },
+        {
+          "name": "perpMarket",
+          "isMut": true,
+          "isSigner": false
+        }
+      ],
+      "args": [
+        {
+          "name": "numberOfUsers",
+          "type": {
+            "option": "u32"
+          }
+        },
+        {
+          "name": "numberOfUsersWithBase",
+          "type": {
+            "option": "u32"
+          }
+        }
+      ]
+    },
     {
       "name": "updatePerpMarketFeeAdjustment",
       "accounts": [
```

### sdk/src/tx/forwardOnlyTxSender.ts
```diff
@@ -1,5 +1,9 @@
 import { AnchorProvider } from '@coral-xyz/anchor';
-import { ConfirmOptions, Connection, VersionedTransaction } from '@solana/web3.js';
+import {
+	ConfirmOptions,
+	Connection,
+	VersionedTransaction,
+} from '@solana/web3.js';
 import bs58 from 'bs58';
 import { IWallet } from '../types';
 import { BaseTxSender } from './baseTxSender';
@@ -75,7 +79,6 @@ export class ForwardOnlyTxSender extends BaseTxSender {
 		rawTransaction: Buffer | Uint8Array,
 		opts: ConfirmOptions
 	): Promise<TxSigAndSlot> {
-
 		const deserializedTx = VersionedTransaction.deserialize(rawTransaction);
 
 		const txSig = deserializedTx.signatures[0];
@@ -107,7 +110,10 @@ export class ForwardOnlyTxSender extends BaseTxSender {
 
 		let slot: number;
 		try {
-			const result = await this.confirmTransaction(encodedTxSig, opts.commitment);
+			const result = await this.confirmTransaction(
+				encodedTxSig,
+				opts.commitment
+			);
 			slot = result.context.slot;
 			// eslint-disable-next-line no-useless-catch
 		} catch (e) {
```

### sdk/src/tx/whileValidTxSender.ts
```diff
@@ -91,7 +91,9 @@ export class WhileValidTxSender extends BaseTxSender {
 		}
 
 		// handle subclass-specific side effects
-		const txSig = bs58.encode(signedTx.signatures[0]?.signature || signedTx.signatures[0]);
+		const txSig = bs58.encode(
+			signedTx.signatures[0]?.signature || signedTx.signatures[0]
+		);
 		this.untilValid.set(txSig, latestBlockhash);
 
 		return signedTx;
```
