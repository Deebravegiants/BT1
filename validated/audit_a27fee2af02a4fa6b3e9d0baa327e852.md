### Title
Same-`assetId` batched POA withdrawals collapse to a single matched record in `findMatchingWithdrawal`, causing `describeWithdrawal` to misreport index 1 as completed with index 0's `transfer_tx_hash` - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves the POA bridge's withdrawal record purely by matching `assetId` via `findMatchingWithdrawal`, ignoring `WithdrawalIdentifier.index` entirely. When a batched intent contains two withdrawals of the same `assetId`, both indices resolve to the *same* array element, so once any one of the two on-chain payouts is marked `COMPLETED` by the bridge API, both `watchWithdrawal` calls (for index 0 and index 1) report `completed` with the identical `transfer_tx_hash`, even though only one payout actually happened.

### Finding Description
The broken equality is: `(status, txHash)` returned for withdrawal `index:i` must equal the on-chain outcome of withdrawal `i` specifically, not of some other withdrawal sharing the same `assetId`.

- `describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` [1](#0-0) , which only filters on `nep141:${w.data.near_token_id} === assetId` and returns the first array match, with no reference to `WithdrawalIdentifier.index` at all [2](#0-1) .
- The code comment directly above `findMatchingWithdrawal` explicitly documents this as a known limitation: *"multiple withdrawals of the same token in a single transaction are not supported"* [3](#0-2) .
- `createWithdrawalIdentifier` assigns `index` per-route but never encodes it into anything used to disambiguate the API response - it's just passed straight through to `describeWithdrawal` as part of `WithdrawalIdentifier` [4](#0-3) .
- `watchWithdrawal` in `withdrawal-watcher.ts` polls `bridge.describeWithdrawal({...args.wid, ...})` per withdrawal identifier and, on `status === "completed"`, resolves the promise with `{ hash: status.txHash }` [5](#0-4) . Since two independent `wid`s (index 0 and index 1, both with the same `assetId`) drive two independent polls, both will converge on the same matched record and thus the same resolved `txHash` as soon as the bridge API returns a single `COMPLETED` entry for that `assetId`.
- No other guard (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()`, `FeeExceedsAmountError`, `getUnderlyingFee`, `matchesRequest`, `assert`) touches this matching step; none of them disambiguate by index or amount for POA. The `supports()`/`validateWithdrawal` checks run pre-submission on withdrawal validity, not on status matching post-submission.

Attacker/trigger: an ordinary user (or integrator forwarding user-supplied `withdrawalParams`) constructs a batched intent with two POA withdrawals for the same `assetId` (e.g., two ZEC withdrawals to different destination addresses). This is a legitimate, unprivileged action - `createWithdrawIntentPrimitive` and `supports()` place no restriction preventing duplicate `assetId` entries in a batch. No malicious bridge/API behavior is required: the bug is fully triggered by the bridge API's genuine, timing-driven state where only one of the two withdrawals has settled to `COMPLETED` at the time of the poll.

### Impact Explanation
An integrator that keys off withdrawal index (as the RFC's own examples do, e.g. `if (index === 0) quoteEntity.destinationTx = tx.hash; if (index === 1) quoteEntity.refundTx = tx.hash;`) will record/credit `transfer_tx_hash` from the withdrawal that actually landed on-chain as belonging to the *other* withdrawal index. This causes a status/hash misreport that can make an integrator credit funds, release custody, or clear a pending obligation for a withdrawal that never had its own destination-chain payout - the classic "status/hash misreport causing double credit" pattern. Given the on-chain outcome for the still-pending/failed withdrawal never occurs, this can result in resources being released against no actual delivered funds - Critical impact per the STATUS TRUTH equality break. It's repeatable on every batched intent with duplicate `assetId` POA withdrawals, for as long as the two withdrawals' completion times diverge.

### Likelihood Explanation
Preconditions: the integrator/user must construct a batch with ≥2 POA withdrawals sharing an `assetId` (fully within an ordinary user's control, no privilege needed), and the two withdrawals' bridge-side processing must complete at different times (a routine occurrence in async bridge processing - not requiring any malicious relayer/bridge behavior, just normal timing skew). Attacker cost is negligible - just submit a normal batched withdrawal intent. It's directly reproducible without any signature forgery, replay, or contract exploit, purely through the described-above code path.

### Recommendation
Make `findMatchingWithdrawal` index-aware: track how many withdrawals of the same `assetId` have already been matched/consumed and correlate the `index`-th occurrence in `withdrawalParams` order with the `index`-th occurrence in the API response's ordering (e.g., sorted by amount, as the existing comment suggests), or refuse to disambiguate and surface an explicit unsupported/ambiguous error rather than silently returning the wrong record for duplicate-asset batches until the POA bridge API provides an unambiguous per-withdrawal correlation ID.

### Proof of Concept
```typescript
// poa-bridge.duplicate-asset.test.ts
import { describe, it, expect, vi } from "vitest";
import { PoaBridge } from "./poa-bridge";
import { poaBridge } from "@defuse-protocol/internal-utils";

describe("PoaBridge duplicate-assetId batch misreport", () => {
  it("falsely reports index 1 as completed using index 0's real payout tx", async () => {
    const sharedAssetId = "nep141:zec.omft.near";
    const tx = { hash: "batch-tx-hash", accountId: "acc" };

    // Mock: bridge API returns exactly ONE COMPLETED record for the shared near_token_id
    vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
      withdrawals: [
        {
          status: "COMPLETED",
          data: {
            near_token_id: "zec.omft.near",
            transfer_tx_hash: "REAL_PAYOUT_FOR_WITHDRAWAL_0",
          },
        },
      ],
    } as any);

    const bridge = new PoaBridge({ envConfig: /* ... */, xrplRpcUrls: [] });

    const wid0 = bridge.createWithdrawalIdentifier({
      withdrawalParams: { assetId: sharedAssetId, amount: 100n, destinationAddress: "addrA" } as any,
      index: 0,
      tx,
    });
    const wid1 = bridge.createWithdrawalIdentifier({
      withdrawalParams: { assetId: sharedAssetId, amount: 200n, destinationAddress: "addrB" } as any,
      index: 1,
      tx,
    });

    const status0 = await bridge.describeWithdrawal(wid0);
    const status1 = await bridge.describeWithdrawal(wid1);

    // LHS: on-chain outcome of withdrawal 0 == reported status0 (expected, correct)
    expect(status0).toEqual({ status: "completed", txHash: "REAL_PAYOUT_FOR_WITHDRAWAL_0" });

    // RHS: withdrawal 1's real on-chain outcome is still pending/failed,
    // but describeWithdrawal falsely reports it as completed with withdrawal 0's tx hash.
    expect(status1).toEqual({ status: "completed", txHash: "REAL_PAYOUT_FOR_WITHDRAWAL_0" });
    // BROKEN EQUALITY: status1.txHash should NOT equal status0.txHash for a distinct withdrawal 1
    // that never had its own destination-chain payout.
  });
});
```
This reproduces the exact scenario in the question: both `describeWithdrawal(wid0)` and `describeWithdrawal(wid1)` resolve to the identical `{status:'completed', txHash:'REAL_PAYOUT_FOR_WITHDRAWAL_0'}` because `findMatchingWithdrawal` ignores `index` [2](#0-1) , confirming `watchWithdrawal` for index 1 would resolve with an integrator-facing `txHash` that does not correspond to withdrawal 1's own payout [5](#0-4) .

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
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
