### Title
DirectBridge.describeWithdrawal reports "completed" without verifying the ft_withdraw/native_withdraw promise outcome for that specific index - (File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts)

### Summary
`DirectBridge.describeWithdrawal` and `IntentsBridge.describeWithdrawal` unconditionally return `{status:"completed", txHash: args.tx.hash}` as soon as the enclosing NEAR settlement tx exists, without inspecting whether the specific `ft_withdraw`/`native_withdraw` intent at `args.index` actually succeeded on-chain. For `IntentsBridge`, the `transfer` intent is an internal, synchronous balance mutation inside `intents.near`, so a failure there panics the whole `execute_intents` call and the tx would never reach "SETTLED" — this half of the claim doesn't hold. For `DirectBridge`, however, `ft_withdraw` creates an external cross-contract promise to the token contract, and per the contract's own documented semantics ("Promises created by different intents are executed concurrently and does not rely on the order of the intents"), one withdrawal's promise can fail while the top-level `execute_intents` transaction still settles successfully.

### Finding Description
Equality claimed broken: reported `status: "completed"` for withdrawal `i` == actual on-chain execution outcome of the `i`-th `ft_withdraw`/`native_withdraw` intent.

Code path:
- `DirectBridge.createWithdrawalIntents` (`packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts:110-149`) creates one `ft_withdraw`/`native_withdraw` intent per withdrawal via `createWithdrawIntentPrimitive` (`direct-bridge-utils.ts:19-61`).
- Multiple such intents (for a batch of transfers) can be bundled into one signed `MultiPayload`'s `intents` array, per `Nep413DefuseMessage_for_DefuseIntents.intents`, whose schema explicitly warns: *"Promises created by different intents are executed concurrently and does not rely on the order of the intents in this structure"* (`packages/contract-types/schemas/intents.schema.json:4174`, similarly `NativeWithdraw`'s doc at `:4480` states *"the `wNEAR` will not be refunded in case of fail (e.g. `receiver_id` account does not exist)"*).
- `IntentRelayerPublic.waitForSettlement` (`packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts:73-92`) only confirms the intent was `SETTLED` (i.e., the top-level NEAR tx that called `execute_intents` succeeded) and returns `{ tx: { hash, accountId } }` — it carries no per-intent execution result.
- `DirectBridge.describeWithdrawal` (`direct-bridge.ts:334-338`) then does: `return { status: "completed", txHash: args.tx.hash };` — ignoring `args.index` entirely and never querying the NEAR tx receipts/outcomes to check whether the specific `ft_withdraw` promise (the actual NEP-141 `ft_transfer`) succeeded.

Because promises for different intents in the batch execute concurrently and independently (per the contract's own documented behavior), a failure of the underlying token transfer for entry `i` (e.g., insufficient balance/allowance, receiver account issues) does not cause `execute_intents` to fail as a whole — transfers `0` and `2` can succeed while `1` fails, yet the top-level tx is still "SETTLED" with a valid `tx.hash`. `DirectBridge.describeWithdrawal` has no logic to distinguish this and reports `completed` for every index unconditionally.

This contrasts with sibling bridges in the same file tree — `HotBridge.describeWithdrawal` (`hot-bridge.ts:375-404`) and `PoaBridge.describeWithdrawal` — which explicitly query per-withdrawal indexers/nonces/hashes before reporting completion, demonstrating the codebase's own established pattern for correctly verifying per-index outcomes that `DirectBridge` fails to follow.

Existing guards that do NOT prevent this: `validateAddress`, `compareAddresses`, storage-deposit checks in `estimateWithdrawalFee`/`validateWithdrawal`, and account-existence checks all run *before* execution and cannot detect execution-time promise failures (e.g., insufficient internal ledger balance for the token at execution time, or any other on-chain failure of the specific `ft_transfer` promise).

For `IntentsBridge`, the equality does NOT appear broken in the same way: its `transfer` intent (`intents-bridge.ts:41-51`) is a synchronous internal balance debit/credit inside `intents.near`, so an insufficient-balance condition there would panic the whole `execute_intents` function call before any promises are scheduled, meaning the transaction would fail to settle at all (no `tx.hash`/SETTLED status), not silently skip one transfer while reporting others as completed. The question's claim that IntentsBridge is equally vulnerable is not supported by the available evidence — I could not find contract-level evidence in this repo confirming partial-failure semantics for internal `transfer` intents specifically (as opposed to `ft_withdraw`'s external promises).

