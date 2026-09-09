### Title
PoA Bridge misreports withdrawal completion status/hash for batched same-asset withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
When multiple withdrawals of the same asset are batched into a single NEAR intent transaction, `PoaBridge.describeWithdrawal` cannot correctly distinguish between them and will report the same status/txHash for withdrawals that are actually different, distinct on-chain outcomes.

### Finding Description
`IntentsSDK.createWithdrawalCompletionPromises` / `waitForWithdrawalCompletion` explicitly support batching an array of `WithdrawalParams` against a single `intentTx`, tracked and resolved per-index via `WithdrawalIdentifier.index` [1](#0-0) . The documented invariant is that "Array index of returned promise matches array index of input `withdrawalParams`" and each promise "resolves independently when its withdrawal completes" [2](#0-1) .

However, `PoaBridge.describeWithdrawal` does not use the per-withdrawal `index` at all to correlate the API response to the correct withdrawal; it looks up the withdrawal by `assetId` only, via `findMatchingWithdrawal`, which does a plain `.find()` over all withdrawals in the transaction: [3](#0-2) [4](#0-3) 

The code comment itself acknowledges the limitation: "multiple withdrawals of the same token in a single transaction are not supported" [5](#0-4) . But nothing in `sdk.ts`, `createWithdrawalIdentifiers`, or `PoaBridge.supports`/`validateWithdrawal` actually prevents an integrator from submitting a batch containing two or more withdrawals of the same `assetId` (e.g., same token, different `destinationAddress`/`amount`) through `signAndSendWithdrawalIntent`/`processWithdrawal` [6](#0-5) . When that happens, `Array.prototype.find` will always return the *first* matching withdrawal in the API's (documented as "unsorted") response for every index that shares that `assetId`. As a result, `watchWithdrawal` — which just checks `status.status === "completed"` and returns the reported `txHash` [7](#0-6)  — will resolve multiple distinct withdrawal promises with the *same* completed status and the *same* destination transaction hash, even though only one of the withdrawals (to one destination address, for one amount) has actually completed on-chain.

This breaks the equality "status/hash reported == actual on-chain outcome for that specific withdrawal index," analogous to the H-14 report's root cause: a check/lookup that ignores an identity/index dimension that should have gated the result, causing state for one entity to be conflated with another.

### Impact Explanation
An integrator relying on `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion`/`processWithdrawal` for a batch containing two same-asset PoA withdrawals to different addresses would see both promises resolve as "completed" with the same `txHash` as soon as the first of the two settles on-chain. This directly matches the "status or hash misreport making an integrator credit or refund twice" High-impact category: the integrator could mark both withdrawals (and thus credit or unlock associated off-chain state for both users/amounts) as fulfilled while only one on-chain transfer has actually occurred, and the second recipient never actually receives funds until it is separately confirmed (or possibly never, since the second entry's promise resolved on a hash that pertains to a different transfer).

### Likelihood Explanation
This requires no privileged or malicious relayer/bridge behavior — it is purely a client-side (SDK) lookup defect triggered whenever a normal, currently-unblocked usage pattern occurs: batching two withdrawals of the same token in one intent via the public batch API. Since batch withdrawals with `withdrawalParams: WithdrawalParams[]` are a first-class, documented SDK feature and no validation rejects duplicate `assetId`s in a batch, an integrator can trigger this unintentionally simply by allowing users to withdraw the same token to two addresses in one transaction.

### Recommendation
- Reject batches at the SDK level (`signAndSendWithdrawalIntent`/`createWithdrawalIntents`) that contain more than one `WithdrawalParams` entry with the same `assetId` routed through `PoaBridge`, until the POA bridge API supports disambiguation, OR
- Implement the correlation strategy the code comment already proposes: sort both the API `withdrawals` response and the local `withdrawalParams` (filtered to the same `assetId`) by `amount` (since relayer fees are equal for same-token withdrawals, relative ordering is preserved) and match positionally instead of via unconditional `.find()`, so each index in the batch is bound to the correct entry in the API response.

### Proof of Concept
1. Caller uses `sdk.signAndSendWithdrawalIntent({ withdrawalParams: [ {assetId: "nep141:btc.omft.near", destinationAddress: "addrA", amount: 100000n}, {assetId: "nep141:btc.omft.near", destinationAddress: "addrB", amount: 200000n} ], ... })`, producing one NEAR intent tx with two POA `ft_withdraw` actions for the same token.
2. Caller then calls `sdk.createWithdrawalCompletionPromises({ withdrawalParams, intentTx })`, yielding index-0 and index-1 promises, both routed to `PoaBridge.describeWithdrawal`.
3. POA bridge's withdrawal-status API returns an unsorted array of withdrawal records; because `findMatchingWithdrawal` filters purely by `nep141:${near_token_id} === assetId` [8](#0-7) , both index-0 and index-1 lookups return the *same* first matching record.
4. Once that one withdrawal (say, to `addrA`) completes, both promises resolve `{ status: "completed", txHash: <addrA's tx hash> }`, even though the withdrawal to `addrB` may still be pending or has a different transaction hash.

### Citations

**File:** packages/intents-sdk/src/shared-types.ts (L434-441)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}
```

**File:** docs/design/rfc-batch-withdrawal-granular-control.md (L279-266)
```markdown

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

**File:** packages/intents-sdk/src/sdk.ts (L689-743)
```typescript
	public async signAndSendWithdrawalIntent(
		args:
			| SignAndSendWithdrawalArgs<WithdrawalParams>
			| SignAndSendWithdrawalArgs<WithdrawalParams[]>,
	): Promise<IntentPublishResult> {
		let withdrawalParamsArray: WithdrawalParams[];
		let feeEstimations: FeeEstimation[];
		if (isBatchMode(args)) {
			withdrawalParamsArray = args.withdrawalParams;
			feeEstimations = args.feeEstimation;
		} else {
			withdrawalParamsArray = [args.withdrawalParams];
			feeEstimations = [args.feeEstimation];
		}

		const intentsP = zip(withdrawalParamsArray, feeEstimations).map(
			([withdrawalParams, feeEstimation]) => {
				return this.createWithdrawalIntents({
					withdrawalParams,
					feeEstimation,
					referral: args.referral ?? this.referral,
					logger: args.logger,
				});
			},
		);

		const intents = (await Promise.all(intentsP)).flat();

		const relayParamsFn: IntentRelayParamsFactory = async () => {
			const relayParams =
				args.intent?.relayParams != null
					? await args.intent?.relayParams()
					: { quoteHashes: undefined };

			const quoteHashes = relayParams.quoteHashes ?? [];

			for (const fee of feeEstimations) {
				if (fee.quote != null) {
					quoteHashes.push(fee.quote.quote_hash);
				}
			}

			return { ...relayParams, quoteHashes };
		};

		return this.signAndSendIntent({
			intents,
			signer: args.intent?.signer,
			onBeforePublishIntent: args.intent?.onBeforePublishIntent,
			relayParams: relayParamsFn,
			payload: args.intent?.payload,
			logger: args.logger,
			signedIntents: args.intent?.signedIntents,
		});
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
