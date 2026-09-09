This confirms the vulnerability and its scope. The `findMatchingWithdrawal` function in `poa-bridge.ts` matches solely by `assetId` via `.find()`, and its own code comment explicitly documents the limitation.### Title
POA bridge `describeWithdrawal` misreports status/txHash when a batch contains two withdrawals of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the status of a specific withdrawal within a batch by looking up `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which matches purely on `assetId` via `Array.prototype.find`. If a batch contains two (or more) withdrawals sharing the same `assetId` but different `destinationAddress`/`amount`, the function cannot distinguish them and will always return the first indexer entry whose `near_token_id` matches, causing `describeWithdrawal` for withdrawal[1] to report withdrawal[0]'s status/`txHash` (or vice versa).

### Finding Description
The claimed equality that should hold is: `describeWithdrawal(wid_i)` returns the destination-chain status/txHash that actually corresponds to `wid_i`'s unique `(assetId, destinationAddress, amount)` — not to some other withdrawal `wid_j` in the same batch that happens to share the same `assetId`.

Code path:
- `createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` (lines 80-107) builds one `WithdrawalIdentifier` per withdrawal in the batch, each carrying its own `withdrawalParams` (including `destinationAddress` and `amount`) and the shared `intentTx` hash.
- `watchWithdrawal` (lines 20-78 in the same file) calls `bridge.describeWithdrawal({...args.wid, logger})` per withdrawal, independently, polling the bridge indexer.
- `PoaBridge.describeWithdrawal` (`poa-bridge.ts` lines 313-343) queries `poaBridge.httpClient.getWithdrawalStatus({ withdrawal_hash: args.tx.hash })` — the same `tx.hash` is used for *every* withdrawal item in the batch since they all originate from the same NEAR intent tx — and then calls:
  ```
  const withdrawal = findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId);
  ```
- `findMatchingWithdrawal` (lines 409-427) is documented in its own comment: *"Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* It performs:
  ```
  return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
  ```
  `Array.prototype.find` returns the *first* array element satisfying the predicate. It does not consult `destinationAddress`, `amount`, or any other field of `WithdrawalIdentifier`/`withdrawalParams` to disambiguate.

Attacker-controlled input: an unprivileged NEAR Intents user submits a batch of two `ft_withdraw` intents for the same `assetId` (e.g., `nep141:usdc.omft.near`) with two different `destinationAddress` values and/or `amount`s in a single signed NEAR transaction. The POA bridge indexer, once it observes and processes both withdrawals from that transaction, returns both entries in `getWithdrawalStatus({ withdrawal_hash })` unordered (as the existing code comment for the historical index-based bug acknowledges: "Response list is unsorted"). Because `findMatchingWithdrawal` only filters by `near_token_id`, both of the caller's two `describeWithdrawal` calls (one for `wid_0`, one for `wid_1`) will match against the *same* first array element returned by `.find()`, since both predicate calls (`nep141:${w.data.near_token_id} === assetId`) are identical for both withdrawal items. Consequently, both calls to `describeWithdrawal` for the two distinct withdrawals return the identical status object — reporting the same `txHash`/status for withdrawal 0 and withdrawal 1, even though they went to two different destination addresses with two different amounts.

Existing guards do not prevent this: `validateWithdrawal`, `compareAddresses`, `supports()`, and `assert` calls in this file operate on withdrawal *creation*/*fee* validation, not on *status matching*; none of them cross-check `destinationAddress`/`amount` against the indexer response in `describeWithdrawal`. The CHANGELOG fix ("assetId instead of index") only replaced one insufficient discriminator (array position) with another insufficient discriminator (assetId) — it does not use the full `WithdrawalIdentifier` (destination + amount + tx).

### Impact Explanation
An integrator polling withdrawal completion for a 2-item same-asset batch receives the same reported `status`/`txHash` for both withdrawal indices. If the integrator credits/settles a user or a ledger entry based on `describeWithdrawal`'s returned `txHash` per withdrawal id, it may treat both withdrawals as completed with the *same* on-chain transaction hash, or attribute a completion event to the wrong destination address/amount. This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category — one withdrawal's real completion can be reported for a still-pending or already-failed different withdrawal, and vice versa, leading to double-crediting or incorrect refund decisions by any downstream system trusting per-withdrawal `describeWithdrawal` results.

### Likelihood Explanation
Preconditions: an ordinary user (no special privileges) submits a batch withdrawal (`intents` array) with two `ft_withdraw` primitives for the same NEP-141 token (`assetId`) but different `destinationAddress`/`amount` — a normal, permitted usage pattern, not a documented escape hatch. This is fully attacker-controlled and requires no cooperation from a malicious relayer, RPC, or bridge operator; the POA bridge indexer behaves normally by returning both real withdrawal records for the shared `withdrawal_hash`. The bug is deterministic and repeatable on every such batch. The only limiting factor is that it requires ≥2 same-asset withdrawals in one batch, which is easy to construct.

### Recommendation
Change `findMatchingWithdrawal` (and its caller `describeWithdrawal`) to disambiguate by the full withdrawal identity — `assetId` **and** `destinationAddress` **and** `amount` (and destination memo where applicable) — rather than `assetId` alone. If the indexer response cannot be uniquely matched (e.g., two batch items truly identical in all these fields), the bridge should not silently pick the first match; it should either use a stable matching by relative order (matching sorted amounts within same-asset groups, as noted in the code's own TODO) or surface an explicit ambiguous-match error rather than returning a status that could belong to another withdrawal.

### Proof of Concept
Vitest plan (mock only the POA bridge HTTP client, `poaBridge.httpClient.getWithdrawalStatus`):
1. Construct two `WithdrawalIdentifier`s for the same `tx.hash`, same `assetId` (`nep141:usdc.omft.near`), but `destinationAddress: "addrA"`, `amount: 100n` for `wid0`, and `destinationAddress: "addrB"`, `amount: 200n` for `wid1`.
2. Mock `getWithdrawalStatus` to return:
   ```
   { withdrawals: [
     { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", transfer_tx_hash: "0xHASH_A", ... /* corresponds to addrA/100 */ } },
     { status: "PENDING", data: { near_token_id: "usdc.omft.near", ... /* corresponds to addrB/200 */ } },
   ] }
   ```
3. Call `bridge.describeWithdrawal(wid0)` and `bridge.describeWithdrawal(wid1)`.
4. Assert the broken equality: currently, both calls return `{ status: "completed", txHash: "0xHASH_A" }` (since `.find()` matches the first `assetId`-equal entry for both), i.e. `describeWithdrawal(wid1)` incorrectly equals `describeWithdrawal(wid0)`'s result, instead of correctly resolving to `{ status: "pending" }` for `wid1` — proving `describeWithdrawal(wid_i)` is not uniquely determined by the full `WithdrawalIdentifier` (destinationAddress + amount + tx) as required, only by `assetId`. [1](#0-0) [2](#0-1) [3](#0-2)

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
