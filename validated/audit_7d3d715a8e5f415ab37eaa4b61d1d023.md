Confirmed: `amount.toString()` at [1](#0-0)  serialises whatever bigint it receives, including a negative value, directly into the `ft_withdraw` intent's `amount` field with no sign check.

### Title
`createWithdrawalIntents` skips the `FeeExceedsAmountError` guard, allowing negative/zero `ft_withdraw` amounts for OmniBridge withdrawals - (File: packages/intents-sdk/src/sdk.ts)

### Summary
`IntentsSDK.createWithdrawalIntents` (invoked by `signAndSendWithdrawalIntent` when a caller supplies its own `feeEstimation`) computes `actualAmount = amount - feeEstimation.amount` for `feeInclusive: true` withdrawals without ever checking `amount > feeEstimation.amount`, unlike its sibling `_estimateWithdrawalFee` which throws `FeeExceedsAmountError` in that case. This lets a caller-supplied `feeEstimation` with `amount` ≤ `feeEstimation.amount` produce a negative/zero `actualAmount` that gets propagated into `OmniBridge.createWithdrawalIntents`.

### Finding Description
The claimed equality is: `sum(debits in produced intents) == amount + (feeInclusive ? 0 : fee)`, with the destination receiving a non-negative amount.

In `sdk.ts`:
- `_estimateWithdrawalFee` guards this at [2](#0-1) : if `feeInclusive` and `amount <= fee.amount`, it throws `FeeExceedsAmountError` before any amount is used.
- `createWithdrawalIntents`, however, computes `actualAmount` the same way but **without** this guard: [3](#0-2) . Since `signAndSendWithdrawalIntent` accepts a caller-supplied `feeEstimation` and routes straight into `createWithdrawalIntents` (bypassing `_estimateWithdrawalFee`) as shown at [4](#0-3) , an attacker can supply `amount = 100`, `feeInclusive = true`, and `feeEstimation.amount = 1000`, yielding `actualAmount = -900n`.

This negative `actualAmount` is passed to `bridge.validateWithdrawal` and `bridge.createWithdrawalIntents` at [5](#0-4) .

In `omni-bridge.ts`, `validateWithdrawal` calls the external `verifyTransferAmount(args.amount, 0n, decimals...)` at [6](#0-5) . `verifyTransferAmount` and `getMinimumTransferableAmount` are external functions from `@omni-bridge/core`, not implemented in this repo, so their exact behavior on negative inputs cannot be verified from this codebase. If they perform a comparison such as `amount >= minAmount` on the raw bigint, a large negative number would fail this check and correctly throw `MinWithdrawalAmountError` — closing the exploit. However, if the underlying library only checks divisibility/remainder in the normalisation logic without an explicit sign/positivity assertion, a negative amount could slip through. Similarly, for UTXO chains the min-amount check compares `args.amount + utxoMaxGasFee + utxoProtocolFee < minAmount` at [7](#0-6) , which for a very negative `args.amount` would still correctly throw (since the sum would be even more negative and less than `minAmount`), so UTXO chains are unlikely to be exploitable this way.

If `validateWithdrawal` does not reject it, `OmniBridge.createWithdrawalIntents` passes the negative `actualAmount` straight through `deriveOmniWithdrawIntentParams` (as `amount`) into `createWithdrawIntentsPrimitive`, which serialises it as `amount.toString()` (e.g., `"-900"`) into the `ft_withdraw` intent with no sign validation at [8](#0-7) .

### Impact Explanation
I cannot confirm from this repository alone whether the `intents.near` contract or `@omni-bridge/core`'s `verifyTransferAmount` would accept a negative `ft_withdraw` amount string, since that logic lives outside this repo (in the `@omni-bridge/core` package and the on-chain `intents.near`/OmniBridge contracts). The SDK-side guard (`FeeExceedsAmountError`) that would deterministically prevent this is present in `_estimateWithdrawalFee` but is missing in `createWithdrawalIntents`, which is a real code-path inconsistency: a caller-supplied `feeEstimation` (an explicitly attacker-controllable input per the entrypoint definition) reaches `createWithdrawalIntents` without ever passing through the `FeeExceedsAmountError` check.

### Likelihood Explanation
Preconditions: attacker must call `signAndSendWithdrawalIntent` directly with a self-supplied `feeEstimation` object (skipping `estimateWithdrawalFee`), with `amount <= feeEstimation.amount` and `feeInclusive: true`. This is an explicitly documented/supported code path (`feeEstimation` is a public parameter of `signAndSendWithdrawalIntent`), not a misuse of an undocumented escape hatch. Whether it results in an actually signable, harmful intent depends entirely on whether `verifyTransferAmount` (external to this repo) or the on-chain `intents.near`/OmniBridge contract validates `amount > 0` on the `ft_withdraw` intent — behavior this repo's index does not contain and I could not verify.

### Recommendation
Add the same `FeeExceedsAmountError` guard used in `_estimateWithdrawalFee` to `createWithdrawalIntents` in `packages/intents-sdk/src/sdk.ts`: before computing `actualAmount`, assert `args.withdrawalParams.amount > args.feeEstimation.amount` when `feeInclusive` is true, and throw `FeeExceedsAmountError` otherwise. Additionally, add an explicit `assert(actualAmount > 0n, ...)` immediately after computing `actualAmount` regardless of `feeInclusive`, so a negative/zero amount can never reach `bridge.validateWithdrawal` or `bridge.createWithdrawalIntents`.

### Proof of Concept
Vitest plan (mocks HTTP only, per rules):
1. Construct a caller-supplied `feeEstimation` mock for `nep141:aptos.omft.near` (OmniBridge, non-UTXO chain) with `amount: 1000n`, `quote: null`, `underlyingFees: { [RouteEnum.OmniBridge]: { relayerFee: 1000n, storageDepositFee: 0n } }`.
2. Call `sdk.signAndSendWithdrawalIntent({ withdrawalParams: { assetId: "nep141:aptos.omft.near", amount: 100n, feeInclusive: true, destinationAddress: <valid aptos address> }, feeEstimation, intent: { signer: <noop/mock signer that records intents> } })`.
3. Assert whether the call throws before signing (expected/desired behavior) — currently it does NOT throw at the SDK level for this specific arithmetic step (only `omni-bridge.ts`'s internal `verifyTransferAmount`/min-amount checks might reject it, which cannot be confirmed from this repo).
4. If it does not throw, intercept the built `IntentPrimitive[]` before signing and assert: `ft_withdraw.amount` parsed as BigInt is `< 0n` or `<= 0n`, violating `sum(debits) == amount + fee` and the non-negativity invariant.
5. Compare against expected: the call should throw `FeeExceedsAmountError` identically to what `_estimateWithdrawalFee` would do for the same inputs — assert `sdk.estimateWithdrawalFee({ withdrawalParams: { ...same, amount: 100n } })` throws `FeeExceedsAmountError` while `signAndSendWithdrawalIntent` with the same numeric inputs does not, demonstrating the guard asymmetry.

Because the ultimate on-chain/library-level rejection point (`verifyTransferAmount` in `@omni-bridge/core`) is outside this repo's indexed contents, I cannot state with certainty whether the negative amount is currently blocked before signing or not — this should be verified with a live/mocked run of the actual `@omni-bridge/core` dependency, which requires a full Devin session rather than static analysis.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge-utils.ts (L64-73)
```typescript
	intents.push({
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: OMNI_BRIDGE_CONTRACT,
		amount: amount.toString(),
		storage_deposit:
			storageDepositAmount > 0n ? storageDepositAmount.toString() : undefined,
		msg: JSON.stringify(ftWithdrawPayload),
		min_gas: MIN_GAS_AMOUNT,
	});
```

**File:** packages/intents-sdk/src/sdk.ts (L342-344)
```typescript
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - args.feeEstimation.amount
					: args.withdrawalParams.amount;
```

**File:** packages/intents-sdk/src/sdk.ts (L346-363)
```typescript
				await bridge.validateWithdrawal({
					assetId: args.withdrawalParams.assetId,
					amount: actualAmount,
					destinationAddress: args.withdrawalParams.destinationAddress,
					destinationMemo: args.withdrawalParams.destinationMemo,
					feeEstimation: args.feeEstimation,
					routeConfig: args.withdrawalParams.routeConfig,
					logger: args.logger,
				});

				return bridge.createWithdrawalIntents({
					withdrawalParams: {
						...args.withdrawalParams,
						amount: actualAmount,
					},
					feeEstimation: args.feeEstimation,
					referral: args.referral ?? this.referral,
				});
```

**File:** packages/intents-sdk/src/sdk.ts (L421-425)
```typescript
				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
				}
```

**File:** packages/intents-sdk/src/sdk.ts (L704-713)
```typescript
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L405-425)
```typescript
		if (!args.skipMinAmountValidation) {
			// verifyTransferAmount ensures (amount - fee) > 0 after normalisation.
			// We pass the actual amount and a zero fee to avoid fee-handling differences
			// between different withdrawal types (UTXO transfers vs regular transfers where the fee is paid in wrap.near).
			const normalisationCheckSucceeded = verifyTransferAmount(
				args.amount, // total amount without fee
				0n, // fee
				decimals.origin_decimals,
				decimals.decimals,
			);
			if (normalisationCheckSucceeded === false) {
				const minAmount = getMinimumTransferableAmount(
					decimals.origin_decimals,
					decimals.decimals,
				);
				throw new MinWithdrawalAmountError(
					minAmount,
					args.amount,
					args.assetId,
				);
			}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L508-519)
```typescript
			if (!args.skipMinAmountValidation) {
				// args.amount is without fee, we need to pass an amount with fee
				const actualAmountWithFee =
					args.amount + utxoMaxGasFee + utxoProtocolFee;
				if (actualAmountWithFee < minAmount) {
					throw new MinWithdrawalAmountError(
						minAmount,
						actualAmountWithFee,
						args.assetId,
					);
				}
			}
```
