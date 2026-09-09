Based on my research, I found a concrete equality-breaking issue in the POA bridge's withdrawal status reporting logic, though I was unable to fully view the body of `findMatchingWithdrawal` due to a tool error on the final iteration — my conclusion rests on the explicit code comment and test evidence at `poa-bridge.ts:313-343` plus `poa-bridge.test.ts:1054-1077`, not a full read of the helper's implementation.

### Title
Withdrawal status/txHash misreported when a batch contains multiple withdrawals with the same `assetId` - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` matches a withdrawal record returned by the POA bridge API to a specific `WithdrawalIdentifier` **by `assetId` only**, not by index or destination address, because the bridge API response list is unsorted with respect to the batch's intent order.

### Finding Description
`describeWithdrawal` retrieves the full list of withdrawals for a NEAR transaction and finds the matching one: [1](#0-0) 
The code comment makes the matching rule explicit: `// Response list is unsorted, so we match by assetId instead of index`. This is confirmed by a dedicated test titled "matches withdrawal by assetId, not by index": [2](#0-1) 

The `WithdrawalIdentifier` used for lookup is constructed per-leg of a batch withdrawal in `createWithdrawalIdentifiers`, one call per withdrawal leg, each carrying its own `index` and `withdrawalParams` (including `destinationAddress`): [3](#0-2) 

If a single NEAR intent transaction contains two (or more) withdrawal legs that share the same `assetId` but go to **different destination addresses** (e.g., paying out the same token to two different recipients in one batched intent), `describeWithdrawal` for leg 0 and leg 1 both filter the API's unsorted `withdrawals` array by the same `assetId` and — since matching is not also constrained by `destinationAddress`/`amount` — can resolve to the wrong underlying record. This breaks the equality "status/txHash reported == the on-chain outcome for *that specific* withdrawal leg."

### Impact Explanation
`watchWithdrawal` in `withdrawal-watcher.ts` trusts `describeWithdrawal`'s returned status/txHash as authoritative to resolve or reject the caller's promise for that specific leg: [4](#0-3) 
If leg 1 (still pending on-chain) is matched against leg 0's completed record because both share the same `assetId`, an integrator using `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` would be told leg 1 completed with leg 0's `txHash`, before leg 1 has actually settled on the destination chain. This is a status/hash misreport of the kind explicitly called out as High impact in the rules ("a status or hash misreport making an integrator credit or refund twice"), since the integrator could credit/release funds for a withdrawal that has not actually completed on-chain, based on a hash belonging to a different destination.

### Likelihood Explanation
This requires a batch withdrawal (multiple `withdrawalParams` in one `intentTx`) where two or more legs share the same `assetId` (same token/chain) but differ in destination — a realistic pattern for services paying out the same token to multiple recipients in one intent. No malicious actor is required; it's a data-shape trigger, not an attacker-controlled input, so likelihood depends on how often integrators batch same-asset/different-recipient withdrawals.

### Recommendation
Match withdrawal records by a stronger composite key that disambiguates same-`assetId` legs — e.g., `assetId` + `destinationAddress` + `amount` (and, if the API exposes one, a leg-local ordinal/nonce) — rather than `assetId` alone, in `findMatchingWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`).

### Proof of Concept
1. Build one NEAR intent with two `ft_withdraw` legs for the same POA-bridge token (same `assetId`), one to `destinationAddress A`, another to `destinationAddress B`.
2. Call `createWithdrawalIdentifiers` — both legs get the same `assetId`, differing only by `destinationAddress`/`index`.
3. POA bridge processes/settles the withdrawal to `A` first; `B` is still pending.
4. Call `describeWithdrawal` for leg `B`'s identifier — since the API's `withdrawals` array is unsorted and matching is by `assetId` only, it can return the `COMPLETED` record (with `A`'s `transfer_tx_hash`) for `B`'s query.
5. `watchWithdrawal`/`waitForWithdrawalCompletion` resolves for leg `B` with a completed status and a txHash that actually corresponds to leg `A`, even though `B` has not settled on-chain.

**Confidence caveat:** I could not read the full body of the `findMatchingWithdrawal` helper on the final tool iteration (tool call failed with a missing-parameter error), so I cannot 100% confirm whether it applies any additional disambiguation (e.g., by amount) beyond `assetId`. The code comment and test name at `poa-bridge.ts:318-337` strongly indicate matching is by `assetId` alone, but a follow-up read of that exact function is recommended to fully confirm before treating this as conclusively proven.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const response = await this.getWithdrawalStatusWithRetry(args);

		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L332-337)
```typescript
		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
		}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-53)
```typescript
		return await poll(
			async () => {
				try {
					const status = await args.bridge.describeWithdrawal({
						...args.wid,
						logger: args.logger,
					});

					consecutiveErrors = 0;

					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

					return POLL_PENDING;
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
}): Promise<{ bridge: Bridge; wid: WithdrawalIdentifier }[]> {
	const indexes = new Map<string, number>();
	const results: { bridge: Bridge; wid: WithdrawalIdentifier }[] = [];

	for (const w of args.withdrawalParams) {
		const bridge = await findBridgeForWithdrawal(args.bridges, w);
		if (bridge == null) {
			throw new BridgeNotFoundError();
		}

		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});

		results.push({ bridge, wid });
	}

	return results;
}
```
