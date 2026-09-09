### Title
Missing `actualAmount >= 0` guard in `IntentsSDK.createWithdrawalIntents` allows negative `amount` in signed `ft_withdraw` intent - ([File: packages/intents-sdk/src/sdk.ts])

### Summary
`IntentsSDK.createWithdrawalIntents` computes `actualAmount = withdrawalParams.amount - feeEstimation.amount` when `feeInclusive` is true, but unlike its sibling `_estimateWithdrawalFee`, it never checks that this result is non-negative before handing it to `bridge.validateWithdrawal` / `bridge.createWithdrawalIntents`. For bridges whose `validateWithdrawal` doesn't independently reject non-positive amounts (`DirectBridge`, `AuroraEngineBridge`), a negative `actualAmount` flows straight into `createWithdrawIntentPrimitive`, producing an `ft_withdraw` intent with `amount: "-400"`.

### Finding Description
The broken equality is: `debits == withdrawalParams.amount - feeEstimation.amount`, which must hold `>= 0` for a withdrawal intent to make sense.

- `_estimateWithdrawalFee` ( [1](#0-0) ) explicitly checks `args.withdrawalParams.amount <= fee.amount` and throws `FeeExceedsAmountError` before computing `actualAmount`.
- `createWithdrawalIntents` ( [2](#0-1) ) performs the identical subtraction (`args.withdrawalParams.amount - args.feeEstimation.amount`) but has **no equivalent guard** — it passes `actualAmount` straight to `bridge.validateWithdrawal` and then to `bridge.createWithdrawalIntents` regardless of sign.
- Whether the negative value survives depends on the selected bridge's `validateWithdrawal`:
  - `PoaBridge.validateWithdrawal` ( [3](#0-2) ) checks `args.amount < minWithdrawalAmount`, which would normally catch a negative amount (assuming a positive minimum) — this guard is incidental, not intentional.
  - `DirectBridge.validateWithdrawal` ( [4](#0-3) ) only checks the destination address and account existence — **no amount check at all**.
  - `AuroraEngineBridge.validateWithdrawal` ( [5](#0-4) ) also only validates the destination address — **no amount check**.
- `DirectBridge.createWithdrawalIntents` ( [6](#0-5) ) forwards `args.withdrawalParams.amount` unchanged into `createWithdrawIntentPrimitive`, which does `amount: params.amount.toString()` ( [7](#0-6) ) — a negative BigInt serializes to a string like `"-400"` with no validation anywhere in this path.

Root cause: the equality guard (`amount > feeEstimation.amount`) that exists in the "estimate" path was not duplicated in the "create intents" path, even though both compute the same `feeInclusive` subtraction. Any caller (an ordinary SDK user/integrator) who invokes `createWithdrawalIntents` directly — supplying their own `feeEstimation` object rather than chaining the output of `estimateWithdrawalFee` — bypasses the only place this equality is checked.

### Impact Explanation
For a DirectBridge/AuroraEngineBridge-routed withdrawal, calling `createWithdrawalIntents` with `feeInclusive: true` and a `feeEstimation.amount` greater than `withdrawalParams.amount` produces an `ft_withdraw` intent primitive whose `amount` field is a negative numeric string. This is a value that would ultimately be embedded in a `MultiPayload` for the caller to sign. A negative `amount` in an `ft_withdraw` intent is semantically undefined/invalid input to `intents.near`; at minimum it produces a corrupted, invalid signed intent carrying the user's signature over a value they never intended (their entered amount minus an oversized fee, going negative), and at worst risks unexpected interpretation by the receiving contract if it does not itself reject negative strings. This matches the Critical category ("a signature ... executed... over an unintended value") only insofar as the SDK itself fails to prevent constructing and signing such a malformed intent — the ultimate on-chain interpretation is outside this repo's control (`intents.near` is out of scope per the rules), but the SDK's failure to enforce its own invariant is squarely in scope.

### Likelihood Explanation
- Preconditions: the withdrawal route must resolve to `DirectBridge` (NEAR withdrawal) or `AuroraEngineBridge` (virtual-chain withdrawal) — both lack any amount-positivity check in `validateWithdrawal`.
- The caller must invoke `createWithdrawalIntents` directly with a self-supplied `feeEstimation` whose `amount` exceeds `withdrawalParams.amount`, rather than using the standard chained flow (`estimateWithdrawalFee` → `createWithdrawalIntents`), which does perform the `FeeExceedsAmountError` check upstream.
- No RPC/API calls are needed to trigger it for `DirectBridge`/`AuroraEngineBridge` since their `createWithdrawalIntents`/`validateWithdrawal` are synchronous and don't fetch external fee data beyond address checks — cost to the caller is a single local SDK call.
- This is fully repeatable and deterministic every time these preconditions are met.

### Recommendation
Add the same guard used in `_estimateWithdrawalFee` to `createWithdrawalIntents` in `packages/intents-sdk/src/sdk.ts`: before computing `actualAmount`, if `args.withdrawalParams.feeInclusive` and `args.withdrawalParams.amount <= args.feeEstimation.amount`, throw `FeeExceedsAmountError`. Additionally, add a defensive `assert(actualAmount >= 0n, ...)` immediately after computing `actualAmount` in `createWithdrawalIntents`, and consider adding an explicit amount-positivity check inside `DirectBridge.validateWithdrawal` and `AuroraEngineBridge.validateWithdrawal` as defense in depth.

### Proof of Concept
```ts
// packages/intents-sdk/src/sdk.negative-amount.test.ts
import { describe, it, expect } from "vitest";
import { IntentsSDK } from "./sdk";
import { noopIntentSigner } from "./intents/intent-signer-impl/intent-signer-noop";
import { createNearWithdrawalRoute } from "./test-helpers"; // or equivalent RouteConfig helper

describe("createWithdrawalIntents negative amount", () => {
  it("produces negative amount string when feeEstimation.amount > withdrawalParams.amount, bypassing estimateWithdrawalFee", async () => {
    const sdk = new IntentsSDK({ referral: "", intentSigner: noopIntentSigner });

    // Equality being validated: actualAmount = amount - feeEstimation.amount
    // amount = 100n, feeEstimation.amount = 500n => actualAmount should be rejected (>= 0 required)
    const intents = sdk.createWithdrawalIntents({
      withdrawalParams: {
        assetId: "nep141:usdt.tether-token.near",
        amount: 100n,
        destinationAddress: "alice.near",
        feeInclusive: true,
        routeConfig: createNearWithdrawalRoute(),
      },
      feeEstimation: {
        amount: 500n,
        quote: null,
        underlyingFees: { /* NearWithdrawal: { storageDepositFee: 0n } */ },
      },
    });

    // BROKEN: no FeeExceedsAmountError is thrown, amount ends up negative
    await expect(intents).resolves.toEqual([
      expect.objectContaining({
        intent: "ft_withdraw",
        amount: "-400", // 100 - 500
      }),
    ]);
  });
});
```
Assert both sides of the equality: `withdrawalParams.amount (100n) - feeEstimation.amount (500n) = -400n`, which is `< 0`, yet no `FeeExceedsAmountError` (or any error) is thrown by `createWithdrawalIntents`, and the resulting intent's `amount` field is the literal negative string `"-400"`.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L334-364)
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
			}
```

**File:** packages/intents-sdk/src/sdk.ts (L421-428)
```typescript
				if (args.withdrawalParams.feeInclusive) {
					if (args.withdrawalParams.amount <= fee.amount) {
						throw new FeeExceedsAmountError(fee, args.withdrawalParams.amount);
					}
				}
				const actualAmount = args.withdrawalParams.feeInclusive
					? args.withdrawalParams.amount - fee.amount
					: args.withdrawalParams.amount;
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L221-230)
```typescript
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

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L110-149)
```typescript
	createWithdrawalIntents(args: {
		withdrawalParams: WithdrawalParams;
		feeEstimation: FeeEstimation;
		referral?: string;
		logger?: ILogger;
	}): Promise<IntentPrimitive[]> {
		withdrawalParamsInvariant(args.withdrawalParams);

		const intents: IntentPrimitive[] = [];

		if (args.feeEstimation.quote != null) {
			intents.push({
				intent: "token_diff",
				diff: {
					[args.feeEstimation.quote.defuse_asset_identifier_in]:
						`-${args.feeEstimation.quote.amount_in}`,
					[args.feeEstimation.quote.defuse_asset_identifier_out]:
						args.feeEstimation.quote.amount_out,
				},
				referral: args.referral,
			});
		}

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

		intents.push(intent);

		return Promise.resolve(intents);
	}
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

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L128-142)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
	}): Promise<void> {
		if (validateAddress(args.destinationAddress, Chains.Ethereum) === false) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				"virtual-chain",
			);
		}

		return;
	}
```

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts (L49-56)
```typescript
	return {
		intent: "ft_withdraw",
		token: tokenAccountId,
		receiver_id: params.destinationAddress,
		amount: params.amount.toString(),
		storage_deposit:
			params.storageDeposit > 0n ? params.storageDeposit.toString() : undefined,
		msg: params.msg,
```
