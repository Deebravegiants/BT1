### Title
POA Bridge `describeWithdrawal` misattributes withdrawal status/hash by matching only on `assetId`, not on the caller's `index` - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` is supposed to report the on-chain status of one specific withdrawal identified by a `WithdrawalIdentifier` (`landingChain`, `index`, `withdrawalParams`, `tx`). Instead it discards the `index` and matches purely on `assetId`, so when a single NEAR transaction contains more than one withdrawal of the same token (e.g. batched withdrawals to two different destination addresses), the status/txHash returned for withdrawal #0 can actually belong to withdrawal #1 (or vice versa).

### Finding Description
`createWithdrawalIdentifier` builds an identifier that carries `index` and the specific `withdrawalParams` for that leg of a batched NEAR transaction: [1](#0-0) 

`describeWithdrawal` then fetches all withdrawals for the transaction hash and calls `findMatchingWithdrawal`, which ignores `args.index` entirely and instead searches the *whole* returned list for the first entry whose `near_token_id` matches `args.withdrawalParams.assetId`: [2](#0-1) [3](#0-2) 

The code comment itself confirms the root cause: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." Because the POA API response list is unordered and `Array.prototype.find` returns the first assetId match, if a user submits two withdrawals of the same `assetId` (same token, different `destinationAddress`/`amount`) in one NEAR transaction, `describeWithdrawal(index=0, ...)` and `describeWithdrawal(index=1, ...)` can both resolve to the *same* underlying withdrawal record (or resolve to each other's record), producing a `txHash`/`status` for withdrawal A that is actually the on-chain outcome of withdrawal B.

This breaks the exact equality the rules target: "a status reported that is not the on-chain outcome" — the `txHash`/`status` returned by the SDK for a given withdrawal identifier does not correspond to that withdrawal's actual on-chain result.

### Impact Explanation
An integrator that polls `describeWithdrawal` per withdrawal index to decide when to mark a withdrawal "completed" (and stop retrying / release UI state / reconcile ledgers) can be told withdrawal A is `completed` with a `txHash` that is really withdrawal B's transaction, while withdrawal A itself may still be pending or failed. This matches the listed High-impact category: "a status or hash misreport making an integrator credit or refund twice" — the integrator could credit/settle the wrong leg of a batched withdrawal as complete, or apply the wrong destination's transaction hash for reconciliation, while the other leg's true status remains unknown or is silently skipped.

### Likelihood Explanation
This requires no privileged action, no relayer/bridge misbehavior, and no admin cooperation — it is triggered purely by ordinary use of the documented `index`-based `WithdrawalIdentifier` API when a caller (via the SDK's batching capability) withdraws the same POA-bridged asset more than once in a single NEAR transaction (e.g., same token to two different recipients, or two separate withdrawal calls in one batched tx). The condition is plausible for integrators doing batch payouts of the same token to multiple recipients.

### Recommendation
Match withdrawals by `index` position after deterministically ordering both the withdrawal params supplied to the SDK and the withdrawals returned by the POA API (e.g., sort both lists by `amount` as the code comment itself suggests, since fees are identical per token/chain and relative amount ordering is preserved), instead of matching solely on `assetId`. Until such a fix lands, the SDK should either reject/guard batched withdrawals of the same `assetId` in one transaction for the POA route, or clearly surface an "ambiguous match" error rather than silently returning a possibly-incorrect status/txHash.

### Proof of Concept
1. Build a NEAR transaction with two POA-bridge withdrawal intents for the same `assetId` (`nep141:btc.omft.near`), one to `destinationAddress` X (index 0) and one to `destinationAddress` Y (index 1).
2. Call `sdk.describeWithdrawal({ ..., index: 0, tx })` and `sdk.describeWithdrawal({ ..., index: 1, tx })`.
3. Both calls invoke `getWithdrawalStatusWithRetry` → `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns the same first-matching array element for both calls regardless of `index`, per [4](#0-3)  and [5](#0-4) .
4. Result: both indices report identical `status`/`txHash`, even though on-chain one withdrawal may have completed to X while the other (to Y) is still pending or failed — an integrator relying on per-index status will misreport the outcome of at least one leg.

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
