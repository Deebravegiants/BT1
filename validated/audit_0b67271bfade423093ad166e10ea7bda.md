The finding is confirmed and directly acknowledged in the source code itself: `findMatchingWithdrawal` explicitly matches only by `assetId` via `withdrawals.find(...)`, returning the first array match regardless of `index`, with an inline comment admitting "multiple withdrawals of the same token in a single transaction are not supported."No additional guard exists that deduplicates or checks for same-assetId batch withdrawals before `createWithdrawalIdentifiers`/`watchWithdrawal` — nothing prevents multiple `WithdrawalParams` entries sharing the same `assetId` in one call, and the per-bridge `index` counter in `createWithdrawalIdentifiers` still assigns sequential indices independent of the underlying API's ability to disambiguate.

### Title
PoA bridge `findMatchingWithdrawal` conflates same-asset withdrawals in a batch, causing cross-withdrawal status/txHash misreport - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain status/txHash for a given `WithdrawalIdentifier` purely by matching `assetId` against the PoA bridge indexer's unsorted withdrawal list, ignoring `index`. When a single intent batch contains two withdrawals of the same PoA asset (e.g., two `nep141:btc.omft.near` withdrawals to different destination addresses), both `WithdrawalIdentifier` entries (index 0 and index 1) resolve to the same array element, so an integrator can receive the same `status`/`txHash` for two distinct withdrawals.

