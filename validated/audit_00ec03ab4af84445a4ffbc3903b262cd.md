### Title
HOT Bridge withdrawal status reports "completed" without checking the `verified_withdraw` flag returned by the API - (File: `packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts`)

### Summary
`HotBridge.fetchWithdrawalHashFromApi` parses the HOT API withdrawal response — which explicitly includes a `verified_withdraw: boolean` field per withdrawal — but never inspects that field before returning a destination transaction hash as proof of a `"completed"` withdrawal. The result is that `describeWithdrawal`/`watchWithdrawal` (and therefore `sdk.waitForWithdrawalCompletion`/`sdk.processWithdrawal`) can report a withdrawal as finished based on an unverified/tentative hash the HOT indexer itself has not confirmed.

### Finding Description
The API response schema captures the verification flag explicitly: [1](#0-0) 

But the fallback lookup that turns this response into a status only checks `nonce` match and that the `hash` is present/hex — `verified_withdraw` is read into the parsed object and then simply discarded: [2](#0-1) 

This function is invoked from `describeWithdrawal` both as the primary fallback for EVM/Stellar/TON withdrawals when the bridge indexer errors, and as the fallback for other chains when the on-chain contract view returns null/pending: [3](#0-2) [4](#0-3) 

In every branch, as soon as `apiHash != null`, the function unconditionally returns `{ status: "completed", txHash: ... }` — there is no equality check that `verified_withdraw === true` before trusting the hash as evidence of on-chain completion. The tests themselves construct response fixtures that include `verified_withdraw: true` alongside the assertion of a `"completed"` result, confirming the field is present in the contract of the API but never asserted against in the implementation: [5](#0-4) 

This breaks the equality the report's bug class targets: "a status reported that is not the on-chain outcome." The SDK's contract with integrators is that `status: "completed"` means the withdrawal landed on the destination chain — see the documented semantics of `describeWithdrawal`/`waitForWithdrawalCompletion` in the `Bridge` interface and README: [6](#0-5) [7](#0-6) 

If HOT's own API sets `verified_withdraw: false` for a given withdrawal record (e.g., the destination-chain transaction is unconfirmed, reorged, or still pending finality checks on HOT's side) but has already populated a `hash`, the SDK will still treat the withdrawal as `"completed"` and hand back that `txHash` to the caller.

### Impact Explanation
`processWithdrawal`/`waitForWithdrawalCompletion` callers rely on `"completed"` to gate downstream actions (e.g., crediting a user's off-chain balance, releasing a linked custody action, or marking an order fulfilled) as shown in `sdk.ts`: [8](#0-7) 

If a withdrawal is reported "completed" while HOT itself has not verified it, an integrator could act on a false-positive completion (e.g., credit/refund based on a hash that HOT may later invalidate or that corresponds to a not-yet-final transfer), matching the "status ... misreport making an integrator credit or refund twice" High-impact category from the rules.

### Likelihood Explanation
This code path is reached automatically as one of the two fallback mechanisms whenever the primary bridge-indexer call fails or a chain's native contract-view status is pending/null — not an edge case requiring an admin/attacker action. Any HOT withdrawal experiencing a temporarily unverified state on HOT's backend during the fallback window will trigger the bug; no malicious input is needed. `verified_withdraw` was clearly added to the schema for exactly this purpose, so its complete disregard represents a real, exploitable gap in normal operation rather than a theoretical corner case.

### Recommendation
In `fetchWithdrawalHashFromApi` (and analogously if the bridge indexer response carries an equivalent flag), only accept `withdrawal.hash` as proof of completion when `withdrawal.verified_withdraw === true`; otherwise treat it as `"pending"` the same as a missing hash.

### Proof of Concept
1. Mock `hotSdk.api.requestApi` (as in the existing test suite) to return a withdrawal entry with a well-formed `hash` but `verified_withdraw: false`.
2. Call `bridge.describeWithdrawal(wid)` via the EVM/other-chain fallback path.
3. Observe the function returns `{ status: "completed", txHash: <hash> }` despite `verified_withdraw` being `false`, matching what the existing test at `hot-bridge.test.ts:669-720` asserts for the `true` case — the code path is identical regardless of the flag's value, since it is never read.

### Citations

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L53-66)
```typescript
const HotApiWithdrawalSchema = v.object({
	hash: v.nullable(v.string()),
	nonce: v.string(),
	near_trx: v.string(),
	verified_withdraw: v.boolean(),
	chain_id: v.number(),
});

const HotApiWithdrawalResponseSchema = v.object({
	hash: v.nullable(v.string()),
	nonce: v.string(),
	near_trx: v.string(),
	withdrawals: v.array(HotApiWithdrawalSchema),
});
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L439-463)
```typescript
				// Bridge indexer failed, fallback to HOT API
				args.logger?.error(
					"Bridge indexer failed unexpectedly, trying HOT API fallback",
					{
						nearTxHash: args.tx.hash,
						nonce: nonce.toString(),
						error,
					},
				);
				const apiHash = await this.fetchWithdrawalHashFromApi(
					args.tx.hash,
					nonce,
					args.logger,
				);
				if (apiHash != null) {
					args.logger?.info("HOT API fallback found withdrawal hash", {
						withdrawalHash: apiHash,
						nearTxHash: args.tx.hash,
						nonce: nonce.toString(),
					});
					return {
						status: "completed",
						txHash: formatTxHash(apiHash, args.landingChain),
					};
				}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L488-499)
```typescript
			// Fallback: API indexer (when contract returns null/pending)
			const apiHash = await this.fetchWithdrawalHashFromApi(
				args.tx.hash,
				nonce,
				args.logger,
			);
			if (apiHash != null) {
				return {
					status: "completed",
					txHash: formatTxHash(apiHash, args.landingChain),
				};
			}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L541-584)
```typescript
	private async fetchWithdrawalHashFromApi(
		nearTxHash: string,
		nonce: bigint,
		logger?: ILogger,
	): Promise<string | null> {
		try {
			const response = await withTimeout(
				() =>
					this.hotSdk.api.requestApi(
						`/api/v1/evm/bridge_withdrawal_hash?near_trx=${nearTxHash}`,
						{ method: "GET" },
					),
				{ timeout: HotBridge.API_FALLBACK_TIMEOUT_MS },
			);
			const data: unknown = await response.json();

			const parseResult = v.safeParse(HotApiWithdrawalResponseSchema, data);
			if (!parseResult.success) {
				logger?.debug("HOT API response parse failed", {
					issues: parseResult.issues,
				});
				return null;
			}

			const withdrawal = parseResult.output.withdrawals.find(
				(w) => w.nonce === nonce.toString(),
			);

			if (withdrawal?.hash) {
				const hash = withdrawal.hash.replace(/^0x/, "");
				if (isHex(hash)) {
					logger?.info("HOT withdrawal hash found via API fallback", {
						nearTxHash,
						nonce: nonce.toString(),
					});
					return hash;
				}
			}
			return null;
		} catch (error) {
			logger?.debug("HOT API fallback failed", { error, nearTxHash });
			return null;
		}
	}
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.test.ts (L669-720)
```typescript
		it("returns completed via API fallback when contract returns null but API has hash", async () => {
			const hotSDK = new HotOmniSdk({
				logger: console,
				evmRpc: {},
				nearRpc: [],
				async executeNearTransaction() {
					throw new Error("not implemented");
				},
			});

			const bridge = new HotBridge({
				envConfig: configsByEnvironment.production,
				hotSdk: hotSDK,
			});

			vi.spyOn(hotSDK.near, "parseWithdrawalNonces").mockResolvedValue([1n]);
			vi.spyOn(hotSDK, "getGaslessWithdrawStatus").mockResolvedValue(null);
			mockBridgeIndexerFailure();
			vi.spyOn(hotSDK.api, "requestApi").mockResolvedValue(
				new Response(
					JSON.stringify({
						hash: "0xDEADBEEF",
						nonce: "1",
						near_trx: "txhash",
						withdrawals: [
							{
								hash: "0xDEADBEEF",
								nonce: "1",
								near_trx: "txhash",
								verified_withdraw: true,
								chain_id: 56,
							},
						],
					}),
				),
			);

			const wid = bridge.createWithdrawalIdentifier({
				withdrawalParams: {
					assetId: BNB_NATIVE_ASSET_ID,
					amount: 100n,
					destinationAddress: zeroAddress,
					feeInclusive: false,
				},
				index: 0,
				tx: { hash: "txhash", accountId: "test.near" },
			});

			const result = await bridge.describeWithdrawal(wid);

			expect(result).toEqual({ status: "completed", txHash: "0xDEADBEEF" });
		});
```

**File:** packages/intents-sdk/src/shared-types.ts (L425-431)
```typescript
	/**
	 * One-shot status check for a withdrawal.
	 * Returns the current status without polling.
	 */
	describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus>;
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L36-47)
```typescript
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

**File:** packages/intents-sdk/src/sdk.ts (L833-838)
```typescript
		// Step 4: Wait for withdrawal completion
		const destinationTx = await this.waitForWithdrawalCompletion({
			withdrawalParams,
			intentTx,
			logger: args.logger,
		});
```
