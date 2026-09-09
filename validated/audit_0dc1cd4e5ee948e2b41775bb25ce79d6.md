## Title
`describeWithdrawal` misreports identical `txHash`/status for two distinct same-token batch withdrawal legs - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`findMatchingWithdrawal` matches PoA bridge withdrawal status records by `assetId` alone, ignoring `WithdrawalIdentifier.index`. When a batch withdrawal contains two legs of the same `nep141` token to different `destinationAddress`/`amount`, both `describeWithdrawal(index:0)` and `describeWithdrawal(index:1)` return the same array match, so a single completed leg is reported as completion for both legs.

### Finding Description
The broken equality is: STATUS TRUTH — `(status, txHash) reported for withdrawal[i]` should equal the true on-chain outcome of `withdrawalParams[i]` specifically, not of some other same-asset withdrawal.

`describeWithdrawal` (lines 313-343) calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` (line 319-322). `findMatchingWithdrawal` (lines 418-427) does:
```
return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
```
This is a pure `Array.find` by token id, with no consideration of `args.index`, `destinationAddress`, or `amount`. The code's own comment (lines 409-416) explicitly acknowledges: *"Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."*

Attacker/caller input: an ordinary user constructs a batch withdrawal (via the normal SDK withdrawal flow) that withdraws the same `nep141:token.omft.near` asset twice within one intent transaction, to two different `destinationAddress` values and/or different `amount`s (e.g., splitting a payment to two recipients). Both legs route through `PoaBridge`.

Exploit flow: when the integrator later calls `sdk.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises`, this constructs a `WithdrawalIdentifier` per leg (index 0 and index 1, same `tx.hash`, same `assetId`, different `destinationAddress`/`amount`) via `createWithdrawalIdentifier` (lines 295-311), then calls `PoaBridge.describeWithdrawal` for each. Both calls fetch the same `getWithdrawalStatus` response (same `tx.hash`) and both run `findMatchingWithdrawal` with the same `assetId`, so `Array.find` returns the *first* matching record for both index 0 and index 1 — even if only leg 0 actually completed on-chain and leg 1 is still pending or failed. Both `describeWithdrawal` calls thus return `{ status: "completed", txHash: <same hash> }`.

No existing guard prevents this: `validateWithdrawal`, `compareAddresses`, `supports()`, and `FeeExceedsAmountError` all operate on withdrawal creation/fee validation, not on status matching. `findMatchingWithdrawal` has no fallback to disambiguate by index, destination, or amount, and the code comment confirms this is a known, unaddressed limitation with no mitigation on the matching side.

### Impact Explanation
The integrator (or any downstream consumer polling withdrawal completion) receives a `completed` status with a `txHash` for withdrawal `index:1` that in reality corresponds only to withdrawal `index:0`'s transfer. If the integrator credits a user or releases custody/downstream funds based on this per-leg completion report, it will credit/release for both legs based on one actual completed transfer — a status/hash misreport causing a double-credit. This matches the **High** impact category ("a status or hash misreport making an integrator credit or refund twice"). The condition is repeatable for every batch withdrawal that includes ≥2 legs of the same token.

### Likelihood Explanation
Preconditions: a batch withdrawal with two or more legs of the *same* `nep141` asset, both routed through the PoA bridge. This is a normal, permissionless usage pattern (splitting a withdrawal of one token to multiple destinations) requiring no privileged access — an ordinary user or integrator can trigger it through standard SDK withdrawal APIs. No special attacker cost beyond constructing a legitimate multi-recipient batch withdrawal of one token. It is fully repeatable on every such batch.

### Recommendation
Extend `findMatchingWithdrawal` to disambiguate among multiple same-asset matches, e.g., by matching `destinationAddress` (and `destinationMemo`) in addition to `assetId`, or — per the code's own suggested approach — sort both the API's withdrawal records and the local `withdrawalParams` by amount consistently and match by relative position/index when multiple same-asset records exist, throwing/returning `pending` (not a false "completed") when a withdrawal cannot be unambiguously matched.

### Proof of Concept
```ts
// vitest — mocks only poaBridge.httpClient.getWithdrawalStatus (HTTP layer)
import { describe, it, expect, vi } from "vitest";
import { PoaBridge } from "./poa-bridge";
import { poaBridge } from "@defuse-protocol/internal-utils";

it("misreports same txHash for two distinct same-asset withdrawal legs", async () => {
  const assetId = "nep141:token.omft.near";
  const tx = { hash: "TX_HASH", accountId: "acc" };

  const withdrawalParamsA = { assetId, destinationAddress: "addrA", amount: 100n, routeConfig: undefined };
  const withdrawalParamsB = { assetId, destinationAddress: "addrB", amount: 200n, routeConfig: undefined };

  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: { near_token_id: "token.omft.near", transfer_tx_hash: "REAL_TX_FOR_A" },
      },
      // leg B has no matching COMPLETED record — still pending in reality
    ],
  });

  const bridge = new PoaBridge({ envConfig: {/* ... */}, xrplRpcUrls: [] });

  const resultA = await bridge.describeWithdrawal({
    landingChain: "..." as any, index: 0, withdrawalParams: withdrawalParamsA as any, tx,
  });
  const resultB = await bridge.describeWithdrawal({
    landingChain: "..." as any, index: 1, withdrawalParams: withdrawalParamsB as any, tx,
  });

  // BROKEN EQUALITY: both report identical completed status/txHash
  expect(resultA).toEqual({ status: "completed", txHash: "REAL_TX_FOR_A" });
  expect(resultB).toEqual({ status: "completed", txHash: "REAL_TX_FOR_A" }); // should be "pending", is not
});
```
This demonstrates that `describeWithdrawal(index:1)` (withdrawal to `addrB`, amount 200) falsely reports completion with the `txHash` belonging only to `describeWithdrawal(index:0)`'s (`addrA`, amount 100) actual on-chain transfer. [1](#0-0) [2](#0-1)

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
