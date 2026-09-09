### Title
Internal transfer to `intents.near` (or any unchecked NEAR account) permanently strands funds while `describeWithdrawal` reports `completed` - (File: `packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts`)

### Summary
`IntentsBridge.validateWithdrawal` only checks that `destinationAddress` matches the generic NEAR account-ID regex format via `validateAddress(..., Chains.Near)`; it performs no check that the address is a real, user-controlled recipient and no check excluding the verifying contract itself (`intents.near`) or other protocol/reserved accounts. `createWithdrawalIntents` then builds a `transfer` intent whose `receiver_id` is exactly that unchecked `destinationAddress`, and `describeWithdrawal` unconditionally returns `{status: "completed"}` without any on-chain verification of where the balance ended up.

### Finding Description
The claimed broken equality is: **intended recipient (user-controlled account) == `receiver_id` actually credited by the `transfer` intent**. Tracing the code:

- `validateWithdrawal` only calls `validateAddress(args.destinationAddress, Chains.Near)`, which resolves to `utils.validateNearAddress(address)` — a pure format/regex check with no semantics about who owns the account and no denylist for reserved accounts such as the verifying contract `intents.near`. [1](#0-0) 
- `createWithdrawalIntents` copies `args.withdrawalParams.destinationAddress` verbatim into `receiver_id` of the `transfer` intent, with `tokens: {[assetId]: amount}`. [2](#0-1) 
- `describeWithdrawal` returns `completed` immediately based only on the presence of `args.tx.hash`, without confirming that the `transfer` succeeded to a meaningful account or that funds are recoverable by the integrator/user. [3](#0-2) 

If `destinationAddress` is set to `intents.near` (a syntactically valid NEAR account, and in fact the verifying contract itself), `validateAddress` returns `true`, `createWithdrawalIntents` emits `{intent: "transfer", receiver_id: "intents.near", tokens: {"nep141:xrp.omft.near": amount}}`, and the multi-token balance for `amount` of `nep141:xrp.omft.near` becomes owned by the `intents.near` account entry inside its own internal ledger rather than by any wallet the user/integrator controls. `describeWithdrawal` still reports `completed`, so the integrator believes the withdrawal succeeded normally.

None of the existing guards catch this: `supports()` only checks `routeConfig.route === RouteEnum.InternalTransfer`; `validateAddress` is format-only by design (per its own docstring); there is no `compareAddresses`/allow-list/denylist step anywhere in this bridge comparing `destinationAddress` against the verifying contract or other reserved accounts; and `describeWithdrawal` never queries chain state to confirm the receiver is meaningful.

### Impact Explanation
The user's/integrator's asset balance for `nep141:xrp.omft.near` (or any asset) is debited from the sender inside `intents.near` and credited to an account (`intents.near` itself, or any other unintended NEAR-format string) that the integrator did not intend and cannot use as a normal counterparty for further intents through this route. The SDK simultaneously reports `status: "completed"`, so the integrator has no signal that recovery/manual intervention is needed. This matches the "withdrawal stuck until manual intervention" High-severity class: repeatable per call, with impact scaling with the amount transferred each time.

### Likelihood Explanation
Preconditions are minimal: the attacker/caller only needs to invoke the public SDK with `createInternalTransferRoute()` and set `destinationAddress` to `intents.near` (or any other syntactically valid but unintended NEAR account string) and a valid `assetId`/`amount`. No special privileges, RPC manipulation, or race conditions are required — this is a standard, documented public entrypoint (`IntentsSDK.processWithdrawal`) reachable by any ordinary user or by an integrator who forwards attacker-controlled strings.

### Recommendation
In `IntentsBridge.validateWithdrawal`, beyond the NEAR-address-format check, reject `destinationAddress` values equal to the verifying/intents contract account (and any other reserved/protocol accounts), and consider requiring confirmation that the destination account exists / is distinct from `envConfig.contractID` before emitting the `transfer` intent. `describeWithdrawal` should not report `completed` purely from `tx.hash` presence without validating the transfer actually reached an operable recipient.

### Proof of Concept
```ts
// vitest, mocks only the withdrawal params — no HTTP/RPC needed to reproduce the missing check
import { describe, it, expect } from "vitest";
import { IntentsBridge } from "../src/bridges/intents-bridge/intents-bridge";

describe("IntentsBridge internal transfer to verifying contract", () => {
  it("does not reject destinationAddress == intents.near", async () => {
    const bridge = new IntentsBridge();

    await expect(
      bridge.validateWithdrawal({
        assetId: "nep141:xrp.omft.near",
        amount: 100n,
        destinationAddress: "intents.near",
      }),
    ).resolves.toBeUndefined(); // no throw => broken equality: "intended recipient" != "receiver_id credited"

    const intents = await bridge.createWithdrawalIntents({
      withdrawalParams: {
        assetId: "nep141:xrp.omft.near",
        amount: 100n,
        destinationAddress: "intents.near",
        destinationMemo: undefined,
      } as any,
      feeEstimation: { amount: 0n, quote: null, underlyingFees: {} } as any,
    });

    expect(intents).toEqual([
      {
        intent: "transfer",
        receiver_id: "intents.near",
        tokens: { "nep141:xrp.omft.near": "100" },
        memo: undefined,
      },
    ]);

    const status = await bridge.describeWithdrawal({
      tx: { hash: "fake-hash" },
    } as any);
    expect(status).toEqual({ status: "completed", txHash: "fake-hash" });
  });
});
```
This confirms both sides of the equality diverge: the `receiver_id` credited (`"intents.near"`, the contract itself) does not equal the account the integrator can subsequently operate on, and `describeWithdrawal` still reports success with no on-chain check.

### Citations

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

**File:** packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts (L97-101)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier,
	): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: args.tx.hash };
	}
```
