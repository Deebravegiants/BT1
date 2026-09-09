### Title
PoA Bridge `describeWithdrawal` Misreports Status by Matching on `assetId` Only, Causing Withdrawal Conflation in Batches - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` determines the on-chain status/txHash of a specific withdrawal by calling `findMatchingWithdrawal()`, which matches entries in the POA API response purely by `assetId`, ignoring the `index`/amount that uniquely identifies each withdrawal within a batch. When a caller submits multiple withdrawals of the same token in a single intent (which the SDK's `signAndSendWithdrawalIntent` explicitly supports via its batch mode), every `describeWithdrawal` call for that `assetId` returns the same matched record — the first one found — regardless of which withdrawal index is actually being queried.

### Finding Description
The equality that should hold is: *the status/txHash reported for withdrawal N is the actual on-chain outcome of withdrawal N*. `findMatchingWithdrawal` breaks this by using `assetId` as the sole matching key: [1](#0-0) 

`describeWithdrawal` then returns whatever that (possibly wrong) record says without validating it against the specific `index`: [2](#0-1) 

The SDK's own `createWithdrawalIdentifiers` assigns a per-bridge/per-route `index` counter specifically to disambiguate multiple withdrawals routed to the same bridge: [3](#0-2) 

And `signAndSendWithdrawalIntent` / `processWithdrawal` explicitly support batches of `WithdrawalParams`, which can legitimately contain repeated `assetId`s (e.g. splitting one withdrawal across two destination addresses of the same token): [4](#0-3) [5](#0-4) 

Because `findMatchingWithdrawal` always returns the *first* record whose `near_token_id` matches, `describeWithdrawal({index: 0, ...})` and `describeWithdrawal({index: 1, ...})` for two same-asset withdrawals in one NEAR transaction will both resolve to the identical POA record — same status, same `transfer_tx_hash`. The `watchWithdrawal` poller in `withdrawal-watcher.ts` will consequently report **both** withdrawals as `completed` with the **same destination tx hash**, even though only one of them has actually settled on the destination chain and the other's transfer has not been produced (or was routed to a different address for a different amount): [6](#0-5) 

The code comment acknowledges the limitation but frames it only as "not supported" rather than flagging the resulting status corruption: [7](#0-6) 

### Impact Explanation
An integrator relying on `processWithdrawal`/`waitForWithdrawalCompletion` results to credit downstream ledgers, mark invoices paid, or release custody would receive a "completed" status with a valid-looking destination tx hash for a withdrawal that never actually completed (its counterpart's hash is reported instead). This matches the High-impact criterion of "a status or hash misreport making an integrator credit or refund twice": the integrator could believe the second withdrawal succeeded (crediting/closing it) while the funds for that specific withdrawal are still in flight or went to a different destination address than the reported hash implies.

### Likelihood Explanation
Any unprivileged caller of the SDK can trigger this simply by submitting a batch withdrawal (`signAndSendWithdrawalIntent`/`processWithdrawal` with an array of `withdrawalParams`) containing two or more entries with the same `assetId` routed through the POA bridge — a normal, documented usage pattern (batch withdrawals are a first-class SDK feature). No malicious relayer, admin, or bridge operator behavior is required; the misreport occurs purely from the SDK's own status-matching logic operating on legitimate POA API responses.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId`. At minimum, incorporate `amount` (and consume matched records so subsequent lookups for the same `assetId` do not re-match the same entry) or use `index` to pick the Nth same-asset withdrawal, consistent with how `createWithdrawalIdentifier` assigns indexes. Until the POA API itself exposes a per-transfer discriminator, `describeWithdrawal` should refuse to report `completed` for a given index if more than one same-asset withdrawal from the same NEAR tx is outstanding and cannot be uniquely matched, rather than silently returning another withdrawal's result.

### Proof of Concept
1. Attacker/integrator calls `sdk.signAndSendWithdrawalIntent` (or `processWithdrawal`) with `withdrawalParams: [{assetId: "nep141:usdt.omft.near", amount: A, destinationAddress: addrX}, {assetId: "nep141:usdt.omft.near", amount: B, destinationAddress: addrY}]` — a legitimate batch withdrawal of the same token to two different destinations, producing indexes 0 and 1 via `createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`).
2. Only the withdrawal to `addrX` (index 0) settles on the POA relayer and appears as `COMPLETED` with `transfer_tx_hash = H` in the POA API response; the withdrawal to `addrY` (index 1) is still `PENDING`.
3. Caller polls status for index 1 via `bridge.describeWithdrawal({..., index: 1})`. `findMatchingWithdrawal` (`poa-bridge.ts:418-427`) ignores `index` and returns the first record matching `assetId`, i.e., the `COMPLETED` record for index 0.
4. `describeWithdrawal` (`poa-bridge.ts:313-343`) reports `{status: "completed", txHash: H}` for index 1 even though the withdrawal to `addrY` never happened.
5. `watchWithdrawal` (`core/withdrawal-watcher.ts:20-53`) resolves successfully for both indexes with the same `txHash: H`, causing the integrator to treat the withdrawal to `addrY` as completed and credit/close it — a double-credit based on a single actual transfer.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-53)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

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

**File:** packages/intents-sdk/src/sdk.ts (L793-857)
```typescript
	async processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams | WithdrawalParams[]>,
	): Promise<WithdrawalResult | BatchWithdrawalResult> {
		const withdrawalParams = Array.isArray(args.withdrawalParams)
			? args.withdrawalParams
			: [args.withdrawalParams];

		// Step 1: Estimate fee
		const feeEstimation = await (() => {
			if (args.feeEstimation != null) {
				return Array.isArray(args.feeEstimation)
					? args.feeEstimation
					: [args.feeEstimation];
			}

			return this.estimateWithdrawalFee({
				withdrawalParams,
				logger: args.logger,
			});
		})();

		// Step 2: Sign and send intent
		const { intentHash } = await this.signAndSendWithdrawalIntent({
			withdrawalParams,
			feeEstimation,
			referral: args.referral,
			intent: args.intent,
			logger: args.logger,
		});

		args.logger?.info("Intent published", { intentHash });

		// Step 3: Wait for intent settlement
		const intentTx = await this.waitForIntentSettlement({
			intentHash: intentHash,
			logger: args.logger,
		});

		args.logger?.info("Intent settled", { txHash: intentTx.hash });

		// Step 4: Wait for withdrawal completion
		const destinationTx = await this.waitForWithdrawalCompletion({
			withdrawalParams,
			intentTx,
			logger: args.logger,
		});

		if (!Array.isArray(args.withdrawalParams)) {
			return {
				// biome-ignore lint/style/noNonNullAssertion: single withdrawal returns single-element arrays
				feeEstimation: feeEstimation[0]!,
				intentHash,
				intentTx,
				// biome-ignore lint/style/noNonNullAssertion: single withdrawal returns single-element arrays
				destinationTx: destinationTx[0]!,
			};
		}

		return {
			feeEstimation,
			intentHash,
			intentTx,
			destinationTx,
		};
	}
```