### Impact Explanation
For `DirectBridge`: an integrator using `describeWithdrawal`/`watchWithdrawal`/`waitForWithdrawalCompletion` for withdrawal index `i` in a batch would receive `{status: "completed", txHash: <NEAR settlement tx>}` even though the actual NEP-141 token transfer for that index failed and the receiver never got funds. This causes the integrator to mark the withdrawal as done/credited despite no funds delivered — a status/hash misreport that can cause the integrator to under-collateralize, double-pay, or otherwise mismanage funds, matching the "status or hash misreport making an integrator credit or refund twice" category (High), with a path toward Critical impact ("funds delivered... with no recovery" from the integrator's perspective, since they believe settlement occurred). This is repeatable for every batched withdrawal where one entry's promise fails.

### Likelihood Explanation
Preconditions: the attacker (an ordinary user with their own funds) crafts/receives a batch of NEP-141 `ft_withdraw` intents in a single signed `MultiPayload` where at least one entry is designed or happens to fail post-signing (e.g., insufficient internal balance for that specific asset at execution time, or a receiver-side issue causing the `ft_transfer` promise to fail). Given NEAR's documented independent/concurrent promise execution for intents batches, this requires no special access — an ordinary user calling `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` with a multi-item `withdrawalParams` array. The condition to trigger a per-entry failure without the contract reverting the whole call, however, depends on `intents.near`'s exact runtime behavior, which is outside this repo's direct control; the repo's own schema/comments corroborate the concurrent/independent-promise model but I could not directly inspect the deployed contract's Rust source to confirm exact revert semantics for all failure classes.

### Recommendation
For `DirectBridge.describeWithdrawal`, do not report `completed` based solely on `args.tx.hash` existing. Instead, fetch and inspect the NEAR transaction's receipts/outcomes for `args.tx.hash`, locate the specific promise/receipt corresponding to the `ft_withdraw`/`native_withdraw` intent at `args.index` (e.g., by matching the receiver_id/token/amount or by tracking receipt IDs returned by `execute_intents`), and only return `completed` if that specific transfer's outcome (`SuccessValue`/`SuccessReceiptId`) indicates success; otherwise return `failed` or `pending` as appropriate. Follow the same per-index verification pattern already used by `HotBridge`/`PoaBridge` in this codebase.

### Proof of Concept
```ts
// direct-bridge.describeWithdrawal.test.ts
import { describe, it, expect, vi } from "vitest";
import { DirectBridge } from "./direct-bridge";
import { configsByEnvironment } from "../../config"; // adjust import path as needed

describe("DirectBridge.describeWithdrawal - per-index execution truth", () => {
  it("BUG: reports completed for index 1 even though that ft_withdraw promise failed on-chain", async () => {
    const nearProvider = {
      // Mock provider whose tx_status/receipt outcome shows:
      // - intent 0 (ft_withdraw) succeeded
      // - intent 1 (ft_withdraw) failed (e.g. FunctionCallError from ft_transfer)
      // - intent 2 (ft_withdraw) succeeded
      sendJsonRpc: vi.fn(),
    } as any;

    const bridge = new DirectBridge({
      envConfig: configsByEnvironment.production,
      nearProvider,
    });

    const tx = { hash: "near-settlement-tx", accountId: "intents.near" };

    const wid = bridge.createWithdrawalIdentifier({
      withdrawalParams: {
        assetId: "nep141:usdt.tether-token.near",
        amount: 1000000n,
        destinationAddress: "receiver1.near",
      } as any,
      index: 1, // the failing sub-intent
      tx,
    });

    const result = await bridge.describeWithdrawal(wid);

    // ASSERT the broken equality:
    // Reported status ("completed") != actual execution outcome (failed) for index 1.
    expect(result).toEqual({ status: "completed", txHash: tx.hash }); // current (buggy) behavior
    // Desired/fixed behavior would instead assert:
    // expect(result).toEqual({ status: "failed", reason: expect.any(String) });
  });
});
```
Note: the current `DirectBridge.describeWithdrawal` implementation (`direct-bridge.ts:334-338`) never calls `nearProvider` at all, so the mock's return value is irrelevant to the outcome — this itself demonstrates the bug: `args.index` and any on-chain receipt data are completely unused. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L334-338)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier,
	): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: args.tx.hash };
	}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L37-51)
