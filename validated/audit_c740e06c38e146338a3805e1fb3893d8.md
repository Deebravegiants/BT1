### Title
POA Bridge withdrawal status matches by `assetId` only, causing status/tx-hash misattribution across batched withdrawals of the same token - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain completion status of a withdrawal by matching the POA bridge API response using only the `assetId`, ignoring the specific withdrawal `index`/destination/amount. When a batch of withdrawals routed through POA bridge contains two or more withdrawals of the same token (same `assetId`, different destinations/amounts), every one of those withdrawals resolves to the same matched API entry, so the wrong `txHash`/status can be reported for a given withdrawal identifier.

### Finding Description
`describeWithdrawal` fetches all withdrawals for the NEAR transaction and calls `findMatchingWithdrawal`, which does: [1](#0-0) [2](#0-1) 

The function's own comment acknowledges the equality it fails to preserve: *"multiple withdrawals of the same token in a single transaction are not supported"* and matching is done purely by `assetId`, not by `index`, amount, or destination address. `createWithdrawalIdentifiers` builds one `WithdrawalIdentifier` per withdrawal in a batch and assigns a per-bridge `index`: [3](#0-2) 

`signAndSendWithdrawalIntent` explicitly supports arrays of `withdrawalParams`, i.e., a caller can request a batch containing two withdrawals with the same `assetId` (same POA token) but different `destinationAddress`/`amount`: [4](#0-3) 

Because `findMatchingWithdrawal` only checks `nep141:${w.data.near_token_id} === assetId` and returns the first array match, calling `describeWithdrawal` for withdrawal index 0 and withdrawal index 1 (same token) both resolve to the *same* underlying POA record — the same `status` and the same `transfer_tx_hash` — even though the two withdrawals are distinct on-chain outcomes going to different addresses/amounts. This breaks the equality "the status/txHash reported for withdrawal N corresponds to the on-chain outcome of withdrawal N."

### Impact Explanation
An integrator that polls per-withdrawal status (via `describeWithdrawal`/`WithdrawalIdentifier`) to decide when to credit a user or reconcile a withdrawal as settled can receive the identical `txHash` and `completed` status for two distinct withdrawals in the same batch. This can cause the integrator to treat both withdrawals as confirmed by the same on-chain transaction, i.e., credit/close out a withdrawal that has not actually landed, or use one confirmed hash as proof for two different amounts/destinations — a status/hash misreport that can lead an integrator to credit or refund twice, matching the High-impact category defined in scope.

### Likelihood Explanation
This requires only a normal (unprivileged) SDK caller to submit a batch withdrawal containing two or more withdrawals of the same POA-bridged asset (e.g., withdrawing the same token to two different addresses) — no malicious relayer, bridge operator, or admin involvement is needed. Batch withdrawals are a first-class supported feature of `signAndSendWithdrawalIntent`, so the trigger condition is easily reachable through the SDK's own public API. The bridge/API-side constraint is documented in code, indicating the condition is realistic, not purely theoretical.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId`: use `index` in combination with a stable secondary key (e.g., match by sorting both the SDK's requested withdrawals and the API's returned withdrawals for the same `assetId` by `amount`, or by destination/memo, as the code comment itself suggests), and only resolve a status for a given `WithdrawalIdentifier` when a unique correspondence can be established. If uniqueness cannot be guaranteed, `describeWithdrawal` should return `pending`/an explicit ambiguity error rather than reusing another withdrawal's hash, and downstream consumers (integrators) should be warned not to rely on `txHash` uniqueness when a batch contains repeated `assetId`s.

### Proof of Concept
1. Call `sdk.signAndSendWithdrawalIntent` with `withdrawalParams` = `[{assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addrA"}, {assetId: "nep141:btc.omft.near", amount: 250000n, destinationAddress: "addrB"}]` — both routed via `PoaBridge`.
2. `createWithdrawalIdentifiers` produces two identifiers with the same `route`/`assetId` but `index: 0` and `index: 1`.
3. Once the POA bridge processes and completes withdrawal 0 (to `addrA`) while withdrawal 1 (to `addrB`) is still pending, call `bridge.describeWithdrawal(widIndex1)`.
4. `findMatchingWithdrawal` finds the only POA withdrawal record matching `nep141:btc.omft.near` — the one for `addrA`/`100000` — and returns `{status: "completed", txHash: <addrA's tx hash>}` for the identifier that actually corresponds to the still-pending `addrB`/`250000` withdrawal, per: [5](#0-4)

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

**File:** packages/intents-sdk/src/sdk.ts (L689-713)
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
```
