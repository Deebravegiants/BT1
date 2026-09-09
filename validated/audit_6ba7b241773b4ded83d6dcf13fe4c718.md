### Title
`OmniBridge.describeWithdrawal` reports a non-final UTXO pending sign ID as the completed withdrawal transaction hash - (`packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
The SDK’s `OmniBridge.describeWithdrawal` returns `status: "completed"` with `txHash` set to `transfer.utxo_meta.pending_sign_id` in browser environments, even though the same code comments state that value is not the finalised on-chain transaction hash and may change. This breaks the equality `reportedTxHash == onChainFinalisedTxHash`, which is the allowed analog class “a status reported that is not the on-chain outcome.”

### Finding Description
`OmniBridge.describeWithdrawal` fetches a transfer from the Omni Bridge API and selects a `txHash` to return. For UTXO destination chains it branches on `typeof window`, using `transfer.utxo_meta?.pending_sign_id` in browsers and `transfer.finalised?.transaction_hash` otherwise. The inline comment explicitly warns that `pending_sign_id` is not the finalised hash and can change if the BTC transfer fails to be submitted, yet the function still returns `{ status: "completed", txHash }` with that pending value. [1](#0-0) 

### Impact Explanation
This is a High-severity status/hash misreport. `watchWithdrawal` stops polling and returns the `txHash` as soon as `describeWithdrawal` reports `completed`, and integrators typically credit a user or mark a refund complete based on that hash. [2](#0-1)  If the finalised transaction hash later differs from `pending_sign_id` — which the code acknowledges

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L714-721)
```typescript
		} else if (isUtxoChain(destinationChain)) {
			// pending_sign_id is not the finalised tx hash. In rare cases, the hash may
			// change if the BTC transfer fails to be submitted. We return fast hash for FE and
			// wait for final one (transfer.finalised?.transaction_hash) for BE.
			txHash =
				typeof window !== "undefined"
					? transfer.utxo_meta?.pending_sign_id
					: transfer.finalised?.transaction_hash;
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-46)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
```
