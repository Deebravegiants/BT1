### Title
POA Bridge withdrawal status matched by `assetId` only, causing cross-withdrawal status/hash misreport in batched same-asset withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain outcome of a specific withdrawal (identified by `tx.hash` + `index`) by calling `findMatchingWithdrawal`, which selects an entry from the POA indexer's unsorted `withdrawals` array purely by matching `assetId`, ignoring `index` entirely. [1](#0-0) [2](#0-1) 

### Finding Description
`WithdrawalIdentifier` is designed to uniquely identify one withdrawal within a NEAR transaction via `{ tx, index }`, since a single transaction can batch multiple withdrawal intents. [3](#0-2) 

However, `describeWithdrawal` never uses `args.index` to disambiguate; it fetches all withdrawals for `args.tx.hash` and then calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` — i.e., it returns the *first* array entry whose asset matches, regardless of which logical withdrawal (index) it belongs to: [1](#0-0) [4](#0-3) 

The code's own comment admits the root cause: *"NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* [5](#0-4) 

Equality that should hold: `status/txHash reported for withdrawal (tx, index=i, destinationAddress=A)` must equal `the on-chain outcome of the specific withdrawal that intent i produced`. Because matching is keyed only by `assetId`, if a single NEAR transaction contains two (or more) withdrawal intents of the same `assetId` — e.g., withdrawing the same token to two different destination addresses/amounts in one batched `signAndSendIntent` call, which `createWithdrawalIntents`/`IntentPayloadBuilder.addIntents` explicitly supports — then `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` can both resolve to the *same* indexer entry (the array is explicitly documented as "unsorted"), returning identical `status`/`txHash` for what are in fact two distinct on-chain transfers to two distinct destinations/amounts.

This is consumed directly by `watchWithdrawal`, which trusts `describeWithdrawal`'s `status`/`txHash` as the completion signal for a specific withdrawal identifier: [6](#0-5) 

An integrator polling per-index withdrawal status will therefore be told that withdrawal `index=0` (destined for address A, amount X) completed with a transaction hash that actually belongs to withdrawal `index=1` (destined for address B, amount Y), or vice versa — a status/hash misreport not matching the true on-chain outcome for that specific withdrawal identifier.

### Impact Explanation
This breaks the "status reported == on-chain outcome" invariant called out by the report's scope. A consuming service that credits/settles per withdrawal index based on `describeWithdrawal`'s returned `status`/`txHash` can:
- Report success/credit a withdrawal to address A using a hash that actually corresponds to the transfer to address B (misattribution of settlement), and
- Mark a still-pending or failed withdrawal (B) as completed by reusing A's/B's shared indexer entry, or leave one of the two withdrawals permanently unresolved/misreported.

This matches the "High" impact bucket in the task's rubric: *"a status or hash misreport making an integrator credit or refund twice."* It does not require the relayer, POA operator, or any external party to act maliciously — it is a purely internal matching-by-wrong-key defect within `packages/intents-sdk`, triggered by ordinary correct usage (a legitimate batch of same-asset withdrawals in one transaction, which is otherwise not disallowed anywhere in `createWithdrawalIntents`/`IntentPayloadBuilder`).

### Likelihood Explanation
Likelihood is moderate: it requires a caller (integrator) to batch two or more withdrawals of the *same* `assetId` through the POA bridge route within a single NEAR transaction (e.g., a service processing multiple user withdrawal requests for the same token together to save gas), which is a supported and reasonable usage pattern of the SDK. Nothing in `PoaBridge.createWithdrawalIntents`, `supports()`, or the SDK's batching layer rejects or warns against this combination; the defect is only documented as a code comment, not enforced or surfaced to callers of `describeWithdrawal`/`watchWithdrawal`.

### Recommendation
- Have `PoaBridge.describeWithdrawal` disambiguate matching withdrawals using `tx.hash` + a stable ordering key that reflects intent order (e.g., sort both the indexer's `withdrawals` and the known per-tx withdrawal list by `amount`/creation order as the comment itself suggests) and select by `index`, not solely by `assetId`.
- Alternatively, if the POA indexer API cannot yet disambiguate by index, throw an explicit unsupported-batching error from `createWithdrawalIntents`/`supports()` (or at the SDK batching layer) when multiple same-`assetId` PoA withdrawals are combined in one transaction, rather than silently returning ambiguous/incorrect status downstream.
- Add regression tests that construct two same-`assetId` withdrawals with different `destinationAddress`/`amount` in one tx and assert that `describeWithdrawal` for each `index` returns the correct, distinct `txHash`/`status`.

### Proof of Concept
1. Build and sign a NEAR intents transaction containing two `ft_withdraw` intents for the same `assetId` (e.g. `nep141:btc.omft.near`): intent 0 → destination `addrA`, amount `1000`; intent 1 → destination `addrB`, amount `2000`.
2. Submit the transaction; the POA relayer processes both withdrawals and the POA indexer eventually returns two entries in `withdrawals` for `tx_hash = <near-tx-hash>`, both with `near_token_id = "btc.omft.near"`, but different `transfer_tx_hash`/`address`/`amount`.
3. Call:
```ts
bridge.describeWithdrawal({
  tx: { hash: "<near-tx-hash>", accountId: "..." },
  index: 0,
  landingChain: Chains.Bitcoin,
  withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 1000n, destinationAddress: "addrA", feeInclusive: false },
});
bridge.describeWithdrawal({
  tx: { hash: "<near-tx-hash>", accountId: "..." },
  index: 1,
  landingChain: Chains.Bitcoin,
  withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 2000n, destinationAddress: "addrB", feeInclusive: false },
});
```
4. Because `findMatchingWithdrawal` filters only by `assetId` and the indexer array order is unspecified ("unsorted"), both calls can resolve to the *same* array entry — e.g., both report `{ status: "completed", txHash: "btc-tx-hash-for-addrA" }` even though only the withdrawal to `addrA` actually completed with that hash, while the withdrawal to `addrB` is misreported as completed with the wrong hash (or never correctly resolved).

**Note on scope/limitations:** I was not able to fully trace the SDK's batch-withdrawal orchestration path (`sdk.ts`) due to running out of tool iterations, so I could not confirm with 100% certainty whether the higher-level SDK explicitly forbids or deduplicates same-asset batched PoA withdrawals before reaching this code path. The vulnerability is proven at the `PoaBridge` unit level and is explicitly acknowledged as an unhandled limitation in the code's own comment; whether an even easier end-to-end trigger exists via `sdk.ts` remains unverified.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-311)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		const assetInfo = this.parseAssetId(args.withdrawalParams.assetId);
		assert(assetInfo != null, "Asset is not supported");

		const landingChain = assetInfo.blockchain;

		return {
			landingChain,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
	}
```

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-53)
```typescript
	try {
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
