### Title
`DirectBridge.describeWithdrawal` unconditionally reports "completed" without verifying the outcome of an `ft_transfer_call` triggered by a user‑supplied `msg` - ([File: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts])

### Summary
When a NEAR withdrawal is created with a non‑empty `routeConfig.msg`, `createWithdrawIntentPrimitive` builds an `ft_withdraw` intent that carries `msg` and deliberately omits `min_gas`, which makes `intents.near` execute the withdrawal as `ft_transfer_call` instead of a plain `ft_transfer`. `DirectBridge.describeWithdrawal` then returns `{ status: "completed", txHash: args.tx.hash }` unconditionally, based purely on the outer NEAR transaction hash succeeding, without ever inspecting whether the receiving contract's `ft_on_transfer` accepted or refunded the tokens.

### Finding Description
The broken equality is:

`amount actually credited to destinationAddress after settlement == args.withdrawalParams.amount`, which the SDK implicitly claims to be true whenever it reports `status: "completed"`.

Trace:
1. Caller uses `createNearWithdrawalRoute(msg)` with `msg = {"action":"deposit"}` and any NEP‑141 `assetId`, e.g. `nep141:eth.bridge.near`.
2. `DirectBridge.createWithdrawalIntents` (packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts, `createWithdrawalIntents`) forwards `routeConfig?.msg` into `createWithdrawIntentPrimitive`. [1](#0-0) 
3. `createWithdrawIntentPrimitive` builds the `ft_withdraw` intent with `msg: params.msg` set and `min_gas: params.msg == null ? MIN_GAS_AMOUNT : undefined` — i.e. `min_gas` is dropped whenever `msg` is present, and only a warning is logged. [2](#0-1) 
4. `intents.near`, when processing this `ft_withdraw` intent with a non‑empty `msg`, calls `ft_transfer_call` on the token contract targeting `receiver_id = destinationAddress`, which in turn invokes `destinationAddress`'s `ft_on_transfer`. Per NEP‑141 semantics, `ft_on_transfer` can return an "unused amount," causing the token contract's `resolve_transfer` callback to refund tokens back to the sender (`intents.near`) instead of leaving them with the recipient — fully or partially negating the withdrawal, even though the outer NEAR transaction still finalizes successfully.
5. `validateWithdrawal` only checks that `destinationAddress` passes `validateAddress`, does not equal the token contract (`compareAddresses`), and, for explicit accounts, exists on-chain — it performs no check on `msg` content, on gas sufficiency, or on the eventual settlement outcome of the `ft_transfer_call`. [3](#0-2) 
6. `DirectBridge.describeWithdrawal` is the single point where a completion status is reported to the caller/integrator, and it returns `completed` unconditionally, keyed only on the NEAR intent transaction hash, with no on-chain check of the actual token balance delta at `destinationAddress` or of `ft_on_transfer`'s return value: [4](#0-3) 
7. `watchWithdrawal` in the SDK's core polling loop treats `status === "completed"` as terminal success and returns the tx hash to the caller, propagating the misreport up through `IntentsSDK.processWithdrawal`. [5](#0-4) 

No existing guard (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()` ordering) inspects `msg` semantics, verifies `min_gas` sufficiency, or checks the eventual balance/refund outcome of the `ft_transfer_call`; they only validate the destination address string and account existence, which is orthogonal to whether the transfer actually lands.

### Impact Explanation
The SDK reports a withdrawal transaction hash and `completed` status to the integrator/caller even when the underlying `ft_transfer_call` results in a refund (tokens returned to `intents.near`) rather than delivery to `destinationAddress`. An integrator that credits an off-chain ledger or closes a withdrawal ticket based on this `completed` status will believe the user received `amount`, when in fact the tokens never reached the destination (or were only partially delivered), matching the High-severity category: "a status or hash misreport making an integrator credit or refund twice." This can be triggered per withdrawal call and is repeatable for any NEP‑141 asset whose destination contract's `ft_on_transfer` does not fully consume the transferred amount for the given `msg`.

### Likelihood Explanation
Preconditions: attacker (an ordinary SDK user) must supply a non-empty `msg` via `createNearWithdrawalRoute(msg)` and choose a `destinationAddress` that is a contract implementing `ft_on_transfer` for the given token (e.g. a bridge contract expecting a specific `msg` format such as `eth.bridge.near`). No privileged access or admin cooperation is needed; the entire path is reachable through public SDK entry points (`IntentsSDK.processWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`). It's fully feasible and repeatable, since the SDK provides no mechanism to opt out of this behavior or independently verify the transfer outcome.

### Recommendation
`DirectBridge.describeWithdrawal` should not report `completed` purely from the intent transaction succeeding when `msg` was used (`ft_transfer_call` path). It should additionally verify actual settlement — e.g., by inspecting the transaction's receipts/logs for the `ft_on_transfer`/`resolve_transfer` outcome or the resulting balance delta at `destinationAddress` — and report `failed`/`pending`/a distinct status when a refund occurred. At minimum, when `msg` is present, the SDK should surface a stronger warning or require the caller to explicitly acknowledge that outcome verification is not performed, rather than silently returning `completed`.

### Proof of Concept
Vitest plan (mocks only HTTP/NEAR RPC, no relayer/RPC trust changes):
1. Build withdrawal intents via `DirectBridge.createWithdrawalIntents` with `assetId = "nep141:eth.bridge.near"`, `destinationAddress = "some-contract.near"`, `routeConfig = createNearWithdrawalRoute('{"action":"deposit"}')`.
   - Assert the resulting `ft_withdraw` intent has `msg === '{"action":"deposit"}'` and `min_gas === undefined` (per `createWithdrawIntentPrimitive`).
2. Mock the NEAR RPC transaction result for the settled intent to include a receipt indicating `ft_on_transfer` returned the full `amount` as unused (simulating token-contract refund via `resolve_transfer`), so the effective balance credited to `destinationAddress` is `0`, not `amount`.
3. Call `DirectBridge.describeWithdrawal({ tx: { hash: "<intentTxHash>" }, ... })`.
   - Assert it returns `{ status: "completed", txHash: "<intentTxHash>" }` (current behavior) even though the mocked receipt shows `0` tokens delivered to `destinationAddress`.
4. Assert the equality break: `creditedAmount (0n) !== withdrawalParams.amount`, while `describeWithdrawal(...).status === "completed"`, demonstrating the SDK cannot distinguish a refunded transfer from a successful one.

### Citations

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L133-144)
```typescript
		const intent = createWithdrawIntentPrimitive({
			assetId: args.withdrawalParams.assetId,
			destinationAddress: args.withdrawalParams.destinationAddress,
			amount: args.withdrawalParams.amount,
			storageDeposit: getUnderlyingFee(
				args.feeEstimation,
				RouteEnum.NearWithdrawal,
				"storageDepositFee",
			),
			msg: args.withdrawalParams.routeConfig?.msg,
			logger: args.logger,
		});
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L154-192)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		if (validateAddress(args.destinationAddress, Chains.Near) === false) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				Chains.Near,
			);
		}

		const { contractId: tokenAccountId } = utils.parseDefuseAssetId(
			args.assetId,
		);

		if (
			compareAddresses(tokenAccountId, args.destinationAddress, Chains.Near)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenAccountId,
				args.assetId,
			);
		}

		// Only check account existence for explicit (named) accounts
		if (
			utils.isImplicitAccount(args.destinationAddress) === false &&
			(await this.getCachedAccountExistenceCheck(args.destinationAddress)) ===
				false
		) {
			throw new DestinationExplicitNearAccountDoesntExistError(
				args.destinationAddress,
			);
		}

		return;
	}
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L334-338)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier,
	): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: args.tx.hash };
	}
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts (L43-60)
```typescript
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
