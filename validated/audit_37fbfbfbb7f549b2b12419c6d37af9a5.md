### Title
Missing `FeeExceedsAmountError` guard in `createWithdrawalIntents` allows negative `actualAmount` when called with a stale/mismatched `feeEstimation` - (File: `packages/intents-sdk/src/sdk.ts`)

### Summary
`_estimateWithdrawalFee` enforces `withdrawalParams.amount > fee.amount` before computing `actualAmount = amount - fee.amount` when `feeInclusive` is true, but `createWithdrawalIntents` recomputes the identical subtraction without repeating that check. Since `createWithdrawalIntents` is a public method that accepts an independently supplied `feeEstimation` object, a caller can invoke it directly with a `withdrawalParams.amount` smaller than `feeEstimation.amount`, producing a negative `actualAmount` bigint that is forwarded into `bridge.validateWithdrawal` and `bridge.createWithdrawalIntents`.

### Finding Description
The broken equality is: `_estimateWithdrawalFee` guarantees `withdrawalParams.amount > feeEstimation.amount` whenever `feeInclusive === true` (enforced at [1](#0-0) ), but `createWithdrawalIntents` assumes this invariant holds for *any* `feeEstimation` object passed to it without re-validating it ( [2](#0-1) ).

`createWithdrawalIntents` is a public SDK method whose signature takes `withdrawalParams` and `feeEstimation` as two independent, caller-supplied arguments — there is nothing tying `feeEstimation` to have been produced by `estimateWithdrawalFee` for that exact `withdrawalParams.amount`. An attacker (an integrator or a caller with access to the SDK instance) can:
1. Call `estimateWithdrawalFee` once with a large `amount` to obtain a valid `feeEstimation`.
2. Call `createWithdrawalIntents` directly with `feeInclusive: true` and a much smaller `withdrawalParams.amount` (less than `feeEstimation.amount`), reusing the previously obtained `feeEstimation`.
3. `actualAmount = args.withdrawalParams.amount - args.feeEstimation.amount` evaluates to a negative bigint at [3](#0-2) , with no `FeeExceedsAmountError` thrown, since that check only exists in `_estimateWithdrawalFee` ( [1](#0-0) ).
4. This negative `actualAmount` is then passed to `bridge.validateWithdrawal` and `bridge.createWithdrawalIntents` ( [4](#0-3) ) as the amount for the signed `ft_withdraw` intent.

Whether this ultimately gets blocked depends entirely on whatever amount-positivity checks exist inside each bridge's `validateWithdrawal` implementation (poa-bridge, omni-bridge, direct-bridge, intents-bridge, hot-bridge, aurora-engine-bridge) — I was not able to fully inspect the bodies of these `validateWithdrawal` implementations within the available context to confirm they uniformly reject non-positive amounts before intent construction. Regardless, the explicit, purpose-built safety net (`FeeExceedsAmountError`) that the codebase itself defines for exactly this scenario is architecturally absent from the `createWithdrawalIntents` code path, meaning protection against this input is not guaranteed by the SDK layer itself but delegated inconsistently to bridge-specific validation logic.

### Impact Explanation
If a bridge's `validateWithdrawal` does not itself reject non-positive/negative amounts, a negative or unexpectedly small `actualAmount` would be used to build and sign an `ft_withdraw` intent, breaking amount conservation between what the user authorized and what gets embedded in the signed payload — a Critical-severity fee/amount computation error per the rubric ("a fee error draining a material share of the amount").

### Likelihood Explanation
Preconditions: the caller must invoke `createWithdrawalIntents` directly (bypassing `estimateWithdrawalFee`'s guard) with `feeInclusive: true` and a `feeEstimation` object whose `amount` exceeds the newly supplied `withdrawalParams.amount`. This is fully within reach of any caller with SDK access since `feeEstimation` and `withdrawalParams` are independent, unlinked arguments to a public method. The attacker cost is a single extra estimate call plus a `createWithdrawalIntents` call — cheap and repeatable. Actual exploitability depends on whether the selected bridge's `validateWithdrawal` independently blocks the negative amount, which could not be fully confirmed from the available code.

### Recommendation
Re-validate the `feeInclusive` fee-vs-amount invariant inside `createWithdrawalIntents` itself (mirroring the check at `sdk.ts:421-424`) before computing `actualAmount`, rather than relying solely on `_estimateWithdrawalFee` or bridge-specific downstream validation.

### Proof of Concept
```ts
// vitest, mocking only HTTP calls made by the bridge's estimateWithdrawalFee
it("createWithdrawalIntents does not reject amount < feeEstimation.amount", async () => {
  const feeEstimation = await sdk.estimateWithdrawalFee({
    withdrawalParams: { ...baseParams, amount: 1_000_000n, feeInclusive: true },
  });
  expect(feeEstimation.amount).toBeGreaterThan(0n);

  // Reuse feeEstimation with a much smaller amount, bypassing estimateWithdrawalFee's guard
  const smallAmount = feeEstimation.amount - 1n; // amount <= fee.amount
  await expect(
    sdk.createWithdrawalIntents({
      withdrawalParams: { ...baseParams, amount: smallAmount, feeInclusive: true },
      feeEstimation,
    }),
  ).resolves.not.toThrow(); // FeeExceedsAmountError is never thrown here

  // Inspect resulting intent for negative/underflowed amount field
});
```
Assertion of the broken equality: before the call, `estimateWithdrawalFee` enforces `withdrawalParams.amount > feeEstimation.amount`; after calling `createWithdrawalIntents` directly with a stale `feeEstimation`, `withdrawalParams.amount <= feeEstimation.amount` holds and no equivalent guard fires, so `actualAmount = amount - feeEstimation.amount` is non-positive, contradicting the invariant `_estimateWithdrawalFee` was designed to enforce.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L334-344)
```typescript
	public async createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
		logger?: ILogger;
	}): Promise<IntentPrimitive[]> {
		for (const bridge of this.bridges) {
			if (await bridge.supports(args.withdrawalParams)) {
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

**File:** packages/intents-sdk/src/sdk.ts (L421-424)
```typescript
				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
```
