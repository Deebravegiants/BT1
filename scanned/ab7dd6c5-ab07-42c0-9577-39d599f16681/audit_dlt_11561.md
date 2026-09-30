# [?] Fixed rare edge case race condition when trying to report a transaction error (#1237)

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2024-10-02
Source: https://github.com/velocity-exchange/protocol-v2/commit/dc1da0e9ac436d4d02785c05030b00d2131d1b44
Type: security-commit

## Details
Fixed rare edge case race condition when trying to report a transaction error (#1237)

## Patch
### sdk/src/tx/whileValidTxSender.ts
```diff
@@ -2,6 +2,7 @@ import { TxSigAndSlot } from './types';
 import {
 	ConfirmOptions,
 	Connection,
+	SendTransactionError,
 	Signer,
 	Transaction,
 	VersionedTransaction,
@@ -242,6 +243,15 @@ export class WhileValidTxSender extends BaseTxSender {
 
 			await this.checkConfirmationResultForError(txid, result.value);
 
+			if (result?.value?.err) {
+				// Fallback error handling if there's a problem reporting the error in checkConfirmationResultForError
+				throw new SendTransactionError({
+					action: 'send',
+					signature: txid,
+					transactionMessage: `Transaction Failed`,
+				});
+			}
+
 			slot = result.context.slot;
 			// eslint-disable-next-line no-useless-catch
 		} catch (e) {
```
