## Finding [1](#0-0) 

### Title
Omni Bridge reports BTC/UTXO withdrawals as "completed" using a mutable `pending_sign_id`, not the final on-chain transaction hash - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
`OmniBridge.describeWithdrawal` returns `status: "completed"` for withdrawals to UTXO chains (e.g. Bitcoin) using `transfer.utxo_meta?.pending_sign_id` whenever the code runs in a browser context (`typeof window !== "undefined"`), instead of the actually finalized transaction hash (`transfer.finalised?.transaction_hash`). The function's own comment acknowledges the `pending_sign_id` "is not the finalised tx hash" and "may change if the BTC transfer fails to be submitted," yet the caller still receives an unconditional `"completed"` status.

### Finding Description
`describeWithdrawal` branches on the destination chain type: [2](#0-1) 

For UTXO chains it selects `pending_sign_id` in a browser environment and only falls back to the real `finalised.transaction_hash` server-side. Regardless of which branch is taken, as long as `txHash` is truthy the function returns `{ status: "completed", txHash }` — there is no distinct "pending" state for the browser case even though the underlying transaction has not been finalized on the BTC network.

This status is consumed directly by `watchWithdrawal`, which treats any `"completed"` status as the terminal, successful state of the polling loop and resolves the promise with that hash as final: [3](#0-2) 

That resolved value is what `sdk.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` hand back to the integrator, documented as the point at which "the withdrawal completes ... on the destination chain": [4](#0-3) 

So an integrator running SDK code in a browser will see `status: "completed"` and a `txHash` (`pending_sign_id`) that the bridge itself documents as unstable and possibly wrong if the underlying BTC broadcast fails — i.e. the reported status/hash is not guaranteed to match the on-chain outcome.

### Impact Explanation
This breaks the equality "status reported == on-chain outcome": callers treat `"completed"` as terminal and record/act on `txHash`, but that hash can later change or the transfer can fail to be broadcast to Bitcoin. An integrator that credits a user or marks a withdrawal as settled based on this "completed" signal (as the SDK's public docs instruct) can end up crediting against a hash that is superseded or invalid, requiring a second credit/refund reconciliation once the true finalized hash appears — matching the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
Any consumer of `sdk.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` for a BTC/UTXO withdrawal, running in a browser context (`window` defined — the common case for frontend wallet integrations), will hit this path automatically; no attacker action is required, only the ordinary bridge race between BTC broadcast and sign-request issuance. The condition is deterministic based on `typeof window`, not a rare edge case.

### Recommendation
Do not report `"completed"` for UTXO withdrawals based on `pending_sign_id`. Either introduce a distinct intermediate status (e.g. `"pending-broadcast"`) that callers must not treat as terminal, or only return `"completed"` once `transfer.finalised?.transaction_hash` is available, regardless of environment, and expose the fast/pending hash through a separate, clearly-labeled field.

### Proof of Concept
1. Initiate a BTC withdrawal via the SDK in a browser environment.
2. `omni-bridge.ts`'s `describeWithdrawal` returns `{ status: "completed", txHash: pendingSignId }` while `transfer.finalised` is still `null`.
3. `watchWithdrawal` resolves the completion promise with this hash, and the integrator's UI/backend marks the withdrawal as done and credits accordingly.
4. The BTC broadcast subsequently fails or is replaced, so the final `transfer.finalised.transaction_hash` differs from `pendingSignId` — the integrator's recorded "completed" transaction never settles on Bitcoin, requiring manual reconciliation or resulting in a double credit if a retry path also succeeds.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-731)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];

		if (transfer == null || transfer.recipient == null) {
			return { status: "pending" };
		}

		const destinationChain = getChain(transfer.recipient as OmniAddress);
		let txHash = null;
		if (
			isEvmChain(destinationChain) ||
			destinationChain === ChainKind.Sol ||
			destinationChain === ChainKind.Fogo ||
			destinationChain === ChainKind.Strk ||
			destinationChain === ChainKind.Aptos
		) {
			txHash = transfer.finalised?.transaction_hash;
		} else if (isUtxoChain(destinationChain)) {
			// pending_sign_id is not the finalised tx hash. In rare cases, the hash may
			// change if the BTC transfer fails to be submitted. We return fast hash for FE and
			// wait for final one (transfer.finalised?.transaction_hash) for BE.
			txHash =
				typeof window !== "undefined"
					? transfer.utxo_meta?.pending_sign_id
					: transfer.finalised?.transaction_hash;
		} else {
			return { status: "completed", txHash: null };
		}

		if (!txHash) {
			return { status: "pending" };
		}

		return { status: "completed", txHash };
	}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```

**File:** packages/intents-sdk/src/sdk.ts (L455-464)
```typescript
	/**
	 * Wait for withdrawal(s) to complete on the destination chain.
	 *
	 * **Important:** Waits until the withdrawal completes, fails, or the chain-specific
	 * p99 timeout is exceeded. Use `AbortSignal.timeout()` to set a shorter timeout budget.
	 *
	 * @throws {WithdrawalWatchError} When status polling fails (timeout or consecutive errors).
	 *   Inspect `error.cause` to determine the reason.
	 * @throws {WithdrawalFailedError} When the withdrawal fails on the destination chain.
	 * @throws {DOMException} When the provided AbortSignal is aborted (name: "AbortError").
```
