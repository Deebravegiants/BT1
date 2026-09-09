### Title
`DirectBridge.describeWithdrawal` unconditionally reports `completed` even when `ft_transfer_call` refunds the withdrawn tokens - (File: `packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts`)

### Summary
When `createNearWithdrawalRoute(msg)` is used with a non-empty `msg`, `DirectBridge.createWithdrawIntentPrimitive` builds an `ft_withdraw` intent that intents.near executes as `ft_transfer_call` to `destinationAddress`, with `min_gas` intentionally left `undefined`. `DirectBridge.describeWithdrawal` then reports `{ status: "completed", txHash: args.tx.hash }` purely based on the NEAR intents transaction succeeding, without inspecting whether the destination contract's `ft_on_transfer` accepted the full amount or refunded some/all of it back to `intents.near` via the standard NEP-141 `ft_resolve_transfer` mechanism.

### Finding Description
The broken equality: the SDK's reported outcome ("tokens delivered to `destinationAddress`, amount == withdrawal amount") must equal the actual on-chain post-state ("`destinationAddress`'s token balance increased by `amount`"). This equality can diverge.

Code path:
- `createWithdrawIntentPrimitive` in `packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts` (lines 43-60): when `params.msg !== undefined`, it emits `ft_withdraw` with `receiver_id: destinationAddress`, `msg: params.msg`, and `min_gas: undefined` (only warns via logger about unpredictable gas). This causes intents.near to perform NEP-141 `ft_transfer_call` instead of a plain `ft_transfer`. [1](#0-0) 
- `DirectBridge.createWithdrawalIntents` in `direct-bridge.ts` passes `args.withdrawalParams.routeConfig?.msg` straight through with no validation of its size or content. [2](#0-1) 
- `DirectBridge.validateWithdrawal` only checks that the destination address is a valid NEAR address, is not the token contract itself, and (for explicit accounts) exists on-chain. It does not check `msg` content, does not verify the destination contract implements `ft_on_transfer` sensibly, and does not check post-settlement balances. [3](#0-2) 
- `DirectBridge.describeWithdrawal` unconditionally returns `completed` with the intents.near transaction hash, with no check of the actual token transfer outcome (e.g., no query of `ft_resolve_transfer` receipt, no balance diff, no distinguishing between full transfer, partial refund, or full refund). [4](#0-3) 

Root cause: per NEP-141, when `ft_transfer_call` is used and the receiving contract's `ft_on_transfer` returns any "unused amount" (including the full amount, e.g., if the receiver rejects/redirects because it can't parse the 2 KB JSON `msg` or intentionally chooses to refund), the NEP-141 token contract's `ft_resolve_transfer` callback returns that unused amount back to the **predecessor** of the call, which is `intents.near`, not to the original off-ramping user. The tokens never end up credited to `destinationAddress`'s external balance as the withdrawal intended, yet the SDK reports `completed` and gives back the intents.near tx hash as proof of settlement.

Why existing guards fail:
- `validateWithdrawal` never simulates or inspects the receiving contract's `ft_on_transfer` behavior; it only checks address existence, which is unrelated to whether a `ft_transfer_call` will succeed as a "real" transfer.
- `describeWithdrawal` does no post-hoc verification of the destination account's token balance delta or of receipts from `ft_resolve_transfer`; it is a hard-coded return statement.
- `min_gas` is intentionally omitted (only logged as a warning) when `msg` is present, per the comment "gas consumption is unpredictable" — this is a known limitation acknowledged in code comments but not compensated for by any settlement-verification logic.

### Impact Explanation
An unprivileged caller (an ordinary user withdrawing their own funds via `createNearWithdrawalRoute(msg)`, or a counterparty whose `msg`/`destinationAddress` are forwarded by an integrator) can cause the SDK to report a Direct withdrawal as `completed` with a real transaction hash while the token amount was actually refunded to `intents.near` instead of being credited to `destinationAddress`. This is a status/hash misreport: an integrator that trusts `describeWithdrawal`'s `completed` status to reconcile off-chain ledgers (e.g., credit a customer, or release counter-value on another rail) could credit funds that never reached the destination, or a counterparty could induce a false "completed" while designing `msg` to always trigger a refund path, enabling a credit/refund double-count. This matches the "High" impact category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
- Preconditions: only requires calling the public SDK with `createNearWithdrawalRoute(msg)` where `msg` is non-empty (any string, including a 2 KB JSON blob) and a `destinationAddress` that is any deployed NEP-141-adjacent NEAR contract account that exists (satisfying `validateWithdrawal`'s existence check) but whose `ft_on_transfer` rejects/refunds the transfer (e.g., a contract that doesn't recognize the msg format, has an unrelated `ft_on_transfer` implementation, or intentionally refunds).
- Attacker cost: one on-chain transaction; fully repeatable per withdrawal.
- Feasibility: does not require any privileged access, malicious relayer, or admin — solely relies on the caller-supplied `msg` and `destinationAddress`, both explicitly described as attacker-controlled inputs in this question.

### Recommendation
- In `describeWithdrawal`, when `msg` was present in the original withdrawal intent (i.e., an `ft_transfer_call` was used), verify actual settlement by inspecting the transaction's receipts for a corresponding `ft_resolve_transfer` outcome (or an equivalent balance check on `destinationAddress`), and only report `completed` when the full `amount` was retained by the destination account (i.e., `ft_on_transfer` did not return any unused amount).
- Alternatively, disallow attaching `msg` to Direct/NEAR withdrawals altogether unless the SDK can positively confirm final settlement, or expose a distinct status (e.g., `"refunded"`/`"partial"`) instead of overloading `completed`.
- Add `min_gas` for `ft_transfer_call` paths, sized to guarantee `ft_on_transfer`/`ft_resolve_transfer` execute deterministically, reducing unpredictable partial-refund scenarios.

### Proof of Concept
Vitest test plan:
1. Unit test on `createWithdrawIntentPrimitive` (`direct-bridge-utils.test.ts`): assert that for `assetId: "nep141:usdt.tether-token.near"`, `msg: <2KB JSON string>`, the resulting intent has `intent: "ft_withdraw"`, `receiver_id: destinationAddress`, `msg` equal to the input, and `min_gas` is `undefined` — confirming the SDK builds an unguarded `ft_transfer_call`.
2. Integration-style test on `DirectBridge.describeWithdrawal`: construct a `WithdrawalIdentifier` with `tx: { hash: "near-tx-hash", accountId: "..." }` and assert the returned value is always `{ status: "completed", txHash: "near-tx-hash" }` regardless of any mocked receipt data indicating a refund — demonstrating that no code path in `describeWithdrawal` can produce anything other than `completed`, i.e., assert the equality "reported completed txHash == real destination balance credited" cannot be evaluated or falsified by the current implementation because it performs zero on-chain outcome verification.
3. (For full end-to-end validation, mock the NEAR RPC transaction receipts to show a `ft_resolve_transfer` refund back to `intents.near` and show that `describeWithdrawal`'s output does not change, which is the crux of the finding — this part requires mocking only the NEAR RPC/HTTP, consistent with the "mocks only HTTP" requirement.)

### Citations

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
