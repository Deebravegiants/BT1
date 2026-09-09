### Title
PoA Bridge withdrawal-status matching by `assetId` alone misreports destination tx hash for batch withdrawals of the same token - (File: packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts / packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
The SDK's PoA bridge status-lookup functions identify which on-chain withdrawal record corresponds to a given withdrawal by comparing only `assetId` (`nep141:${near_token_id}`), ignoring destination address, amount, or ordering. When a batch withdrawal (a feature explicitly supported by `sdk.processWithdrawal({ withdrawalParams: [...] })`) contains two or more withdrawals of the *same* token to *different* destination addresses/amounts, every one of those withdrawals resolves to the *same* matched PoA record, so the reported `destinationTxHash`/`txHash` does not correspond to the actual on-chain outcome of each individual withdrawal.

### Finding Description
`findMatchingWithdrawal` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (lines 144-153) and the analogous function in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (lines 418-427) both select a withdrawal record using:
```
withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId)
``` [1](#0-0) [2](#0-1) 

This is the sole criterion used to bind a per-withdrawal "completion" report to a specific PoA API record — there is no comparison against `destinationAddress`, `amount`, or a stable index. Both functions' own doc-comments openly acknowledge the gap: "Currently only matches by assetId... This means multiple withdrawals of the same token in a single transaction are not supported." [3](#0-2) 

However, nothing in `sdk.ts` (`processWithdrawal`, `signAndSendWithdrawalIntent`, `waitForWithdrawalCompletion`, `createWithdrawalCompletionPromises`) rejects or validates that batch `withdrawalParams` contain duplicate `assetId`s. [4](#0-3) 
The README explicitly documents/encourages batch withdrawals, and its examples show `Array<Promise>` returned by index, with each index expected to resolve to the corresponding withdrawal's own destination tx. [5](#0-4) 

Because `waitForWithdrawalCompletion` is invoked independently per withdrawal (see `sdk.waitForWithdrawalCompletion.test.ts` showing per-index calls to `describeWithdrawal`), when two withdrawals in the same intent share the same `assetId`, both lookups query the same (unsorted) PoA response and both match the *first* record found for that `assetId` — resulting in both promises resolving to the identical `txHash`, even though two genuinely distinct on-chain transfers (to two different destination addresses/amounts) exist. [6](#0-5) 

The equality broken here is: *the destination tx hash reported for withdrawal N must be the hash of the on-chain transfer that actually executed withdrawal N's `(assetId, amount, destinationAddress)`.* Instead, the SDK reports the same tx hash (or, depending on array order, the wrong one) for multiple distinct withdrawals.

### Impact Explanation
An integrator relying on `destinationTx[i]` per withdrawal index to reconcile off-chain bookkeeping (e.g., "credit withdrawal to address A once tx X is seen") could be misled: it may see the same `txHash` reported as the completion evidence for two different withdrawals whose actual destination addresses differ, or a `txHash` that in reality belongs to another user's withdrawal segment in the batch. This falls under the "status or hash misreport making an integrator credit or refund twice" category — an integrator could mistakenly treat two separate withdrawals as both completed via a single actual transfer, double-crediting downstream ledgers, or misattribute funds to the wrong destination in its records, without any recovery path since the underlying PoA API response is not disambiguated.

### Likelihood Explanation
No malicious actor is required — this is triggered by ordinary use of the explicitly documented batch-withdrawal feature (`sdk.processWithdrawal({ withdrawalParams: [...] })`) whenever a caller includes two or more withdrawals of the same token (e.g., splitting one token to two recipients) in a single batch. There is no validation anywhere in the withdrawal pipeline (`sdk.ts`, `poa-bridge.ts`, `waitForWithdrawalCompletion.ts`) that blocks or warns against this input, so it is easily reachable in production use.

### Recommendation
Disambiguate PoA withdrawal matching by more than `assetId`: match using amount and/or destination address together with `near_token_id`, or (preferably) require/track a stable per-withdrawal correlation identifier from the PoA bridge API. Until the API supports this, `processWithdrawal`/`signAndSendWithdrawalIntent`/`estimateWithdrawalFee` should validate batch input and throw if multiple entries share the same `assetId` destined for the PoA bridge, to prevent silently misreported completion status.

### Proof of Concept
1. Call `sdk.processWithdrawal({ withdrawalParams: [ { assetId: "nep141:usdt.omft.near", amount: 100n, destinationAddress: "ADDR_A" }, { assetId: "nep141:usdt.omft.near", amount: 200n, destinationAddress: "ADDR_B" } ] })` — a legitimate batch withdrawal of the same PoA-bridged token to two different destinations, as documented in the README's "Batch Withdrawals" section.
2. Once the intent settles on NEAR and PoA processes both destination transfers, `sdk.waitForWithdrawalCompletion` internally calls `describeWithdrawal`/`findMatchingWithdrawal` independently for each of the two withdrawal params, both using `assetId = "nep141:usdt.omft.near"` as the only match criterion (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427`).
3. Both lookups against the PoA API's unsorted `withdrawals` array return the *same first-matching* record (or a swapped one), so `destinationTx[0]` and `destinationTx[1]` can both surface the tx hash belonging to only one of the two actual transfers (e.g., the transfer to `ADDR_A`), even though `destinationTx[1]` should correspond to the separate transfer to `ADDR_B`.
4. An integrator consuming `destinationTx[0]`/`destinationTx[1]` by index credits/records the wrong transaction against the wrong withdrawal, exactly as flagged by the code's own comment: "multiple withdrawals of the same token in a single transaction are not supported" — yet nothing prevents constructing such a batch.

### Citations

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-143)
```typescript
/**
 * Finds a withdrawal matching the given criteria.
 *
 * NOTE: Currently only matches by assetId (near_token_id). This means multiple
 * withdrawals of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
function findMatchingWithdrawal(
	withdrawals: types.WithdrawalStatusResponseOk["result"]["withdrawals"],
	criteria: WithdrawalCriteria,
):
	| types.WithdrawalStatusResponseOk["result"]["withdrawals"][number]
	| undefined {
	return withdrawals.find(
		(w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
	);
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

**File:** packages/intents-sdk/src/sdk.ts (L793-838)
```typescript
	async processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams | WithdrawalParams[]>,
	): Promise<WithdrawalResult | BatchWithdrawalResult> {
		const withdrawalParams = Array.isArray(args.withdrawalParams)
			? args.withdrawalParams
			: [args.withdrawalParams];

		// Step 1: Estimate fee
		const feeEstimation = await (() => {
			if (args.feeEstimation != null) {
				return Array.isArray(args.feeEstimation)
					? args.feeEstimation
					: [args.feeEstimation];
			}

			return this.estimateWithdrawalFee({
				withdrawalParams,
				logger: args.logger,
			});
		})();

		// Step 2: Sign and send intent
		const { intentHash } = await this.signAndSendWithdrawalIntent({
			withdrawalParams,
			feeEstimation,
			referral: args.referral,
			intent: args.intent,
			logger: args.logger,
		});

		args.logger?.info("Intent published", { intentHash });

		// Step 3: Wait for intent settlement
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

**File:** packages/intents-sdk/README.md (L521-563)
```markdown
### Batch Withdrawals

Process multiple withdrawals in a single intent:

```typescript
const withdrawalParams = [
    {
        assetId: 'nep141:usdt.tether-token.near',
        amount: 1000000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    },
    {
        assetId: 'nep245:v2_1.omni.hot.tg:137_qiStmoQJDQPTebaPjgx5VBxZv6L',
        amount: 100000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    }
]

// Method 1: Complete end-to-end batch processing
const batchResult = await sdk.processWithdrawal({
    withdrawalParams,
    // feeEstimation is optional - will be estimated automatically if not provided
});

console.log('Batch intent hash:', batchResult.intentHash);
console.log('Destination transactions:', batchResult.destinationTx); // Array of results

// Method 2: Step-by-step batch processing for granular control
const feeEstimation = await sdk.estimateWithdrawalFee({
    withdrawalParams
});

const {intentHash} = await sdk.signAndSendWithdrawalIntent({
    withdrawalParams,
    feeEstimation
});

const intentTx = await sdk.waitForIntentSettlement({intentHash});

// See "Waiting for Batch Completion" below for completion options
```
```

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L43-67)
```typescript
	it("supports multiple withdrawals (preserving tx info order)", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal)
			.mockImplementationOnce(() =>
				wait(300).then(() => ({
					status: "completed" as const,
					txHash: "fake-dest-hash-1",
				})),
			)
			.mockResolvedValueOnce({
				status: "completed",
				txHash: "fake-dest-hash-2",
			});

		const result = sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams],
		});

		await expect(result).resolves.toEqual([
			{ hash: "fake-dest-hash-1" },
			{ hash: "fake-dest-hash-2" },
		]);
		expect(mockBridge.describeWithdrawal).toHaveBeenCalledTimes(2);
```
