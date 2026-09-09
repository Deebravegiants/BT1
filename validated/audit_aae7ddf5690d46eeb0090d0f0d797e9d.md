### Title
`AuroraEngineBridge.describeWithdrawal` unconditionally reports `completed`/`txHash: null` regardless of on-chain outcome - ([File: packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts])

### Summary
`AuroraEngineBridge.describeWithdrawal` is a stub that always returns `{ status: "completed", txHash: null }` with no check of the actual destination transfer, ticket, index, or NEAR/Aurora transaction state. `watchWithdrawal` in `withdrawal-watcher.ts` treats any `status: "completed"` as final success and resolves the polling promise immediately, so every `VirtualChain`-route withdrawal reported through `waitForWithdrawalCompletion` is marked completed on the very first poll, independent of whether the `ft_withdraw` transfer to Aurora actually landed, reverted, or was refunded.

### Finding Description
The claimed invariant is: *the `(status, txHash)` pair returned for withdrawal index `i` corresponds to the i-th withdrawal actually executed for that route, and `completed` is only returned after the destination transfer is final.*

Tracing the code:
- `AuroraEngineBridge.describeWithdrawal()` [1](#0-0)  ignores all of its arguments (`WithdrawalIdentifier`, `index`, `tx`, `withdrawalParams`) and unconditionally returns `{ status: "completed", txHash: null }`.
- `watchWithdrawal` calls `args.bridge.describeWithdrawal({...args.wid, logger})` and, on `status.status === "completed"`, immediately resolves with `{ hash: status.txHash }` (i.e. `{ hash: null }`), ending the poll loop [2](#0-1) .
- `createWithdrawalIdentifiers` assigns a per-route `index` to each withdrawal param and calls `bridge.createWithdrawalIdentifier` [3](#0-2) , and `AuroraEngineBridge.createWithdrawalIdentifier` simply echoes back the passed-in `index`, `withdrawalParams`, and `tx` [4](#0-3)  without any linkage to a real on-chain receipt/outcome for that index.

Because `describeWithdrawal` never inspects `index`, `tx`, or on-chain state at all, the bug is broader than "batch shaping can trick per-index resolution" — every single call, for every index, in every batch composition, order, or duplication, returns `completed`/`null` on the very first poll. There is no logic anywhere in this bridge to distinguish a withdrawal that: (a) succeeded and transferred funds to the destination, (b) was refunded by the Aurora Engine contract (e.g. insufficient storage deposit, invalid destination format, gas issues), or (c) never executed at all. None of the existing guards (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()` ordering, `FeeExceedsAmountError`, `getUnderlyingFee`, `matchesRequest`) apply here because they operate at intent-construction time, not at status-polling time, and none of them verify the destination-chain outcome.

An attacker does not even need to "shape" the batch (order/duplicate/mixed routes) — the divergence exists per single withdrawal already, since `describeWithdrawal` takes no branch based on the identifier. Any batch composition simply multiplies the number of false-`completed` reports, one per `VirtualChain`-route entry, each with `txHash: null`.

### Impact Explanation
An integrator that calls `waitForWithdrawalCompletion` (which drives `watchWithdrawal` per identifier) will receive `status: "completed"` for every `VirtualChain` withdrawal almost immediately, regardless of whether the Aurora Engine bridge actually delivered funds to `destinationAddress`. If the integrator's off-chain ledger treats `completed` as proof of delivery and credits the user (or, in a refund scenario, treats it as delivered and does not also refund — or vice versa treats a stalled/refunded transfer as delivered and releases credit twice), funds can be double-paid: once via the (non-existent or refunded) on-chain transfer and once via the integrator's off-chain credit triggered by the false `completed` signal. This matches the "status or hash misreport making an integrator credit or refund twice" High-severity category. It is fully repeatable on every `VirtualChain` withdrawal, not just crafted batches.

### Likelihood Explanation
Preconditions: the integrator must route a withdrawal through the `VirtualChain` (Aurora Engine) route and rely on the SDK's `waitForWithdrawalCompletion`/`describeWithdrawal` result to decide crediting/refunding. No special batch shaping, duplicate tokens, or signed-intent tricks are required — a single ordinary withdrawal through this bridge is sufficient to trigger a false `completed` report with `txHash: null` on the first poll. This makes the issue trivially and consistently reproducible at zero extra cost to an attacker/normal user; it does not require adversarial ordering of `signedIntents.before/.after`.

### Recommendation
Implement real status verification in `AuroraEngineBridge.describeWithdrawal`: query the underlying NEAR/Aurora Engine transaction or `ft_withdraw` receipt (e.g. via `nearProvider`) tied to the specific `WithdrawalIdentifier`'s `tx`/`index`, and only return `status: "completed"` with a genuine `txHash` once the destination-chain transfer is confirmed final; return `pending` while unresolved and `failed` (with a reason) if the transfer reverted or was refunded. Ensure the returned identifier data unambiguously binds to the specific withdrawal instance (not just an index counter) so batches with duplicate/mixed routes cannot be conflated.

### Proof of Concept
```ts
// aurora-engine-bridge.describeWithdrawal.test.ts
import { describe, it, expect } from "vitest";
import { AuroraEngineBridge } from "./aurora-engine-bridge";

describe("AuroraEngineBridge.describeWithdrawal false-completed", () => {
  it("reports completed/null even though no on-chain transfer occurred", async () => {
    const bridge = new AuroraEngineBridge({
      envConfig: {} as any,
      nearProvider: {} as any, // never queried
    });

    // Simulate a withdrawal that was never executed / refunded on Aurora Engine.
    const status = await bridge.describeWithdrawal();

    // Broken equality under test:
    // status.status === "completed" should imply destination transfer is final
    // AND status.txHash should be a real, verifiable hash.
    expect(status.status).toBe("completed"); // always true regardless of reality
    expect(status.txHash).toBeNull();          // no proof of any transfer
  });
});
```
This demonstrates the equality `(status, txHash)` == `(actual on-chain outcome, real tx hash)` is violated unconditionally: the left side is always `("completed", null)` while the right side can be "never executed" / "refunded" / any arbitrary on-chain state.

### Citations

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L207-218)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		return {
			landingChain: Chains.Near,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
	}
```

**File:** packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts (L220-222)
```typescript
	async describeWithdrawal(): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: null };
	}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-47)
```typescript
		return await poll(
			async () => {
				try {
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L84-107)
```typescript
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