### Finding Description
The broken equality: `describeWithdrawal({index: 0, assetId: A}).txHash` should correspond to withdrawal 0's own on-chain transfer, and `describeWithdrawal({index: 1, assetId: A}).txHash` should correspond to withdrawal 1's own on-chain transfer — these must be independent when both withdrawals share `assetId`. In `findMatchingWithdrawal` [1](#0-0)  the lookup is `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)`, which returns the first array element matching only on `assetId`, with no use of `index`, `destinationAddress`, or `amount` to disambiguate. The comment directly above this function [2](#0-1)  acknowledges: "multiple withdrawals of the same token in a single transaction are not supported."

The call path: `sdk.createWithdrawalCompletionPromises` builds one polling promise per withdrawal via `createWithdrawalIdentifiers`, which assigns a strictly increasing per-bridge-route `index` [3](#0-2) . Each resulting `WithdrawalIdentifier` (differing in `index` and `withdrawalParams.destinationAddress`, but sharing `assetId`) is passed to `watchWithdrawal`, which calls `bridge.describeWithdrawal({...args.wid, logger})` on every poll [4](#0-3) . `PoaBridge.describeWithdrawal` [5](#0-4)  then calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` — for both index-0 and index-1 calls, since `assetId` is identical, `Array.prototype.find` returns the same first-matching element from the API response array regardless of which withdrawal is actually being queried.

Attacker input: any ordinary user submits one intent with a batch of two POA withdrawals of `nep141:btc.omft.near`, one to `destinationAddressA`, one to `destinationAddressB`. No documented escape hatch or malicious external actor is required — this is normal SDK usage with public methods and legitimate parameters.

None of the existing guards prevent this: `supports()` only checks assetId eligibility per withdrawal individually and is not aware of sibling withdrawals in the batch; `validateWithdrawal`/`validateAddress`/`compareAddresses` validate address format and min-amount per-withdrawal but never cross-reference other withdrawals in the same batch; there is no dedupe check in `sdk.ts`'s batch construction; and the PoA bridge indexer API itself returns an unsorted list with no positional/index field to correlate back to the request order (as acknowledged in the code comment).

### Impact Explanation
An integrator watching both withdrawals via `sdk.createWithdrawalCompletionPromises`/`watchWithdrawal` receives the identical `{status: "completed", txHash: X}` for both withdrawal 0 and withdrawal 1, even though only one of them actually completed with hash X (the other's real destination-chain hash is silently never surfaced, or worse, both are reported "completed" with the same hash while only one transfer actually happened on-chain). An integrator that credits/refunds a user's off-chain ledger balance based on `(status, txHash)` per withdrawal index will double-credit funds for the withdrawal that never received its own distinct confirmation, matching the "status or hash misreport making an integrator credit or refund twice" High-severity category (and can escalate toward Critical-level fund loss depending on how the integrator reconciles). This is repeatable on every batch that contains ≥2 same-asset withdrawals to the PoA bridge.

### Likelihood Explanation
Preconditions are trivial and require no privilege beyond normal SDK usage: submit a batch withdrawal intent with two `WithdrawalParams` entries sharing the same PoA `assetId` (any NEP-141 token bridged via PoA, e.g., `nep141:btc.omft.near`), with different `destinationAddress` values. This is a natural usage pattern (e.g., withdrawing the same asset to two different addresses in one transaction) and costs the attacker only the normal withdrawal fee/gas — no special access or racing is needed. The bug is deterministic given the array-ordering behavior of `Array.prototype.find` combined with the indexer's unsorted response, so it reproduces on essentially every such batch, not just occasionally.

### Recommendation
`findMatchingWithdrawal` needs a disambiguation strategy beyond `assetId` when multiple withdrawals share the same asset — e.g., match by `(assetId, destinationAddress)` pair, or, if the API doesn't expose enough correlating data, deterministically sort both the request-side and response-side withdrawal lists by amount (as the code comment itself suggests) and assign by relative position, since PoA relayer fees are identical for same-token withdrawals so amount ordering is preserved. At minimum, `PoaBridge` should detect the ambiguous case (multiple response withdrawals matching the same assetId within a single batch) and either throw/return `pending` rather than silently returning a value that may belong to a different withdrawal in the batch.

### Proof of Concept
```ts
// vitest, mocking poaBridge.httpClient.getWithdrawalStatus only
vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
  withdrawals: [
    {
      status: "COMPLETED",
      data: {
        tx_hash: "near-tx-hash",
        transfer_tx_hash: "dest-tx-hash-A", // belongs to withdrawal 0 -> addressA
        chain: "btc",
        defuse_asset_identifier: "nep141:btc.omft.near",
        near_token_id: "btc.omft.near",
        decimals: 8,
        amount: 100000,
        account_id: "test.near",
        address: "addressA",
        created: "2024-01-01T00:00:00Z",
      },
    },
    {
      status: "COMPLETED",
      data: {
        tx_hash: "near-tx-hash",
        transfer_tx_hash: "dest-tx-hash-B", // belongs to withdrawal 1 -> addressB
        chain: "btc",
        defuse_asset_identifier: "nep141:btc.omft.near",
        near_token_id: "btc.omft.near",
        decimals: 8,
        amount: 100000,
        account_id: "test.near",
        address: "addressB",
        created: "2024-01-01T00:00:00Z",
      },
    },
  ],
});

const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });

const wid0 = { landingChain: Chains.Bitcoin, index: 0,
  withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addressA", feeInclusive: false },
  tx: { hash: "near-tx-hash", accountId: "test.near" } };

const wid1 = { landingChain: Chains.Bitcoin, index: 1,
  withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addressB", feeInclusive: false },
  tx: { hash: "near-tx-hash", accountId: "test.near" } };

const result0 = await bridge.describeWithdrawal(wid0);
const result1 = await bridge.describeWithdrawal(wid1);

// STATUS_TRUTH broken: withdrawal 1 (destined for addressB) is reported
// with withdrawal 0's txHash ("dest-tx-hash-A"), not "dest-tx-hash-B".
expect(result0).toEqual({ status: "completed", txHash: "dest-tx-hash-A" });
expect(result1).toEqual({ status: "completed", txHash: "dest-tx-hash-A" }); // WRONG: should be "dest-tx-hash-B"
expect(result0.txHash).toBe(result1.txHash); // demonstrates the collision
```

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-417)
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L418-427)
```typescript
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-47)
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
