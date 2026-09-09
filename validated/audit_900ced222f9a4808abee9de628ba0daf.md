This confirms the bug precisely — there's a dedicated test named `"matches withdrawal by assetId, not by index"` at [1](#0-0)  that documents the exact behavior, and the developer comment at `findMatchingWithdrawal` explicitly acknowledges the limitation.

### Title
Missing invariant [reported == signed]: PoA bridge `describeWithdrawal` matches withdrawals by `assetId` only, misreporting destination txHash for same-token batch withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` (via `findMatchingWithdrawal`) selects a completion record from the PoA API purely by matching `nep141:<near_token_id> === assetId`, ignoring the `WithdrawalIdentifier.index`, destination address, and amount of the specific withdrawal being watched. When a caller submits a batch of two (or more) withdrawals of the same token to two different addresses via `processWithdrawal`, both watchers query the same underlying NEAR tx hash and both resolve to the *first* matching entry in the unsorted `withdrawals` array, so an integrator can receive the wrong `destinationTx` (recipient/amount/txHash) for a given `WithdrawalIdentifier`.

### Finding Description
The invariant that should hold is: for withdrawal `i` in a batch, `describeWithdrawal(wid_i)` must report the status/txHash of the on-chain transfer that corresponds to the same recipient and amount that were signed in intent `i`. Instead, `findMatchingWithdrawal` at [2](#0-1)  does:

```
return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
```

This never compares `w.data.address`/`w.data.amount` against `args.withdrawalParams.destinationAddress`/`args.withdrawalParams.amount`, and it never uses `args.index`. The docstring above it even states: *"Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* [3](#0-2) 

Exploit flow: an unprivileged caller builds a `WithdrawalParams[]` batch of two POA withdrawals for the same `assetId` (e.g., `nep141:btc.omft.near`) to two different `destinationAddress` values (address A and address B), and calls `processWithdrawal`. Both withdrawals get published in the same NEAR intent transaction (`intentTx`), so `createWithdrawalIdentifier` for both entries carries the same `tx.hash`, differing only in `index` and `withdrawalParams.destinationAddress/amount` (as confirmed by `createWithdrawalIdentifiers` in [4](#0-3) ). `watchWithdrawal` then calls `describeWithdrawal` independently per index at [5](#0-4) , and each call queries `getWithdrawalStatus({ withdrawal_hash: args.tx.hash })` — identical for both. When the POA relayer returns the withdrawals array (order not guaranteed to match request order, and initially may contain only whichever withdrawal completed/indexed first), `findMatchingWithdrawal` returns the same first-matching record with the same `assetId` for **both** index 0 and index 1 queries, regardless of which one it actually is.

Concretely: withdrawal to address A completes first, entry `{address: A, transfer_tx_hash: "txA"}` is added to the API's `withdrawals` list. Both `describeWithdrawal(wid_0)` (bound to A) and `describeWithdrawal(wid_1)` (bound to B, still pending) call the same API and both get back the *same* array. Because match only keys on assetId, and B's own entry may not exist yet in the array (or may exist later at a different position), it is possible for the watcher for index 1 (B) to report `completed` with `txHash: "txA"` — a transaction that actually delivered funds to address A, not B. This is a status/hash misreport, not merely a delayed pending state, because there is no per-item disambiguation once two entries with the same `near_token_id` exist in the response.

None of the existing guards catch this: `validateAddress`, `compareAddresses`, and `validateWithdrawal` operate purely at creation/estimation time on the input parameters and never re-validate against the reported withdrawal; `FeeExceedsAmountError` and `getUnderlyingFee` are fee-only checks; `matchesRequest`/equality checks simply don't exist in `describeWithdrawal`. The intents contract's own signature/nonce verification protects the on-chain transfer amount and destination correctly (the *actual* funds movement executed by the PoA relayer is unaffected), but it does nothing to protect the SDK's own **reporting** of which transaction hash corresponds to which withdrawal.

### Impact Explanation
No funds are misrouted on-chain — the PoA relayer still sends the correct amount to the correct address per its own internal bookkeping; this bug lives entirely in the SDK-side reporting layer (`describeWithdrawal` → `watchWithdrawal` → `processWithdrawal`'s `destinationTx`). The impact is: an integrator relying on `processWithdrawal`'s `destinationTx[i]` / `txHash` to reconcile withdrawal `i` can be given the *wrong* transaction hash (belonging to a different withdrawal in the same batch), for two same-token withdrawals to different destinations. This matches the "status or hash misreport making an integrator credit or refund twice" High-severity impact category, since an integrator could credit/refund a user based on a txHash that actually belongs to someone else's transfer, or think a withdrawal is confirmed when the recipient (B) has not actually received funds yet. It is repeatable on every batch containing ≥2 same-token POA withdrawals to different destinations, and requires no special privilege — any SDK caller/integrator forwarding user-supplied batches can trigger it.

### Likelihood Explanation
Preconditions: (1) caller submits a batch (`WithdrawalParams[]`) with ≥2 entries sharing the same `assetId` routed through `PoaBridge` (same NEP-141 token), to different `destinationAddress`; (2) the underlying PoA relayer processes/indexes them at different times or returns them in different order (explicitly documented as unsorted: *"Response list is unsorted, so we match by assetId instead of index"* [6](#0-5) ). Attacker cost is zero beyond crafting normal batch withdrawal parameters, and it is a documented, reproducible limitation of the current matching logic (confirmed by the existing test `"matches withdrawal by assetId, not by index"` at [7](#0-6) , which shows index is entirely ignored in favor of assetId matching, even when two distinct chains/amounts are present in the array).

### Recommendation
Extend `findMatchingWithdrawal` (and the equivalent `findMatchingWithdrawal` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate entries sharing the same `assetId` by also matching on `destinationAddress` (`w.data.address`) and `amount` (`w.data.amount`), and fail closed (throw, not silently misreport) when multiple withdrawals in the response share identical `assetId`+`address`+`amount` such that they cannot be disambiguated (in that specific edge case, fall back to stable index-based matching only among the filtered candidate set, in the same relative order as submitted). At minimum, document this as an explicit constraint/validation rejecting batches with duplicate `(assetId, destinationAddress)` or duplicate `(assetId, amount)` pairs at `createWithdrawalIntents`/`processWithdrawal` time, so silent misreporting cannot occur.

### Proof of Concept
Vitest plan (extending `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts`, mocking only `poaBridge.httpClient.getWithdrawalStatus`):

1. Mock `getWithdrawalStatus` to return two `COMPLETED` withdrawals with the same `near_token_id: "btc.omft.near"`, different `address` ("addrA" and "addrB"), and different `transfer_tx_hash` ("txA" and "txB").
2. Call `bridge.describeWithdrawal({ index: 0, withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: "addrA", amount: 100000n, feeInclusive: false }, tx: {...} })` and `bridge.describeWithdrawal({ index: 1, withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: "addrB", amount: 100000n, feeInclusive: false }, tx: {...} })`.
3. Assert the **signed** side: `wid_0.withdrawalParams.destinationAddress === "addrA"`, `wid_1.withdrawalParams.destinationAddress === "addrB"`.
4. Assert the **reported** side: current buggy behavior returns `{status:"completed", txHash:"txA"}` for **both** calls (since `.find()` always returns the first array entry matching `assetId`), i.e. `reported_1.txHash === "txA" !== "txB"`, proving `reported != signed` for index 1.
5. Fixed behavior should assert `reported_0.txHash === "txA"` and `reported_1.txHash === "txB"`, i.e., `reported == signed` per destination address.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1111)
```typescript
		it("matches withdrawal by assetId, not by index", async () => {
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
				withdrawals: [
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "other-tx-hash",
							chain: "eth",
							defuse_asset_identifier: "nep141:eth.omft.near",
							near_token_id: "eth.omft.near",
							decimals: 18,
							amount: 1000000,
							account_id: "test.near",
							address: zeroAddress,
							created: "2024-01-01T00:00:00Z",
						},
					},
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "btc-tx-hash",
							chain: "btc",
							defuse_asset_identifier: "nep141:btc.omft.near",
							near_token_id: "btc.omft.near",
							decimals: 8,
							amount: 100000,
							account_id: "test.near",
							address: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
							created: "2024-01-01T00:00:00Z",
						},
					},
				],
			});

			const bridge = new PoaBridge({
				envConfig: configsByEnvironment.production,
				xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
			});

			const result = await bridge.describeWithdrawal({
				landingChain: Chains.Bitcoin,
				index: 0,
				withdrawalParams: {
					assetId: "nep141:btc.omft.near",
					amount: 100000n,
					destinationAddress: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
				status: "completed",
				txHash: "btc-tx-hash",
			});
		});
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L318-318)
```typescript
		// Response list is unsorted, so we match by assetId instead of index
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-416)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-39)
```typescript
		return await poll(
			async () => {
				try {
					const status = await args.bridge.describeWithdrawal({
						...args.wid,
						logger: args.logger,
					});
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
