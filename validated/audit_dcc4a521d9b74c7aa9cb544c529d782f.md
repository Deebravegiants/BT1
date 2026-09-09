### Title
Omni Bridge `describeWithdrawal()` matches transfer status/hash by raw array index instead of by withdrawal identity, causing status/hash misreport for multi-withdrawal transactions - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal()` selects which on-chain transfer to report by indexing directly into the array returned by `omniBridgeAPI.getTransfer({ transactionHash })` with `args.index`, the position of the withdrawal in the caller's original request list. Nothing ties that index to the specific token/destination/amount of the withdrawal being queried. The PoA Bridge implementation in the same codebase explicitly avoids this exact pattern because the API's list is "unsorted," and instead matches by `assetId`/`near_token_id`.

### Finding Description
`OmniBridge.describeWithdrawal()`: [1](#0-0) 
selects `transfer = (await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash }))[args.index]` and reports that transfer's `status`/`txHash` as the outcome for the withdrawal identified by `args.wid` (built from `withdrawalParams`, `index`, `tx`). There is no check that `transfer.recipient`, token, or amount actually correspond to `args.withdrawalParams` (destinationAddress/assetId/amount) — the index alone determines which transfer's data is trusted.

Contrast with `PoaBridge.describeWithdrawal()`, which explicitly matches by asset identity rather than index, with an in-code comment stating why: [2](#0-1) [3](#0-2) 
and the CHANGELOG confirms this was a deliberate fix for a prior index-based matching bug: [4](#0-3) 

The Omni Bridge implementation still relies purely on the raw index returned by `getTransfer`, with no ordering guarantee documented or enforced anywhere in the reviewed code. `createWithdrawalIdentifierIdentifier()` / `createWithdrawalIdentifiers()` in `withdrawal-watcher.ts` assign monotonically increasing per-route indices purely based on the order `withdrawalParams` were supplied by the caller/SDK: [5](#0-4) 
If the on-chain/indexer transfer array for a NEAR transaction containing multiple Omni Bridge withdrawal intents is not guaranteed to preserve that same order (as the PoA API explicitly is not, per the codebase's own comment), then `describeWithdrawal({index: N})` can return the status and `txHash` belonging to a *different* withdrawal in the same transaction (different token, amount, destination).

### Impact Explanation
Reported `status`/`txHash` is consumed by `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` to determine that a specific withdrawal (a specific token/amount/destination) has completed. If withdrawal #0 (e.g. small USDC transfer) is falsely reported completed using the `txHash` that actually belongs to withdrawal #1 (e.g. a different token/destination), an integrator relying on this SDK could:
- Credit/refund a user for a withdrawal that hasn't actually landed at their address (status misreport), or
- Attribute the wrong destination transaction hash to a withdrawal, breaking any on-chain verification/matching an integrator performs downstream.

This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category, since it could cause a double credit (once from wrongly-reported completion, once from separate reconciliation) or missed real fraud detection tied to txHash association.

### Likelihood Explanation
This only manifests when a single NEAR transaction bundles multiple Omni Bridge withdrawal intents (batch withdrawal) and the indexer/API's transfer list ordering doesn't match the caller-assigned index — a scenario the codebase's own comment (for the sibling PoA bridge) states is a real, encountered condition ("Response list is unsorted"). It requires no malicious actor — any legitimate batched multi-withdrawal request through Omni Bridge is at risk if the indexer reorders transfers, which is an unprivileged trigger (an ordinary user/integrator submitting >1 withdrawal in the same intent). I could not directly confirm from available files whether `omniBridgeAPI.getTransfer` (from `@omni-bridge/core`, a third-party dependency) guarantees index-stable ordering; this reduces certainty of exploitability but the code contains no defensive matching despite the pattern being explicitly called out as broken for the analogous PoA bridge.

### Recommendation
Match transfers returned by `getTransfer()` to the specific withdrawal by identity (destination address, token/asset, and amount) rather than trusting raw array position, mirroring the `findMatchingWithdrawal()` approach used in `poa-bridge.ts`. If multiple withdrawals share the same destination/asset/amount (ambiguous), disambiguate using additional fields returned by the transfer object (e.g. `transfer_id`, `sender`, `msg`) or explicitly document and verify an ordering guarantee from the Omni Bridge indexer before relying on index-based lookups.

### Proof of Concept
1. Sign and publish a single NEAR intent transaction containing two Omni Bridge withdrawal intents: withdrawal A (token X → address A, index 0) and withdrawal B (token Y → address B, index 1).
2. The Omni Bridge indexer processes/returns the two resulting transfers via `getTransfer({transactionHash})` in an order that does not match submission order (analogous to the documented "unsorted" behavior on the PoA bridge API).
3. `describeWithdrawal({index: 0, withdrawalParams: A, tx})` returns `transfer[0]`, which is actually transfer B's data (different token/destination/amount), reporting `{status: "completed", txHash: <B's tx hash>}` for withdrawal A.
4. An integrator watching withdrawal A via `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` sees it "completed" with an unrelated `txHash`, and credits/reconciles the user for withdrawal A based on a transaction that never delivered those funds to address A.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-702)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];

		if (transfer == null || transfer.recipient == null) {
			return { status: "pending" };
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

**File:** packages/intents-sdk/CHANGELOG.md (L592-599)
```markdown
## 0.43.2

### Patch Changes

- 8bbd5c6: Fix POA bridge withdrawal matching to use assetId instead of index.
- c7738e3: Add `min_gas` to withdrawals, so bridges do not fail with out of gas.
- Updated dependencies [8bbd5c6]
  - @defuse-protocol/internal-utils@0.21.1
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
