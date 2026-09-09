Confirmed: `validateNearAddress` performs a pure regex/format check on the NEAR account-id syntax, with no RPC lookup and no check against `assetId`'s token contract or account existence/type.

### Title
Internal transfer route lets funds be sent to the token contract itself with immediate false "completed" status - (File: packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts)

### Summary
`IntentsBridge.validateWithdrawal` only checks that `destinationAddress` matches the NEAR account-id regex (`validateNearAddress`), with no check that the address differs from the token contract encoded in `assetId`, no existence check, and no check of account type. `createWithdrawalIntents` then emits a `transfer` intent with `receiver_id = destinationAddress` and `tokens: { [assetId]: amount }`, and `describeWithdrawal` unconditionally reports `{ status: "completed" }` without inspecting the on-chain outcome.

### Finding Description
The claimed equality is: `receiver_id` used in the signed `transfer` intent equals an account the user actually intends and controls, AND `status: "completed"` implies the transfer settled as intended on `intents.near`.

Trace:
- `createInternalTransferRoute()` sets `routeConfig.route = RouteEnum.InternalTransfer` [1](#0-0) , which makes `IntentsBridge.supports()` return true for this route [2](#0-1) .
- `validateWithdrawal` is the only gate before signing, and it does nothing but call `validateAddress(destinationAddress, Chains.Near)` [3](#0-2) .
- `validateAddress` for `Chains.Near` calls `utils.validateNearAddress`, which is a pure regex/length check on NEAR account-id syntax — no RPC call, no comparison to the token contract, no account-existence or account-kind check [4](#0-3) [5](#0-4) .
- `createWithdrawalIntents` builds the `transfer` intent directly from `destinationAddress` as `receiver_id` and `assetId` as the token key with no cross-check between the two [6](#0-5) .
- `describeWithdrawal` unconditionally returns `{ status: "completed", txHash: args.tx.hash }` without querying `intents.near` state for the receiver's balance or account type [7](#0-6) .

So if an attacker (or a confused integrator forwarding attacker-supplied `destinationAddress`) sets `destinationAddress = "doge.omft.near"` (the token contract itself) with `assetId = "nep141:doge.omft.near"`, `validateWithdrawal` passes (valid NEAR account-id syntax), `createWithdrawalIntents` emits `transfer { receiver_id: "doge.omft.near", tokens: { "nep141:doge.omft.near": amount } }`, and `describeWithdrawal` reports `completed` immediately. `processWithdrawal` orchestrates exactly this sequence: `signAndSendWithdrawalIntent` → `waitForIntentSettlement` → `waitForWithdrawalCompletion` (which calls `describeWithdrawal`) [8](#0-7) .

None of the existing guards catch this: `supports()` only checks route type, `compareAddresses`/`matchesRequest` and fee checks (`FeeExceedsAmountError`, `getUnderlyingFee`) are irrelevant to this route since fees are hardcoded to zero [9](#0-8) , and no assertion anywhere compares `receiver_id` against the contract id parsed from `assetId`.

### Impact Explanation
Balance held under `intents.near` for the withdrawing account is debited via a signed `transfer` intent to `receiver_id` equal to the fungible-token contract account itself. NEP-141 contracts are regular NEAR contracts that are not designed to hold or "own" balances registered to themselves inside `intents.near`; this is at minimum an operationally-wrong recipient the integrator did not intend, and the SDK reports `status: "completed"` immediately with no on-chain verification, so the integrator's system will treat the withdrawal as successfully settled to the intended recipient when in fact funds ended up parked at an account nobody (in the normal user flow) operates. This matches "withdrawal stuck/misrouted until manual intervention, status reported incorrectly" — High severity per the target's classification. It is repeatable per call since there is no on-chain or SDK-level restriction preventing this receiver every time this route is used.

### Likelihood Explanation
The precondition is simply calling `processWithdrawal` (or `createWithdrawalIntents`/`signAndSendWithdrawalIntent`) with `routeConfig: createInternalTransferRoute()` and a syntactically valid NEAR account id as `destinationAddress` — no special privileges, no RPC manipulation, and no reliance on a malicious relayer/RPC required. The only barrier is that the "attacker" role here is really the same party supplying `destinationAddress` to the SDK (the end user themselves, or a counterparty whose string an integrator blindly forwards, as explicitly allowed by the rules), so the cost is a single self-inflicted or forwarded string. This is feasible and repeatable at zero cost.

### Recommendation
In `IntentsBridge.validateWithdrawal`, parse `assetId` to extract the underlying token contract id and reject the withdrawal (or require explicit confirmation) when `destinationAddress` equals that contract id or other well-known non-user accounts (e.g., `intents.near` itself). Additionally, `describeWithdrawal` should not unconditionally report `completed`; it should verify on-chain (via the intents contract's `mt_balance_of`/`ft_balance_of`-style query for the receiver) that the transfer actually landed in a balance the recipient can use, or at least surface a warning when the receiver is a contract account rather than a typical user/named account.

### Proof of Concept
```ts
import { describe, it, expect } from "vitest";
import { IntentsBridge } from "./intents-bridge";
import { InvalidDestinationAddressForWithdrawalError } from "../../classes/errors";

describe("IntentsBridge internal transfer to token contract itself", () => {
  const bridge = new IntentsBridge();
  const assetId = "nep141:doge.omft.near";
  const destinationAddress = "doge.omft.near"; // == token contract from assetId
  const amount = 1000n;

  it("validateWithdrawal does NOT reject receiver == token contract", async () => {
    await expect(
      bridge.validateWithdrawal({ assetId, amount, destinationAddress })
    ).resolves.toBeUndefined(); // EXPECTED equality broken: no rejection
  });

  it("createWithdrawalIntents emits transfer to the token contract itself", async () => {
    const intents = await bridge.createWithdrawalIntents({
      withdrawalParams: { assetId, amount, destinationAddress, feeInclusive: false, routeConfig: { route: "internal_transfer" } } as any,
      feeEstimation: { amount: 0n, quote: null, underlyingFees: { internal_transfer: null } } as any,
    });

    expect(intents).toEqual([
      {
        intent: "transfer",
        receiver_id: destinationAddress, // == assetId's contract id — broken equality
        tokens: { [assetId]: amount.toString() },
        memo: undefined,
      },
    ]);
  });

  it("describeWithdrawal reports completed without any on-chain check", async () => {
    const status = await bridge.describeWithdrawal({
      landingChain: "near",
      index: 0,
      withdrawalParams: { assetId, amount, destinationAddress } as any,
      tx: { hash: "fake-hash", accountId: "user.near" },
    } as any);

    expect(status).toEqual({ status: "completed", txHash: "fake-hash" });
  });
});
```
Assertions on both sides of the equality: expected side — `validateWithdrawal` should throw `InvalidDestinationAddressForWithdrawalError` when `receiver_id === contractIdOf(assetId)`; actual side — it resolves normally, `createWithdrawalIntents` emits the transfer to that same contract id, and `describeWithdrawal` reports `completed` with no verification, confirming the divergence.

### Citations

**File:** packages/intents-sdk/src/lib/route-config-factory.ts (L12-14)
```typescript
export function createInternalTransferRoute(): InternalTransferRouteConfig {
	return { route: RouteEnum.InternalTransfer };
}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L24-31)
```typescript
	async supports(
		params: Pick<WithdrawalParams, "routeConfig">,
	): Promise<boolean> {
		if ("routeConfig" in params && params.routeConfig != null) {
			return this.is(params.routeConfig);
		}
		return false;
	}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L37-54)
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

		return Promise.resolve(intents);
	}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L59-72)
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
				"near-intents",
			);
		}
		return;
	}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L74-82)
