### Title
POA Bridge withdrawal status/hash misattribution across withdrawals of the same asset in a single transaction - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` reports the on-chain destination transaction hash and completion status for a specific withdrawal index inside a batched NEAR transaction. Instead of correlating the reported result to the specific withdrawal it was asked about, it matches purely by `assetId`, so when a single NEAR transaction contains multiple withdrawals of the same token (e.g. two different amounts/destinations of `nep141:btc.omft.near`), every one of those withdrawals is described using the same (first) match returned by the POA indexer.

### Finding Description
`describeWithdrawal` is supposed to answer "what is the on-chain outcome of withdrawal #index (with these specific `withdrawalParams`)?" The equality it should preserve is: *reported `(status, txHash)` for index i == actual on-chain outcome of the intent primitive created at index i*.

Instead, the implementation does: [1](#0-0) 

and the matcher: [2](#0-1) 

`findMatchingWithdrawal` selects the first entry in `response.withdrawals` whose `near_token_id` maps to the requested `assetId` — it ignores `args.index`, `args.withdrawalParams.amount`, and `args.withdrawalParams.destinationAddress` entirely. The code comment even acknowledges: *"multiple withdrawals of the same token in a single transaction are not supported."* But `describeWithdrawal` is called once per index for every withdrawal in the batch (see `sdk.waitForWithdrawalCompletion`, which calls the bridge once per index using `withdrawalParams[index]`): [3](#0-2) 

If a caller batches two POA withdrawals of the same asset with different destination addresses/amounts in one NEAR transaction (a directly reachable, unprivileged usage — nothing requires the relayer or bridge operator to misbehave; the "attacker" here is simply a normal SDK caller batching withdrawals as the public API allows), `Array.find` returns the same underlying withdrawal record for both `describeWithdrawal` calls. Whichever POA withdrawal completes first is reported back for both indices, with its `transfer_tx_hash`.

### Impact Explanation
This breaks the "status/hash reported == actual on-chain outcome" equality: an integrator polling `waitForWithdrawalCompletion`/`describeWithdrawal` for withdrawal index 1 can receive the transaction hash and "completed" status belonging to withdrawal index 0 (or vice versa) while its own withdrawal is still pending or routed to a different address/amount. Per the rubric this is a "status or hash misreport making an integrator credit or refund twice" — a High severity issue, since a custodial integrator (exchange, wallet backend) could mark a user's withdrawal as settled using another user's destination transaction hash, or double-credit one destination while leaving the other unaccounted for.

### Likelihood Explanation
Any caller of the public `createWithdrawalIntents`/`waitForWithdrawalCompletion` API can trivially trigger this by including two withdrawals of the same POA-bridged asset in a single batched transaction — a legitimate, unprivileged usage pattern the SDK's own types (`WithdrawalParams[]`, per-index `describeWithdrawal`) are designed to support. No malicious relayer, RPC, or admin action is required.

### Recommendation
In `findMatchingWithdrawal`, disambiguate by more than `assetId` — e.g., correlate by `destinationAddress` + `amount` (adjusted for fee) or track already-consumed indices from `response.withdrawals` so each POA record is matched to at most one requested withdrawal, only falling back to "pending" (never a wrong hash) when disambiguation is not possible.

### Proof of Concept
1. Build a withdrawal batch with two `nep141:btc.omft.near` withdrawals in the same NEAR tx: index 0 → address A amount 100000, index 1 → address B amount 50000.
2. Submit; POA indexer completes index 1 (address B) first, returning one `withdrawals` entry with `near_token_id: "btc.omft.near"`, `transfer_tx_hash: "hash-B"`.
3. Call `describeWithdrawal` for index 0 (address A). `findMatchingWithdrawal` matches on `assetId` only and returns the entry for B, so index 0 is reported `{status:"completed", txHash:"hash-B"}` even though A's own on-chain withdrawal has not settled (or settles differently). [4](#0-3)

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

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L99-124)
```typescript
	it("maintains indexes specific to bridge route", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal).mockResolvedValue({
			status: "completed",
			txHash: "fake-dest-hash",
		});

		await sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams, withdrawalParams],
		});

		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			1,
			expect.objectContaining({ index: 0 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			2,
			expect.objectContaining({ index: 1 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			3,
			expect.objectContaining({ index: 2 }),
		);
	});
```
