### Title
`findMatchingWithdrawal` matches same-token withdrawals by assetId only, causing status/txHash misattribution across identifiers in a batch - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the status for a given `WithdrawalIdentifier` by calling `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which matches purely on `nep141:<near_token_id> === assetId` via `Array.prototype.find`. When a single NEAR intents transaction contains two or more withdrawals of the same PoA token (e.g. two `nep141:cardano.omft.near` withdrawals to different destination addresses), both `WithdrawalIdentifier`s produce the identical `assetId`, so `find()` deterministically returns the same (first) matching entry from the API's withdrawal list for both identifiers.

### Finding Description
The broken equality: the code implicitly assumes `withdrawal.destinationAddress/amount == args.withdrawalParams.destinationAddress/amount` is guaranteed once `nep141:<near_token_id> == assetId` holds. This assumption is false when a batch contains ≥2 withdrawals of the same token.

Code path:
- `PoaBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343`) calls `getWithdrawalStatusWithRetry` then `findMatchingWithdrawal`.
- `findMatchingWithdrawal` (`poa-bridge.ts:418-427`) does `withdrawals.find((w) => \`nep141:${w.data.near_token_id}\` === assetId)`. The developer comment explicitly documents the limitation: *"NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."*
- `createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107` builds one `WithdrawalIdentifier` per withdrawal param in the batch, all sharing the same `tx` (NEAR intent tx) and, for repeated same-token withdrawals, the same `assetId`.
- `watchWithdrawal` (`withdrawal-watcher.ts:20-78`) polls `bridge.describeWithdrawal({...wid, logger})` independently for each identifier.

Since the identifiers differ only by `index` (which `describeWithdrawal` never uses — it explicitly ignores index "Response list is unsorted, so we match by assetId instead of index") and `withdrawalParams` (destinationAddress/amount, which are also never inspected during matching), any two withdrawals with the same `assetId` will resolve to the *same* matched API record for both, and thus the same `status`/`txHash` will be reported to both `WithdrawalIdentifier` consumers regardless of which of the two real on-chain payouts corresponds to which identifier.

Exploit flow: an ordinary user (or an integrator following instructions from an untrusted counterparty) submits a withdrawal batch with two intents for the same `nep141:cardano.omft.near` token, one to destination A (amount X) and one to destination B (amount Y), inside a single NEAR intents transaction. The relayer/PoA processor executes both withdrawals; the PoA HTTP API's `withdrawal_status` for the tx hash returns both entries. When the integrator calls `IntentsSDK.waitForWithdrawalCompletion` for both identifiers, `findMatchingWithdrawal` returns the same entry (e.g., the one for destination A, whichever is first in `withdrawals` array — order not guaranteed) to both identifiers. If A's payout completes first, the identifier tracking B's withdrawal will report `status: "completed"` with A's `txHash`, even though B's payout may still be pending, failed, or landed with a different amount/address.

None of the existing guards prevent this: `validateWithdrawal`, `compareAddresses`, and `supports()` operate at intent-creation time and don't consider batch composition; there is no cross-check between `withdrawal.data.address`/`withdrawal.data.amount` and `args.withdrawalParams.destinationAddress`/`amount` in `describeWithdrawal`.

### Impact Explanation
An integrator relying on `IntentsSDK.waitForWithdrawalCompletion` (via `watchWithdrawal`/`describeWithdrawal`) can receive a `completed` status and `txHash` for a `WithdrawalIdentifier` that does not correspond to the identifier's own destination/amount — the misreport uses another withdrawal's real completion data. This can cause an integrator to prematurely credit/mark-complete a payout that has not actually landed at the expected destination, or to associate the wrong `txHash` with a given user withdrawal record. This matches the "High" impact category: *a status or hash misreport making an integrator credit or refund twice.* It is repeatable on every batch containing ≥2 same-token PoA withdrawals for as long as the API returns multiple entries for that `withdrawal_hash`.

### Likelihood Explanation
Preconditions: the attacker (or an ordinary integrator-forwarded batch) needs only to construct a withdrawal batch with two or more withdrawal params sharing the same PoA `assetId` (e.g., `nep141:cardano.omft.near`) in a single intents transaction — a normal, unprivileged SDK usage pattern requiring no special access. The cost is a single transaction with the required withdrawal amounts; feasibility is high since nothing in `supports()`, `validateWithdrawal()`, or intent construction rejects duplicate-asset batches. This is fully repeatable per batch/transaction.

### Recommendation
Extend `findMatchingWithdrawal` to disambiguate among multiple candidates sharing the same `assetId` by also matching on `destinationAddress` (and ideally `amount`, accounting for fees) via `compareAddresses`, and/or reject/guard batches containing duplicate `assetId` withdrawals for the PoA route until the upstream API supports disambiguation, per the maintainers' own comment about sorting by amount when duplicate assetIds are unsupported.

### Proof of Concept
Vitest plan (mock only `poaBridge.httpClient.getWithdrawalStatus`):
```ts
vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
  withdrawals: [
    { status: "COMPLETED", data: { near_token_id: "cardano.omft.near", address: "addr_A", amount: 1000000, transfer_tx_hash: "txA", ... } },
    { status: "PENDING",   data: { near_token_id: "cardano.omft.near", address: "addr_B", amount: 2000000, transfer_tx_hash: null, ... } },
  ],
});

const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: [] });

const resultA = await bridge.describeWithdrawal({
  landingChain: Chains.Cardano, index: 0,
  withdrawalParams: { assetId: "nep141:cardano.omft.near", amount: 1000000n, destinationAddress: "addr_A", feeInclusive: false },
  tx: { hash: "tx-hash", accountId: "test.near" },
});

const resultB = await bridge.describeWithdrawal({
  landingChain: Chains.Cardano, index: 1,
  withdrawalParams: { assetId: "nep141:cardano.omft.near", amount: 2000000n, destinationAddress: "addr_B", feeInclusive: false },
  tx: { hash: "tx-hash", accountId: "test.near" },
});

// Broken equality demonstrated: resultB should reflect addr_B's PENDING state,
// but instead equals resultA (addr_A's COMPLETED/txA), because both calls
// match the first array entry for the shared assetId.
expect(resultA).toEqual({ status: "completed", txHash: "txA" });
expect(resultB).toEqual({ status: "completed", txHash: "txA" }); // WRONG: should be { status: "pending" }
```
This demonstrates `resultB` (destination B, still pending) is misreported as `completed` with destination A's `txHash`, confirming the misattribution. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-107)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

	try {
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

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

					return POLL_PENDING;
				} catch (err: unknown) {
					if (err instanceof WithdrawalFailedError) {
						throw err;
					}

					consecutiveErrors++;
					if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
						throw new WithdrawalWatchError(err);
					}

					args.logger?.warn(
						`Transient error (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}): ${err}`,
					);
					return POLL_PENDING;
				}
			},
			{ stats, signal: args.signal },
		);
	} catch (err: unknown) {
		if (err instanceof PollTimeoutError) {
			throw new WithdrawalWatchError(err);
		}
		throw err;
	}
}

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
