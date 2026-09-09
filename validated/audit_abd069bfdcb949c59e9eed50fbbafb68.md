This confirms the vulnerability described. The code and its own comments explicitly acknowledge this exact limitation.

### Title
Same-asset multi-withdrawal identity collapse causes `watchWithdrawal` to misreport second withdrawal's outcome as the first's - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`createWithdrawalIdentifiers` assigns a route-scoped `index` (0, 1, ...) to each withdrawal that resolves to `PoaBridge`, but `PoaBridge.describeWithdrawal` ignores `index` entirely and matches purely by `assetId` via `findMatchingWithdrawal`. When two withdrawal params in the same intent both use the PoA bridge and share the same `assetId` (differing only by `destinationAddress`/amount), both `WithdrawalIdentifier`s (index 0 and index 1) resolve to the same matched record from the PoA API, so `watchWithdrawal` on the second withdrawal reports the completion status/txHash of whichever matching record `Array.find` returns first — not the actual second withdrawal.

### Finding Description
The broken equality: `watchWithdrawal({wid: wid_i})` should return the outcome of the i-th withdrawal for a given route, but for `PoaBridge`, `describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`) discards `args.index` and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` [1](#0-0) , which does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` [2](#0-1)  — returning the first array match regardless of which `index` was requested. The code's own comment states: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [3](#0-2) .

Meanwhile, `createWithdrawalIdentifiers` in `withdrawal-watcher.ts` increments a per-`bridge.route` counter and stamps each `WithdrawalIdentifier` with that index without any check that the underlying bridge can actually disambiguate by index for same-asset entries: [4](#0-3) . Nothing in `supports()`, `findBridgeForWithdrawal`, or `createWithdrawalIdentifier` validates uniqueness of `assetId` among same-route entries before minting distinct indices — so the SDK produces two structurally distinct `WithdrawalIdentifier`s (`index: 0` and `index: 1`) that are behaviorally indistinguishable to `PoaBridge.describeWithdrawal`.

Attacker's exact input: an integrator (forwarding counterparty-controlled `withdrawalParams`) submits an intent with two withdrawal legs, both `assetId: "nep141:btc.omft.near"` (or any same PoA-supported asset), differing only by `destinationAddress` (e.g., two different BTC addresses) and/or amount. Both resolve via `supports()` to the same `PoaBridge` instance/route.

Exploit flow: `createWithdrawalIdentifiers` returns `[{bridge, wid: {index:0, assetId:X, destA}}, {bridge, wid: {index:1, assetId:X, destB}}]`. When the first withdrawal to address A completes, the PoA API returns one `COMPLETED` record for asset X. Calling `watchWithdrawal(wid1)` (index 1, destined for B) invokes `describeWithdrawal`, which finds the same single record (matched only by `near_token_id`/assetId) and reports it as completed with A's `transfer_tx_hash`, even though B's withdrawal may still be pending or use a different tx entirely.

Existing guards do not prevent this: `supports()` only checks asset/chain compatibility, not per-route uniqueness; `findMatchingWithdrawal` explicitly does not use `index`; there is no `assert` anywhere enforcing that two same-route `withdrawalParams` in one call have distinct assetIds.

### Impact Explanation
An integrator using `createWithdrawalCompletionPromises()[1]` (or manually calling `watchWithdrawal` on the second identifier) as the ground truth for withdrawal #2's completion instead observes withdrawal #1's `txHash`/completed status. This is a status/hash misreport that can cause the integrator to credit or refund the wrong withdrawal as complete — matching the High severity category ("a status or hash misreport making an integrator credit or refund twice"). This is repeatable any time a batch withdrawal contains ≥2 same-asset PoA legs.

### Likelihood Explanation
Preconditions: the integrator/attacker must construct an intent with at least two withdrawal legs that both route to `PoaBridge` and share the same `assetId` — a state fully reachable by an ordinary user constructing `withdrawalParams` with a repeated PoA-supported asset and different destination addresses. No special privileges, malicious relayer, or bridge API misbehavior needed; the PoA API's real matching behavior (documented in the code's own comments and covered by the "matches withdrawal by assetId, not by index" test) is exactly what's exploited. Attacker cost is minimal — just submitting a batch withdrawal intent.

### Recommendation
In `createWithdrawalIdentifiers` (or `PoaBridge.supports`/`createWithdrawalIdentifier`), detect when two or more withdrawal params routed to the same bridge share an `assetId` that the bridge cannot disambiguate by index (specifically for `PoaBridge`), and either reject/throw (e.g., a new `AmbiguousWithdrawalError`) or require `PoaBridge.describeWithdrawal` to consume PoA API results in a stable order matched against a stably-sorted list of expected withdrawals (as the code comment suggests: sort both API results and withdrawal params by amount) so `index` maps deterministically to a specific record.

### Proof of Concept
```ts
// packages/intents-sdk/src/core/withdrawal-watcher.poc.test.ts
import { describe, it, expect, vi } from "vitest";
import { createWithdrawalIdentifiers, watchWithdrawal } from "./withdrawal-watcher";
import { PoaBridge } from "../bridges/poa-bridge/poa-bridge";
// ... imports for configsByEnvironment, configureXrplRpcUrls, PUBLIC_XRPL_RPC_URLS

it("index does not disambiguate same-asset PoA withdrawals", async () => {
  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}) });

  const { results } = { results: await createWithdrawalIdentifiers({
    bridges: [bridge],
    withdrawalParams: [
      { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addrA", feeInclusive: false },
      { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addrB", feeInclusive: false },
    ],
    intentTx: { hash: "tx", accountId: "test.near" },
  }) };

  expect(results[0].wid.index).toBe(0);
  expect(results[1].wid.index).toBe(1); // distinct indices assigned

  // Mock the PoA API returning only ONE matching completed withdrawal (addrA's)
  vi.mocked(bridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [{
      status: "COMPLETED",
      data: { tx_hash: "tx", transfer_tx_hash: "addrA-tx-hash", chain: "btc",
        defuse_asset_identifier: "nep141:btc.omft.near", near_token_id: "btc.omft.near",
        decimals: 8, amount: 100000, account_id: "test.near", address: "addrA", created: "2024-01-01T00:00:00Z" },
    }],
  });

  const status0 = await watchWithdrawal({ bridge, wid: results[0].wid });
  const status1 = await watchWithdrawal({ bridge, wid: results[1].wid }); // supposed to be addrB's withdrawal

  // BROKEN EQUALITY: wid1 (destined for addrB) resolves to wid0's (addrA) outcome
  expect(status0).toEqual({ hash: "addrA-tx-hash" });
  expect(status1).toEqual({ hash: "addrA-tx-hash" }); // should differ / reflect addrB, but doesn't
});
``` [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L405-427)
```typescript
type WithdrawalStatusResponse = Awaited<
	ReturnType<typeof poaBridge.httpClient.getWithdrawalStatus>
>;

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
