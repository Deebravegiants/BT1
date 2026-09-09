### Title
Same-`assetId` batch withdrawals cause `describeWithdrawal` to report the wrong index's status/txHash - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves each withdrawal's status by matching only on `assetId` via `findMatchingWithdrawal`, with no disambiguation by index, amount, or destination address. When a batch contains two or more `WithdrawalParams` entries with the same `assetId` but different `destinationAddress`/`amount`, every index resolves to the same (first) matching entry in the unsorted POA API response, so an integrator can receive index 0's completed status/txHash for what is actually index 1's withdrawal (or vice versa).

### Finding Description
The broken equality: `describeWithdrawal({index: i}).txHash/status` should correspond to the on-chain outcome of `withdrawalParams[i]` (the withdrawal actually sent to `withdrawalParams[i].destinationAddress`), i.e. `outcome(i) == describeWithdrawal(i)`. Instead, `findMatchingWithdrawal` at [1](#0-0)  selects `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` — the *first* array element whose asset matches, independent of `index`, `destinationAddress`, or `amount`. This is called from `describeWithdrawal` at [2](#0-1)  and the comment explicitly documents the limitation: "Currently only matches by assetId... multiple withdrawals of the same token in a single transaction are not supported" at [3](#0-2) .

There is no upstream guard preventing this scenario. `processWithdrawal` / `signAndSendWithdrawalIntent` build the batch intents from `withdrawalParamsArray` with a simple `zip`/`map` and no uniqueness check on `assetId` [4](#0-3) , and `waitForWithdrawalCompletion`/`createWithdrawalIntents` pass each `withdrawalParams[i]` through to `describeWithdrawal` per-index without any dedup or reconciliation against the other batch entries. `validateWithdrawal` only checks a single withdrawal's own address/amount validity [5](#0-4)  and does nothing to prevent duplicate `assetId`s across a batch.

Exploit flow: an attacker (a counterparty whose batch parameters an integrator forwards) supplies `withdrawalParams = [A, B]` where `A.assetId === B.assetId` but `A.destinationAddress !== B.destinationAddress` (and/or different amounts). Both withdrawals settle on the POA bridge side and appear in the unsorted `getWithdrawalStatus` response. When the integrator's code calls `describeWithdrawal` for index 0 and index 1, both calls run the identical `findMatchingWithdrawal` lookup and can return the same matched record — e.g., both report B's `transfer_tx_hash`/status, or index 0 gets credited with B's completed status while B's actual completion is never correctly attributed to itself.

### Impact Explanation
This directly matches the "status or hash misreport making an integrator credit or refund twice" High/Critical impact category: an integrator that tracks per-index completion (e.g., to release custody funds, mark an invoice paid, or refund a user) can attribute the wrong destination address's completed transaction to the wrong batch entry. This is repeatable on every batch withdrawal that has ≥2 entries with identical `assetId`, which is an ordinary attacker-controlled parameter set — no privileged access, malicious relayer, or bridge-contract bug required, purely an SDK-side aggregation defect confirmed by the code's own inline comment.

### Likelihood Explanation
Preconditions: PoaBridge route, and a batch of ≥2 withdrawals sharing the same `assetId` (trivial for an attacker/counterparty to construct since nothing rejects it). No special timing or bridge state is needed beyond both withdrawals eventually appearing in the POA `getWithdrawalStatus` response list. Attacker cost is zero beyond issuing a normal batch withdrawal request with duplicate asset IDs, and the defect is deterministic and repeatable each time such a batch is processed.

### Recommendation
Disambiguate matches beyond `assetId`: either (a) reject/validate batches containing duplicate `assetId` entries at `signAndSendWithdrawalIntent`/`processWithdrawal` time until POA API support exists, or (b) implement the sorting-by-amount reconciliation strategy already suggested in the code comment (sort both the API response and the local `withdrawalParams` sharing the same `assetId` by amount, since relayer fees are equal for the same token) so each index maps deterministically to the correct API entry, and add an assertion that flags/throws when duplicate assetIds are detected until proper matching is implemented.

### Proof of Concept
Vitest test plan (mock only `poaBridge.httpClient.getWithdrawalStatus`):
1. Mock `getWithdrawalStatus` to return two withdrawals for the same `near_token_id`, e.g. `withdrawals: [{status:"COMPLETED", data:{near_token_id:"usdt.tether-token.near", transfer_tx_hash:"HASH_B", destination_address:"ADDR_B"}}, {status:"COMPLETED", data:{near_token_id:"usdt.tether-token.near", transfer_tx_hash:"HASH_A", destination_address:"ADDR_A"}}]`.
2. Construct `withdrawalParams = [{assetId:"nep141:usdt.tether-token.near", destinationAddress:"ADDR_A", amount: 100n}, {assetId:"nep141:usdt.tether-token.near", destinationAddress:"ADDR_B", amount: 200n}]`.
3. Call `bridge.describeWithdrawal({ index: 0, withdrawalParams: withdrawalParams[0], tx, landingChain })` and `describeWithdrawal({ index: 1, withdrawalParams: withdrawalParams[1], tx, landingChain })`.
4. Assert equality violated: expect index 0's returned `txHash` to equal `"HASH_A"` (the withdrawal actually sent to `ADDR_A`), but the code instead returns `"HASH_B"` for both index 0 and index 1 (`findMatchingWithdrawal` returns the same/first matching entry regardless of index), demonstrating `describeWithdrawal(0).txHash !== outcome(ADDR_A)`.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-230)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
		destinationMemo?: string;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		// Use cached getSupportedTokens to avoid frequent API calls
		const { tokens } = await this.getCachedSupportedTokens(
			[toPoaNetwork(assetInfo.blockchain)],
			args.logger,
		);

		const tokenInfo = tokens.find(
			(token) => token.intents_token_id === args.assetId,
		);

		if (tokenInfo == null) {
			throw new UnsupportedAssetIdError(
				args.assetId,
				"`assetId` is not supported in PoA bridge.",
			);
		}

		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}

		if (!args.skipMinAmountValidation) {
			const minWithdrawalAmount = BigInt(tokenInfo.min_withdrawal_amount);
			if (args.amount < minWithdrawalAmount) {
				throw new MinWithdrawalAmountError(
					minWithdrawalAmount,
					args.amount,
					args.assetId,
				);
			}
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

**File:** packages/intents-sdk/src/sdk.ts (L689-715)
```typescript
	public async signAndSendWithdrawalIntent(
		args:
			| SignAndSendWithdrawalArgs<WithdrawalParams>
			| SignAndSendWithdrawalArgs<WithdrawalParams[]>,
	): Promise<IntentPublishResult> {
		let withdrawalParamsArray: WithdrawalParams[];
		let feeEstimations: FeeEstimation[];
		if (isBatchMode(args)) {
			withdrawalParamsArray = args.withdrawalParams;
			feeEstimations = args.feeEstimation;
		} else {
			withdrawalParamsArray = [args.withdrawalParams];
			feeEstimations = [args.feeEstimation];
		}

		const intentsP = zip(withdrawalParamsArray, feeEstimations).map(
			([withdrawalParams, feeEstimation]) => {
				return this.createWithdrawalIntents({
					withdrawalParams,
					feeEstimation,
					referral: args.referral ?? this.referral,
					logger: args.logger,
				});
			},
		);

		const intents = (await Promise.all(intentsP)).flat();
```