```typescript
	async estimateWithdrawalFee(): Promise<FeeEstimation> {
		return {
			amount: 0n,
			quote: null,
			underlyingFees: {
				[RouteEnum.InternalTransfer]: null,
			},
		};
	}
```

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L97-101)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier,
	): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: args.tx.hash };
	}
```

**File:** packages/intents-sdk/src/lib/validateAddress.ts (L26-30)
```typescript
export function validateAddress(address: string, blockchain: Chain): boolean {
	switch (blockchain) {
		case Chains.Near:
			return utils.validateNearAddress(address);

```

**File:** packages/internal-utils/src/utils/near.ts (L85-96)
```typescript
export function validateNearAddress(accountId: string): boolean {
	if (
		accountId.length < MIN_ACCOUNT_ID_LENGTH ||
		accountId.length > NEAR_IMPLICIT_ACCOUNT_LENGTH
	) {
		return false;
	}
	if (isImplicitAccount(accountId)) {
		return true;
	}
	return ACCOUNT_ID_REGEX.test(accountId);
}
```

**File:** packages/intents-sdk/src/sdk.ts (L814-838)
```typescript
		// Step 2: Sign and send intent
		const { intentHash } = await this.signAndSendWithdrawalIntent({
			withdrawalParams,
			feeEstimation,
			referral: args.referral,
			intent: args.intent,
			logger: args.logger,
		});

		args.logger?.info("Intent published", { intentHash });

		// Step 3: Wait for intent settlement
		const intentTx = await this.waitForIntentSettlement({
			intentHash: intentHash,
			logger: args.logger,
		});

		args.logger?.info("Intent settled", { txHash: intentTx.hash });

		// Step 4: Wait for withdrawal completion
		const destinationTx = await this.waitForWithdrawalCompletion({
			withdrawalParams,
			intentTx,
			logger: args.logger,
		});
```
