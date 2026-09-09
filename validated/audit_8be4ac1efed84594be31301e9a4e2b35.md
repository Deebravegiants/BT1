## Root cause confirmation

In `createWithdrawalIdentifiers` (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`), batch withdrawals routed through the same bridge share one NEAR `intentTx.hash` and are assigned a **per-bridge sequential index** (`currentIndex = indexes.get(bridge.route) ?? 0`) based purely on the order the caller supplied `withdrawalParams`, with no binding to the actual on-chain transfer that will be produced by that index. [1](#0-0) 

`OmniBridge.describeWithdrawal` then resolves status purely by that positional index into the API's transfer list for the given tx hash — `(await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash }))[args.index]` — without ever checking that the returned transfer's `recipient`/token actually corresponds to the `withdrawalParams` (`destinationAddress`, `assetId`) being queried: [2](#0-1) 

This is exactly the same bug class the sibling `PoaBridge.describeWithdrawal` had and was patched for, per the CHANGELOG entry "Fix POA bridge withdrawal matching to use assetId instead of index" — the fix comment explicitly states "Response list is unsorted, so we match by assetId instead of index": [3](#0-2) [4](#0-3) 

The Omni Bridge path never received the equivalent fix and still trusts raw index ordering, as confirmed by the test `"returns correct transfer by index"` which locks in index-based (not identity-based) matching as intended behavior: [5](#0-4) 

Batch withdrawals through Omni Bridge are a supported, documented feature (multiple tokens/destinations in one intent, tracked by array index into `withdrawalParams`), and `waitForWithdrawalCompletion`/`processWithdrawal` fan out per-index using exactly this `describeWithdrawal` call: [6](#0-5) [7](#0-6) 

## The equality being broken

The correct invariant should be: *the `txHash`/`recipient` reported for withdrawal `i` == the on-chain transfer whose `recipient`/`token` matches `withdrawalParams[i]`.* Instead, the code reports: *the transfer located at array position `i` in whatever order the Omni Bridge indexer API returns*, an order this same codebase's own PoA-bridge fix documents as unsorted/unstable. If the API returns transfers for a single NEAR tx in an order that doesn't match submission order (a plausible operational condition given the PoA precedent, and not something the SDK controls or validates), `describeWithdrawal(index=i)` will report **another withdrawal's** `recipient`/`txHash` as the completed result for withdrawal `i`.

### Title
Omni Bridge `describeWithdrawal` Trusts Unvalidated Positional Index Into an Externally-Ordered Transfer List, Enabling Withdrawal Status/TxHash Misattribution in Batches — (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
`OmniBridge.describeWithdrawal` selects the transfer to report on via `getTransfer(...)[args.index]`, a raw array index, without verifying the selected transfer's `recipient`/token match the `withdrawalParams` actually being queried. This mirrors the exact bug the PoA bridge had (and fixed by matching on `assetId` instead of index, because "Response list is unsorted"), but the fix was never applied to the Omni bridge.

### Finding Description
- `createWithdrawalIdentifiers` assigns each batched withdrawal a `index` per bridge route based solely on the caller-supplied order of `withdrawalParams`, with no cryptographic or data binding to the specific transfer that will actually be created on-chain.
- `OmniBridge.describeWithdrawal` fetches all transfers for the shared NEAR `tx.hash` and picks element `[args.index]`, then reports that transfer's `recipient` and `txHash` as the result for the withdrawal being queried, with only a `recipient == null` null-check — no comparison against `args.withdrawalParams.destinationAddress` or `assetId`.
- The PoA bridge (a structurally identical multi-withdrawal-per-tx design) required exactly this fix, documented in its changelog and code comment as "Response list is unsorted, so we match by assetId instead of index." No equivalent safeguard, and no comment asserting order stability, exists for the Omni bridge.

### Impact Explanation
When a batch of withdrawals is routed through the Omni Bridge in a single NEAR intent transaction, and the bridge's transfer-list API returns entries in an order different from submission order (the same failure mode the PoA bridge patch was created to address), `describeWithdrawal` will report a **different withdrawal's** destination `txHash`/`recipient` as "completed" for the wrong `withdrawalParams` entry. An integrator using `waitForWithdrawalCompletion`/`processWithdrawal`/`createWithdrawalCompletionPromises` in a batch would then attribute funds delivered to counterparty A's address as belonging to counterparty B's withdrawal (or vice versa), which is a status/hash misreport that can cause an integrator to credit the wrong withdrawal as settled — matching the "status reported that is not the on-chain outcome" / "double credit" impact class (High).

### Likelihood Explanation
Likelihood depends entirely on whether the Omni Bridge indexer API preserves submission order for multiple transfers sharing one origin tx hash. This is an external-service ordering assumption that the codebase itself has already shown (via the PoA bridge incident) not to always hold. No caller-malicious action is required — it is triggered by ordinary use of the documented batch-withdrawal feature under an unfavorable (but demonstrated-possible) API response ordering.

### Recommendation
In `OmniBridge.describeWithdrawal`, stop relying on raw positional indexing into `getTransfer()`'s result. Match the correct transfer by a stable identifier that ties it to the specific `withdrawalParams` being queried (e.g., `recipient` address plus asset/token id, and/or amount), analogous to the `findMatchingWithdrawal` approach already used in `poa-bridge.ts`, rather than assuming `getTransfer` results are returned in submission order.

### Proof of Concept
1. Submit a single NEAR intent batching two Omni Bridge withdrawals: withdrawal[0] → `destinationAddress = "0xAAA..."`, withdrawal[1] → `destinationAddress = "0xBBB..."`.
2. `createWithdrawalIdentifiers` assigns `index: 0` to the AAA withdrawal and `index: 1` to the BBB withdrawal, both sharing the same `tx.hash`.
3. Suppose the Omni Bridge indexer's `getTransfer({transactionHash})` returns the BBB transfer first and AAA transfer second (order not guaranteed, as demonstrated by the analogous PoA-bridge issue).
4. `describeWithdrawal({index: 0, withdrawalParams: {destinationAddress: "0xAAA...", ...}, tx})` picks `transfers[0]`, which is actually the BBB transfer, and returns `{status: "completed", txHash: <BBB's tx hash>}` — reported as the completion of the AAA withdrawal.
5. An integrator polling per-index (as shown in the SDK's own batch-withdrawal usage examples) records the wrong destination transaction hash against the AAA withdrawal.

**Uncertainty note:** I could not directly verify, from indexed content, whether the live `@omni-bridge/core` `BridgeAPI.getTransfer` endpoint guarantees ordering by submission — this is an external dependency whose behavior isn't fully covered by the repo index. The PoA bridge's own history of hitting and fixing this exact ordering assumption is the strongest available evidence in-repo that such an assumption is unsafe for these bridges.

### Citations

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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-731)
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

		const destinationChain = getChain(transfer.recipient as OmniAddress);
		let txHash = null;
		if (
			isEvmChain(destinationChain) ||
			destinationChain === ChainKind.Sol ||
			destinationChain === ChainKind.Fogo ||
			destinationChain === ChainKind.Strk ||
			destinationChain === ChainKind.Aptos
		) {
			txHash = transfer.finalised?.transaction_hash;
		} else if (isUtxoChain(destinationChain)) {
			// pending_sign_id is not the finalised tx hash. In rare cases, the hash may
			// change if the BTC transfer fails to be submitted. We return fast hash for FE and
			// wait for final one (transfer.finalised?.transaction_hash) for BE.
			txHash =
				typeof window !== "undefined"
					? transfer.utxo_meta?.pending_sign_id
					: transfer.finalised?.transaction_hash;
		} else {
			return { status: "completed", txHash: null };
		}

		if (!txHash) {
			return { status: "pending" };
		}

		return { status: "completed", txHash };
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-326)
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
```

**File:** packages/internal-utils/CHANGELOG.md (L236-238)
```markdown
### Patch Changes

