### Title
Duplicate-assetId batch withdrawal causes `describeWithdrawal` to report the wrong txHash for later indices - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`findMatchingWithdrawal` matches POA bridge API results purely by `assetId` using `Array.prototype.find`, which always returns the first array element matching the criterion, regardless of which `WithdrawalIdentifier.index` requested it. When a batch withdrawal contains two or more entries with the same `assetId` (e.g. same token withdrawn to two different destination addresses/amounts in one intent), `describeWithdrawal` called for index 1 will report the same record (typically withdrawal[0]'s `transfer_tx_hash`) as index 0, breaking the invariant that the reported `(status, txHash)` for withdrawal *i* corresponds to withdrawal *i*'s actual outcome.

### Finding Description
The broken equality: `describeWithdrawal({index: 1, withdrawalParams: params[1]}).txHash == outcome.txHash for withdrawal 1`. In practice, for same-assetId batches, this becomes `describeWithdrawal(index:1).txHash == describeWithdrawal(index:0).txHash` (both report the first matching record from the API response array), which is only correct by coincidence.

Code path:
- `PoaBridge.describeWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343) calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`.
- `findMatchingWithdrawal` (packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427) does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)`, ignoring `args.index` entirely.
- The function's own doc comment (lines 409-416) explicitly acknowledges: *"Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."*

Nothing in the reachable code path prevents an ordinary user from constructing a batch withdrawal intent containing two entries with the same `assetId` but different `destinationAddress`/`amount`. `PoaBridge.validateWithdrawal` (poa-bridge.ts:170-259) validates each withdrawal entry independently (asset support, destination address, min amount) and does not check for duplicate assetIds across the batch. `createWithdrawalIdentifiers` in `withdrawal-watcher.ts:80-107` assigns a per-route `index` counter but this index is never used by `findMatchingWithdrawal` to disambiguate. `supports()`, `compareAddresses`, and `FeeExceedsAmountError`-style guards address unrelated concerns (asset routing, self-transfer, fee bounds) and do nothing to prevent or detect duplicate-assetId collisions in status reporting.

Attacker/user input: a `withdrawalParams` array such as `[{assetId: "nep141:usdc.omft.near", amount: 100, destinationAddress: A}, {assetId: "nep141:usdc.omft.near", amount: 50, destinationAddress: B}]` submitted in one NEAR Intents transaction. When the integrator later polls per-index status via `watchWithdrawal`/`createWithdrawalCompletionPromises`, index 1's `describeWithdrawal` call will return withdrawal[0]'s `transfer_tx_hash` (whichever the POA API lists first, since "Response list is unsorted").

### Impact Explanation
An integrator that tracks withdrawals by index (as the SDK's own array-of-promises API and RFC design explicitly encourage, see `docs/design/rfc-batch-withdrawal-granular-control.md`) will attribute the wrong destination-chain txHash to index 1. This can cause the integrator to mark/credit withdrawal 1 as completed with a txHash that actually paid out to destination A (index 0) for a different amount, while withdrawal 1's own real completion (to destination B) may separately be discovered later, leading to double crediting/refunding for a single txHash. This is a status/hash misreport affecting the party who owns/operates the SDK-side integrator, and it recurs on every poll of the affected withdrawal until the underlying POA record for index 1 happens to appear first in the (unsorted) list — i.e., partially self-correcting, but still repeatable and dangerous mid-flight. This matches the "High" impact category (a status/hash misreport making an integrator credit or refund twice) rather than moving funds outright; the underlying token transfers by the bridge are still correctly executed to the correct addresses, only the SDK's reporting layer misattributes which withdrawal that transfer belongs to.

### Likelihood Explanation
Preconditions: the batch must include ≥2 withdrawal entries with identical `assetId` in the same POA-bridge-routed intent, which is an ordinary, permitted usage pattern (nothing rejects it in `validateWithdrawal`, `supports`, or `createWithdrawalIdentifiers`). The attacker only needs to be a normal user (or an integrator itself, not "misusing an escape hatch" — this is a documented and reachable design gap) constructing such a batch withdrawal with their own funds. No solver, relayer, or bridge cooperation required. This is straightforward to trigger and the misreport is deterministic based on the order returned by the (explicitly documented as unsorted) POA API.

### Recommendation
Either (a) reject/validate that a single POA-bridge-routed batch does not contain duplicate `assetId`s (fail fast in `validateWithdrawal` or at batch-construction time), or (b) implement the disambiguation strategy already suggested in the code comment: sort both the API response withdrawals and the local `withdrawalParams` by amount (since fees are equal for same-token entries, relative ordering is preserved) and match by position, or (c) if the POA API is later extended to expose a stable per-request/per-index correlation id, use that instead of `assetId` for matching.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (illustrative addition)
it("misattributes txHash between two same-assetId withdrawals in a batch", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "dest-tx-hash-FOR-WITHDRAWAL-0",
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8,
          amount: 100000,
          account_id: "test.near",
          address: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j", // destination A
          created: "2024-01-01T00:00:00Z",
        },
      },
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "dest-tx-hash-FOR-WITHDRAWAL-1",
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8,
          amount: 50000,
          account_id: "test.near",
          address: "1AnotherDestinationAddressB", // destination B
          created: "2024-01-01T00:00:00Z",
        },
      },
    ],
  });

  const bridge = new PoaBridge({
    envConfig: configsByEnvironment.production,
    xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
  });

  const paramsIndex1 = {
    assetId: "nep141:btc.omft.near",
    amount: 50000n,
    destinationAddress: "1AnotherDestinationAddressB",
    feeInclusive: false,
  };

  const result = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin,
    index: 1,
    withdrawalParams: paramsIndex1,
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  // EQUALITY UNDER TEST: reported txHash for index 1 should correspond to
  // withdrawal[1] (destination B), NOT withdrawal[0] (destination A).
  expect(result).toEqual({ status: "completed", txHash: "dest-tx-hash-FOR-WITHDRAWAL-1" });
  // This assertion FAILS with the current implementation: it actually returns
  // "dest-tx-hash-FOR-WITHDRAWAL-0" because `findMatchingWithdrawal` uses
  // `Array.prototype.find` and ignores `index`, always returning the first
  // element whose assetId matches, i.e. withdrawal[0]'s data for both index 0 and index 1.
});
``` [1](#0-0) [2](#0-1) [3](#0-2)

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
