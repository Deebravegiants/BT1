### Title
`findMatchingWildrawal` matches by `assetId` only, causing txHash/status misattribution for same-asset batch withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the withdrawal's status/`txHash` for `WithdrawalIdentifier` index *i* by calling `findMatchingWithdrawal`, which selects the first entry in the (unsorted) PoA `withdrawals` array whose `nep141:${w.data.near_token_id}` equals `assetId`, ignoring `amount`, `address`, and `account_id`. When a batch `processWithdrawal`/`createWithdrawalCompletionPromises` call contains two `WithdrawalParams` with the same `assetId` but different `destinationAddress`, both indices query the same PoA status response (same `args.tx.hash`, the shared intent tx) and both resolve to the same matched entry, so at least one index's reported `status`/`txHash` does not correspond to its own withdrawal.

### Finding Description
The claimed equality is: for `WithdrawalIdentifier` at index *i*, `describeWithdrawal(i).txHash` must correspond to the on-chain completion of withdrawal *i*'s own `(assetId, destinationAddress, amount)`.

Code path:
- `describeWithdrawal` (poa-bridge.ts:313-343) calls `getWithdrawalStatusWithRetry` with `{ withdrawal_hash: args.tx.hash }` (poa-bridge.ts:352-353). In a batch, all withdrawals share the same signed intent, hence the same `intentTx`/`args.tx.hash` [1](#0-0) , so calling `describeWithdrawal` for index *i* and index *j* of the same batch hits the identical PoA status endpoint and receives the identical (documented as unsorted) `withdrawals` array.
- `findMatchingWithdrawal` (poa-bridge.ts:418-427) then does `withdrawals.find((w) => \`nep141:${w.data.near_token_id}\` === assetId)`, using only `assetId` — never `w.data.address`, `w.data.amount`, or `w.data.account_id` — to disambiguate.
- The function's own doc comment admits this: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." (poa-bridge.ts:409-417).

Root cause: with two same-`assetId` withdrawals to different `destinationAddress`es in one `WithdrawalParams[]` batch, `.find()` returns the same array element for both `describeWithdrawal(i)` and `describeWithdrawal(j)` calls, so one of the two indices reports a `status`/`transfer_tx_hash` that actually belongs to the other withdrawal's real destination/completion.

No existing guard prevents this: `supports()`, `validateWithdrawal`, and `createWithdrawalIdentifier` (poa-bridge.ts:295-311) never check for duplicate `assetId` within a batch; nothing in `sdk.ts`'s `processWithdrawal`/`createWithdrawalCompletionPromises` deduplicates or reorders by destination; and the intents contract's own signature/nonce checks are irrelevant to this off-chain status-matching bug.

### Impact Explanation
`describeWithdrawal`'s `txHash`/`status` for withdrawal *i* is what `watchWithdrawal`/`createWithdrawalCompletionPromises` surfaces to the integrator as completion proof for that specific withdrawal (`sdk.ts:557-609`). If an integrator credits or releases funds based on this reported per-index completion, a same-asset multi-destination batch can cause the integrator to treat withdrawal *i* as completed using withdrawal *j*'s `transfer_tx_hash` (or vice-versa), enabling a status/hash misreport that can lead to premature or duplicate crediting — matching the "High: a status or hash misreport making an integrator credit or refund twice" category. This is repeatable on every batch containing ≥2 withdrawals of the same `assetId`.

### Likelihood Explanation
Preconditions: caller submits a `WithdrawalParams[]` batch through `processWithdrawal`/`signAndSendWithdrawalIntent` with two or more entries sharing the same `assetId` (POA-bridge-routed token) but different `destinationAddress`. This is a completely ordinary usage pattern — nothing in `supports()`/`validateWithdrawal` rejects duplicate-asset batches — and requires no privileged access, only the ability to construct a normal multi-withdrawal request (something an ordinary user or an integrator forwarding counterparty-supplied withdrawal lists can trivially do). Feasibility is high and the bug is deterministic/repeatable for any batch matching this shape.

### Recommendation
Disambiguate `findMatchingWithdrawal` using additional fields returned by the PoA API (e.g., match on `near_token_id` + `address`/`account_id` + `amount`), or, as the code comment suggests, sort both the API's `withdrawals` and the batch's `WithdrawalParams` by amount (for same-token entries) before pairing by position, and throw/return an unresolved status when multiple candidates remain ambiguous rather than silently picking `.find()`'s first match.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (illustrative)
import { poaBridge } from "@defuse-protocol/internal-utils";
import { describe, it, expect, vi } from "vitest";
import { PoaBridge } from "./poa-bridge";

it("misattributes txHash for same-asset different-destination batch", async () => {
  const bridge = new PoaBridge({ envConfig: /* ... */, xrplRpcUrls: [] });

  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", address: "ADDR_A", transfer_tx_hash: "TX_A", amount: "100" } },
      { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", address: "ADDR_B", transfer_tx_hash: "TX_B", amount: "200" } },
    ],
  });

  const wid = (destinationAddress: string, index: number) => ({
    landingChain: "near:mainnet",
    index,
    withdrawalParams: { assetId: "nep141:usdc.omft.near", destinationAddress, amount: 0n, routeConfig: undefined },
    tx: { hash: "SAME_INTENT_TX_HASH" },
  });

  const resultForIndex0 = await bridge.describeWithdrawal({ ...wid("ADDR_A", 0) });
  const resultForIndex1 = await bridge.describeWithdrawal({ ...wid("ADDR_B", 1) });

  // Broken equality: both resolve via the SAME array entry (findMatchingWithdrawal ignores address),
  // so index 1 (destination ADDR_B) incorrectly reports TX_A (belongs to ADDR_A).
  expect(resultForIndex0).toEqual({ status: "completed", txHash: "TX_A" });
  expect(resultForIndex1).toEqual({ status: "completed", txHash: "TX_A" }); // should be TX_B, proving misattribution
});
``` [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L557-609)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
	}
```

**File:** packages/intents-sdk/src/sdk.ts (L826-838)
```typescript
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