```typescript
	createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
	}): Promise<IntentPrimitive[]> {
		const intents: IntentPrimitive[] = [
			{
				intent: "transfer",
				receiver_id: args.withdrawalParams.destinationAddress,
				tokens: {
					[args.withdrawalParams.assetId]:
						args.withdrawalParams.amount.toString(),
				},
				memo: args.withdrawalParams.destinationMemo,
			},
		];
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L97-101)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier,
	): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: args.tx.hash };
	}
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts (L19-61)
```typescript
export function createWithdrawIntentPrimitive(params: {
	assetId: string;
	destinationAddress: string;
	amount: bigint;
	storageDeposit: bigint;
	msg: string | undefined;
	logger?: ILogger;
}): IntentFtWithdraw | IntentNativeWithdraw {
	if (
		params.assetId === NEAR_NATIVE_ASSET_ID &&
		// Ensure `msg` is not passed, because `native_withdraw` intent doesn't support `msg`
		params.msg === undefined
	) {
		return {
			intent: "native_withdraw",
			receiver_id: params.destinationAddress,
			amount: params.amount.toString(),
		};
	}

	const { contractId: tokenAccountId, standard } = utils.parseDefuseAssetId(
		params.assetId,
	);
	assert(standard === "nep141", "Only NEP-141 is supported");
	if (params.msg !== undefined) {
		params.logger?.warn(
			"min_gas is not set for direct-bridge withdrawal with msg, gas consumption is unpredictable",
		);
	}

	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: params.destinationAddress,
		amount: params.amount.toString(),
		storage_deposit:
			params.storageDeposit > 0n ? params.storageDeposit.toString() : undefined,
		msg: params.msg,
		// Only set min_gas when msg is not provided (simple ft_transfer).
		// When msg is present, ft_transfer_call is used and gas consumption is unpredictable.
		min_gas: params.msg == null ? MIN_GAS_AMOUNT : undefined,
	};
}
```

**File:** packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts (L73-92)
```typescript
	async waitForSettlement(
		ticket: IntentHash,
		ctx: { logger?: ILogger; signal?: AbortSignal } = {},
	): Promise<{ tx: NearTxInfo }> {
		const result = await solverRelay.waitForIntentSettlement({
			intentHash: ticket,
			signal: ctx.signal,
			baseURL: this.envConfig.solverRelayBaseURL,
			logger: ctx.logger,
			solverRelayApiKey: this.solverRelayApiKey,
		});
		return {
			tx: {
				hash: result.txHash,
				// Usually relayer's account id is the verifying contract (`intents.near`),
				// but it is not set in stone and may change in the future.
				accountId: this.envConfig.contractID,
			},
		};
	}
```

**File:** packages/contract-types/schemas/intents.schema.json (L4171-4180)
```json
										"type": "string"
									},
									"intents": {
										"description": "Sequence of intents to execute in given order. Empty list is also a valid sequence, i.e. it doesn't do anything, but still invalidates the `nonce` for the signer WARNING: Promises created by different intents are executed concurrently and does not rely on the order of the intents in this structure",
										"type": "array",
										"items": {
											"oneOf": [
												{
													"description": "See [`AddPublicKey`]",
													"type": "object",
```

**File:** packages/contract-types/artifacts/defuse_contract_abi.json (L4479-4494)
```json
        "NativeWithdraw": {
          "description": "Withdraw native tokens (NEAR) from the intents contract to a given external account id (external being outside of intents). This will subtract from the account's wNEAR balance, and will be sent to the account specified as native NEAR. NOTE: the `wNEAR` will not be refunded in case of fail (e.g. `receiver_id` account does not exist).",
          "type": "object",
          "required": [
            "amount",
            "receiver_id"
          ],
          "properties": {
            "amount": {
              "type": "string"
            },
            "receiver_id": {
              "description": "NEAR Account Identifier.\n\nThis is a unique, syntactically valid, human-readable account identifier on the NEAR network.\n\n[See the crate-level docs for information about validation.](index.html#account-id-rules)\n\nAlso see [Error kind precedence](AccountId#error-kind-precedence).\n\n## Examples\n\n``` use near_account_id::AccountId;\n\nlet alice: AccountId = \"alice.near\".parse().unwrap();\n\nassert!(\"ƒelicia.near\".parse::<AccountId>().is_err()); // (ƒ is not f) ```",
              "type": "string"
            }
          }
```

**File:** packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts (L375-404)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const cacheKey = this.getNoncesCacheKey(args.tx);
		const nonces = await this.noncesCache.fetch(cacheKey, { context: args.tx });
		if (nonces == null) {
			throw new HotWithdrawalNotFoundError(args.tx.hash, args.index);
		}

		const nonce = nonces[args.index];
		if (nonce == null) {
			throw new HotWithdrawalNotFoundError(args.tx.hash, args.index);
		}

		const status: unknown = await this.hotSdk.getGaslessWithdrawStatus(
			nonce.toString(),
		);
		// stop polling in case withdrawal is cancelled
		if (status === HotWithdrawStatus.Canceled) {
			return {
				status: "failed",
				reason: "Withdrawal was cancelled",
			};
		}

		const isEvm = args.landingChain.startsWith("eip155:");
		const isTon = args.landingChain === Chains.TON;
		// Bridge indexer is the source of truth for destination hashes on these chains.
		// TON does not fall back to HOT API hashes because they can refer to trace roots instead of CEX-visible transfers.
		if (isEvm || args.landingChain === Chains.Stellar || isTon) {
```
