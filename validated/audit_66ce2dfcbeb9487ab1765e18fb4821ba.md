### Title
Batch withdrawals of the same assetId cause `findMatchingWithdrawal` to always return the array's first match, corrupting per-leg status/txHash reporting - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves each `WithdrawalIdentifier` to a status purely by matching `assetId` via `findMatchingWithdrawal`, completely ignoring `WithdrawalIdentifier.index`. When a single intent contains multiple POA withdrawals of the same `assetId`, every `describeWithdrawal` call for that batch (regardless of `index: 0,1,2`) returns the same `Array.prototype.find` result — the first entry in the API's withdrawal list matching that `assetId`.

### Finding Description
The broken equality: `(status, txHash)` reported for withdrawal `i` must equal `(status, txHash)` of the actual on-chain payout for withdrawal `i`, for `i = 0,1,2` individually.

Code path: [1](#0-0) 
`describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which matches only on `assetId`: [2](#0-1) 
The `index` field on `WithdrawalIdentifier` (set in `createWithdrawalIdentifier`, incremented per-route in `createWithdrawalIdentifiers`) is never read here: [3](#0-2) [4](#0-3) 

The root cause is explicitly documented in the source itself: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." This is not a hypothetical edge case — an unprivileged user (or a counterparty whose `withdrawalParams` array is forwarded by an integrator) can simply request three withdrawals with the same `assetId` and three distinct `destinationAddress` values in one batch (`sdk.processWithdrawal`/`sdk.waitForWithdrawalCompletion` with `withdrawalParams: WithdrawalParams[]`). `sdk.ts`'s `createWithdrawalCompletionPromises` and `withdrawal-watcher.ts`'s `createWithdrawalIdentifiers` build one `WithdrawalIdentifier` per leg with `index 0,1,2`, but nothing anywhere in the stack validates or rejects duplicate `assetId` entries in a batch, and no downstream code disambiguates by index, amount, or destination for POA bridge status lookups.

None of the referenced guards (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()`, `FeeExceedsAmountError`, `getUnderlyingFee`, contract-level nonce/signature checks) touch this code path at all — they operate on withdrawal creation/fee estimation, not on post-settlement status polling, and none of them reject or reorder duplicate-`assetId` batches.

Exploit flow: attacker submits an intent with 3 POA withdrawals of `nep141:eth.omft.near` to addresses A, B, C. Integrator calls `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` per leg. Each of the 3 `watchWithdrawal` calls polls `describeWithdrawal` with `index` 0, 1, 2 respectively but identical `assetId`; `findMatchingWithdrawal` returns the same (first-matching) API entry for all three regardless of `index`, so all three promises resolve with the same `{status:'completed', txHash}` even though A, B, and C received distinct on-chain payouts (or worse, only one of the three has completed while the other two are still pending/failed, yet all three legs are reported as completed with that one txHash).

### Impact Explanation
An integrator that credits/refunds users based on `describeWithdrawal`'s per-leg `{status, txHash}` will (a) credit or reconcile the same reported `txHash` for three distinct payouts, effectively triple-crediting or misattributing funds across destinations, and/or (b) mark two legs "completed" while their actual payouts are still pending or failed, masking undelivered funds as delivered. This is a status/hash misreport causing an integrator to credit/refund based on incorrect completion state for multiple legs simultaneously — matching the High/Critical "status or hash misreport making an integrator credit or refund twice" impact category, and is repeatable on every batch withdrawal that reuses the same `assetId`.

### Likelihood Explanation
Preconditions: the caller must submit a batch of ≥2 POA withdrawals sharing the same `assetId` within one intent (routed by `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` with `WithdrawalParams[]`). Nothing in `supports()`, `validateWithdrawal()`, or the batch-building code (`sdk.ts`, `withdrawal-watcher.ts`) prevents or even warns about duplicate `assetId` entries in the same batch. This requires no special privilege beyond normal SDK usage and is trivially and deterministically reproducible — attacker cost is a single intent submission with three near-identical withdrawal legs.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId` alone: match remaining unmatched withdrawals by combining `assetId` with `destinationAddress` (and `destinationMemo`) and/or amount, consuming each API withdrawal entry at most once (e.g., track already-consumed entries per `describeWithdrawal` call chain, or accept the full list of sibling `WithdrawalIdentifier`s and resolve all same-assetId legs together by sorting on amount/destination as the code's own comment suggests). At minimum, until per-leg disambiguation is implemented, `PoaBridge.supports`/`validateWithdrawal`/the SDK's batch entry point should detect and reject batches containing duplicate `assetId` withdrawals routed to `PoaBridge`, to prevent silent misreporting.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.status-truth.test.ts
import { describe, it, expect, vi } from "vitest";
import { poaBridge } from "@defuse-protocol/internal-utils";
import { PoaBridge } from "./poa-bridge";

describe("STATUS_TRUTH violation: duplicate assetId batch", () => {
  it("returns identical {status, txHash} for 3 distinct on-chain payouts", async () => {
    vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
      withdrawals: [
        { status: "COMPLETED", data: { near_token_id: "eth.omft.near", transfer_tx_hash: "0xAAA" /* to destA */ } },
        { status: "COMPLETED", data: { near_token_id: "eth.omft.near", transfer_tx_hash: "0xBBB" /* to destB */ } },
        { status: "PENDING",   data: { near_token_id: "eth.omft.near", transfer_tx_hash: null   /* to destC, not done */ } },
      ],
    });

    const bridge = new PoaBridge({ envConfig: /* ... */, xrplRpcUrls: [] });
    const withdrawalParams = { assetId: "nep141:eth.omft.near", /* ... */ };
    const tx = { hash: "intent-tx-hash", accountId: "user.near" };

    const results = await Promise.all(
      [0, 1, 2].map((index) =>
        bridge.describeWithdrawal({
          landingChain: /* ... */,
          index,
          withdrawalParams,
          tx,
        }),
      ),
    );

    // Broken equality: all three report the SAME status/txHash ("0xAAA"),
    // even though leg 1 actually paid "0xBBB" and leg 2 is still PENDING.
    expect(results[0]).toEqual({ status: "completed", txHash: "0xAAA" });
    expect(results[1]).toEqual({ status: "completed", txHash: "0xAAA" }); // WRONG: should be "0xBBB"
    expect(results[2]).toEqual({ status: "completed", txHash: "0xAAA" }); // WRONG: should be "pending"
  });
});
```

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