- 8bbd5c6: Fix POA bridge withdrawal matching to use assetId instead of index.
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.test.ts (L515-572)
```typescript
		it("returns correct transfer by index", async () => {
			vi.spyOn(BridgeAPI.prototype, "getTransfer").mockResolvedValue([
				createTransferMock({
					recipient: "eth:0x1111111111111111111111111111111111111111",
					finalised: {
						transaction_hash: "0xfirst-tx",
						chain: "Eth",
						timestamp_seconds: 1700000000,
						details: {
							type: "evm",
							block_number: 1,
							transaction_index: null,
							log_index: null,
						},
					},
				}),
				createTransferMock({
					recipient: "eth:0x2222222222222222222222222222222222222222",
					finalised: {
						transaction_hash: "0xsecond-tx",
						chain: "Eth",
						timestamp_seconds: 1700000001,
						details: {
							type: "evm",
							block_number: 2,
							transaction_index: null,
							log_index: null,
						},
					},
				}),
			]);

			const nearProvider = nearFailoverRpcProvider({
				urls: PUBLIC_NEAR_RPC_URLS,
			});

			const bridge = new OmniBridge({
				envConfig: configsByEnvironment.production,
				nearProvider,
			});

			const result = await bridge.describeWithdrawal({
				landingChain: Chains.Ethereum,
				index: 1,
				withdrawalParams: {
					assetId: "nep141:eth.bridge.near",
					amount: 100000n,
					destinationAddress: zeroAddress,
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
				status: "completed",
				txHash: "0xsecond-tx",
			});
		});
```

**File:** packages/intents-sdk/src/sdk.ts (L486-521)
```typescript
	}): Promise<TxInfo | TxNoInfo>;

	public waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams[];
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<Array<TxInfo | TxNoInfo>>;

	public async waitForWithdrawalCompletion(args: {
		withdrawalParams: WithdrawalParams | WithdrawalParams[];
		intentTx: NearTxInfo;
		signal?: AbortSignal;
		logger?: ILogger;
	}): Promise<(TxInfo | TxNoInfo) | Array<TxInfo | TxNoInfo>> {
		const withdrawalParamsArray = Array.isArray(args.withdrawalParams)
			? args.withdrawalParams
			: [args.withdrawalParams];

		const promises = this.createWithdrawalCompletionPromises({
			withdrawalParams: withdrawalParamsArray,
			intentTx: args.intentTx,
			signal: args.signal,
			logger: args.logger,
		});

		const result = await Promise.all(promises);

		if (Array.isArray(args.withdrawalParams)) {
			return result;
		}

		assert(result.length === 1, "Unexpected result length");
		// biome-ignore lint/style/noNonNullAssertion: length asserted above
		return result[0]!;
	}
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
