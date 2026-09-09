### Title
POA Bridge withdrawal status matches by `assetId` alone, causing cross-withdrawal status/hash misreport for batched same-token withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`describeWithdrawal()` in the POA bridge resolves the on-chain outcome of a specific withdrawal (identified by NEAR tx hash + intent index) by scanning the bridge indexer's response and picking the first record whose `near_token_id` matches the requested `assetId`. It does not verify that the returned record actually corresponds to the requested `index`/`destinationAddress`/`amount`. When a single NEAR transaction contains more than one withdrawal of the same token (a legitimate, SDK-supported scenario via `IntentPayloadBuilder.addIntents()` / composed multi-intents), every such withdrawal resolves to the exact same matched record, so a caller polling for withdrawal at `index: 1` can be told "completed" with a `txHash` that actually belongs to the withdrawal at `index: 0` (different destination address / amount).

### Finding Description
`findMatchingWithdrawal()` is defined as: [1](#0-0) 

The equality that should hold is: *the withdrawal status/hash reported for withdrawal index N must be the on-chain outcome of withdrawal index N*, not of any other withdrawal that happens to share the same token. Instead, the code establishes only:

`nep141:${w.data.near_token_id} === assetId`

with no comparison against `withdrawal.data.address` (destination) or `withdrawal.data.amount`, and no use of `args.index`. This is called from: [2](#0-1) 

The lookup is scoped to `args.tx.hash` (the same NEAR transaction) via `getWithdrawalStatusWithRetry`, so the ambiguity is confined to withdrawals batched in one transaction — but the SDK explicitly supports batching multiple `ft_withdraw` intents into a single signed/published transaction (see `IntentExecuter.signAndSendIntent` composing multiple intents, and `IntentPayloadBuilder.addIntents`): [3](#0-2) 

The code comment itself acknowledges the limitation ("multiple withdrawals of the same token in a single transaction are not supported"), but it does not fail closed — it silently returns a match against the wrong record rather than signaling ambiguity, so callers cannot detect the misattribution.

### Impact Explanation
If a user (or an integrator batching withdrawals on a user's behalf) submits two `ft_withdraw` intents for the same POA token to two different destination addresses/amounts in one NEAR transaction, `describeWithdrawal({index: 1, ...})` can return `{status: "completed", txHash: <hash of index 0's transfer>}` before or instead of index 1's actual transfer. An integrator that credits/refunds based on this status (e.g., `waitForWithdrawalCompletion`, `createWithdrawalCompletionPromises`) can therefore mark a withdrawal complete using a transaction hash that does not correspond to that withdrawal's real destination/amount — a status/hash misreport that can lead to premature completion handling, double crediting, or an integrator being unable to reconcile funds actually delivered to a different address. This matches the "High" impact category: a status/hash misreport making an integrator credit or refund based on the wrong outcome.

### Likelihood Explanation
Reachable without any privileged or malicious actor: any caller using the standard SDK APIs to batch two withdrawals of the same POA-bridged token in one transaction (a normal, documented usage pattern for atomic intent composition) triggers the ambiguous match. No cooperation from the bridge, relayer, or an admin is required.

### Recommendation
`findMatchingWithdrawal` should require a stronger match than `assetId` alone — validate `destinationAddress` and `amount` (and reject with an explicit "ambiguous match" error rather than silently returning a same-token record) so that a status can never be attributed to the wrong withdrawal index. Until POA API returns a per-intent identifier, the SDK should refuse to resolve ambiguous cases (return `pending`/throw) instead of matching by `assetId` only.

### Proof of Concept
1. Build a NEAR transaction with two `ft_withdraw` intents for the same `assetId` (e.g., `nep141:usdc.omft.near`): intent A → 100 USDC to address X, intent B → 100 USDC to address Y, composed via `composeMultiPayloads`/`IntentExecuter.signAndSendIntent`.
2. After the NEAR tx lands, the POA indexer returns both withdrawal records for that `tx.hash` with the same `near_token_id`.
3. Call `poaBridge.describeWithdrawal({ tx, index: 1, withdrawalParams: { assetId, amount: <B's amount>, destinationAddress: Y, ... } })`.
4. `findMatchingWithdrawal` returns `withdrawals.find(...)`, i.e., whichever record (A or B) appears first in the unsorted API response — independent of `index`, `destinationAddress`, or `amount`.
5. If record A is returned first, the caller polling for withdrawal B is told `{status: "completed", txHash: <A's transfer_tx_hash>}`, even though B's actual transfer may still be pending or went to a different address/amount.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-343)
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

		if (withdrawal == null) {
			return { status: "pending" };
		}

		if (withdrawal.status === "PENDING") {
			return { status: "pending" };
		}

		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
		}

		return {
			status: "failed",
			reason: withdrawal.status,
		};
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-427)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	// POA bridge only supports NEP-141 tokens. The API returns `near_token_id`
	// (e.g., "zec.omft.near") which we prefix with "nep141:" to match assetId format.
	// Note: `defuse_asset_identifier` cannot be used as it contains chain-native
	// format (e.g., "zec:mainnet:native") which differs from the assetId format.
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

**File:** packages/intents-sdk/src/intents/intent-payload-builder.ts (L107-116)
```typescript
	/**
	 * Add multiple intents to the payload at once.
	 *
	 * @param intents - Array of intent primitives to add
	 * @returns The builder instance for chaining
	 */
	addIntents(intents: IntentPrimitive[]): this {
		this.intents.push(...intents);
		return this;
	}
```
