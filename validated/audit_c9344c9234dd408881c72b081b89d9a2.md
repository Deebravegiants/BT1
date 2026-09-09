## Finding [1](#0-0) 

### Title
`OmniBridge.describeWithdrawal` matches transfers by array index instead of validating recipient/amount, can report the wrong destination tx hash for a batch withdrawal - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
`OmniBridge.describeWithdrawal` fetches all transfers created by a NEAR transaction via `omniBridgeAPI.getTransfer({ transactionHash })` and selects the one to report on purely by numeric array position (`args.index`), with no verification that the selected transfer's `recipient` or amount actually corresponds to the `withdrawalParams` the caller is polling for. [2](#0-1) 

### Finding Description
`describeWithdrawal` does:
```
const transfer = (await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash }))[args.index];
```
and then reports `{ status: "completed", txHash }` from whatever transfer object happened to be at that array position, using only that object's own `recipient`/`finalised.transaction_hash` fields. It never checks the resolved `transfer.recipient` against `args.withdrawalParams.destinationAddress`, nor the amount against `args.withdrawalParams.amount`, before reporting completion.

This is the same class of bug the codebase's own changelog documents as already fixed for the PoA bridge: `8bbd5c6: Fix POA bridge withdrawal matching to use assetId instead of index` [3](#0-2) . The PoA bridge now matches by `assetId` via `findMatchingWithdrawal` [4](#0-3) , but `OmniBridge` was left using the fragile index-based lookup that was proven unreliable for exactly this reason (indexer-returned order is not guaranteed to match submission order for multi-leg/batch withdrawals from a single NEAR transaction).

This directly parallels the ClearingHouse issue in the external report: a component (`ClearingHouse`'s fallback / here `describeWithdrawal`) cannot distinguish "this externally observed event genuinely corresponds to the operation I'm tracking" from "this is a different, unrelated event that happens to occupy the same slot" — it trusts positional/identity correspondence instead of validating the content (recipient, amount) of the event against the expected withdrawal.

`createWithdrawalCompletionPromises` in `sdk.ts` relies on `describeWithdrawal` per-index to resolve each promise, and callers use these promises/hashes to credit/save the completion status per leg of a batch withdrawal (see README batch-completion usage `promises[0].then(tx => saveUsdc(tx))`, `promises[1].then(tx => saveBtc(tx))`) [5](#0-4)  and [6](#0-5) . If the OmniBridge API returns the transfer list in an order that doesn't match `withdrawalParams` submission order (e.g. Solana leg indexed after BTC leg due to processing/indexing timing), an integrator polling `promises[i]` for a specific destination/amount could be handed the tx hash belonging to a different leg of the batch.

### Impact Explanation
A misreported completion status/tx hash for the wrong withdrawal leg can cause an integrator to mark the wrong withdrawal as completed and use the wrong destination tx hash to reconcile/credit user balances — matching the High-impact category "a status or hash misreport making an integrator credit or refund twice" from the rules.

### Likelihood Explanation
Requires only a normal batch withdrawal (multiple withdrawal legs settled in a single NEAR intent transaction) where the Omni Bridge indexer's transfer list ordering does not exactly match the order `withdrawalParams` were submitted in. No malicious actor action is required — the bug is a data-integrity gap (positional lookup instead of content validation), the same class of gap that was already found and patched for the sibling PoA bridge implementation.

### Recommendation
In `OmniBridge.describeWithdrawal`, do not select the transfer by raw array index. Instead, match the transfer by validating that its `recipient` corresponds to `args.withdrawalParams.destinationAddress` (and ideally amount), similar to the fix already applied to `PoaBridge.describeWithdrawal`/`findMatchingWithdrawal`. If multiple transfers can share the same recipient/amount, additional correlation data from the indexer (e.g. an explicit intent leg index or nonce) should be used instead of positional array index.

### Proof of Concept
1. Submit a batch withdrawal intent with two legs in the same NEAR tx: leg[0] = withdraw USDC to Solana address `A`, leg[1] = withdraw BTC to address `B`.
2. `omniBridgeAPI.getTransfer({ transactionHash })` returns the two transfer records but in an order that doesn't match submission order (e.g. BTC transfer appears at index 0 because it was indexed/finalized first, USDC at index 1).
3. `sdk.createWithdrawalCompletionPromises` polls `describeWithdrawal` for `wid.index = 0` expecting the USDC/Solana leg, but `transfer[0]` is actually the BTC transfer; since there is no recipient/amount check, `describeWithdrawal` returns `{status: "completed", txHash: <BTC tx hash>}` for the promise the caller believes corresponds to the USDC leg.
4. The caller's `promises[0].then(tx => saveUsdc(tx))` persists the BTC transaction hash as the USDC leg's completion, and vice versa for `promises[1]`, corrupting the completion record for both legs (referenced pattern in [5](#0-4) ).

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

**File:** packages/intents-sdk/CHANGELOG.md (L595-598)
```markdown

- 8bbd5c6: Fix POA bridge withdrawal matching to use assetId instead of index.
- c7738e3: Add `min_gas` to withdrawals, so bridges do not fail with out of gas.
- Updated dependencies [8bbd5c6]
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
function findMatchingWithdrawal(
	withdrawals: types.WithdrawalStatusResponseOk["result"]["withdrawals"],
	criteria: WithdrawalCriteria,
):
	| types.WithdrawalStatusResponseOk["result"]["withdrawals"][number]
	| undefined {
	return withdrawals.find(
		(w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
	);
}
```

**File:** packages/intents-sdk/README.md (L596-612)
```markdown
// Fire and forget - handle each independently
promises[0].then(tx => saveUsdc(tx)).catch(err => logError(0, err));
promises[1].then(tx => saveBtc(tx)).catch(err => logError(1, err));

// Or await a specific withdrawal (fast chain first)
const usdcTx = await promises[0];
await notifyUser('USDC received', usdcTx.hash);

// Or process as they complete with backpressure
const pending = new Map(promises.map((p, i) => [i, p]));
while (pending.size > 0) {
    const { index, tx } = await Promise.race(
        [...pending.entries()].map(async ([i, p]) => ({ index: i, tx: await p }))
    );
    pending.delete(index);
    await saveSuccess(index, tx);  // Backpressure maintained
}
```

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
```
