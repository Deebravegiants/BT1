### Title
`OmniBridge.describeWithdrawal` reports `completed` for unhandled/future `ChainKind` without checking `finalised` - ([File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts])

### Summary
`describeWithdrawal`'s destination-chain switch only recognizes EVM, `Sol`, `Fogo`, `Strk`, `Aptos`, and UTXO chain kinds; any other `ChainKind` value falls into the `else` branch which unconditionally returns `{ status: "completed", txHash: null }` without ever inspecting `transfer.finalised`. This breaks the equality that `status: "completed"` should imply the transfer actually finalised on the destination chain.

### Finding Description
The broken equality: **`status === "completed"` should imply `transfer.finalised` (or an equivalent on-chain confirmation) was observed**. In the code: [1](#0-0) 

the branch structure checks `isEvmChain(destinationChain) || Sol || Fogo || Strk || Aptos` (reads `transfer.finalised?.transaction_hash`), then `isUtxoChain(destinationChain)` (reads `finalised` or `pending_sign_id`), and for every other value of `destinationChain` falls to `else { return { status: "completed", txHash: null }; }` — no read of `transfer.finalised` at all.

`destinationChain` is derived from `getChain(transfer.recipient as OmniAddress)` at line 704, which decodes the recipient address string returned by the bridge's `getTransfer` API — this value is not validated against the known chain-kind set before the branch executes. `createWithdrawalIdentifier` only asserts that `makeAssetInfo` succeeds (asset is supported), not that the destination chain kind is one of the six explicitly handled ones — so a withdrawal for a chain kind added to the wider Omni protocol (or any value that decodes outside the known set) can reach `describeWithdrawal` and hit the `else` branch on the very first poll, before the transfer has settled.

Existing guards (`assert` in `createWithdrawalIdentifier`, `supports()`, `validateWithdrawal`) only check asset support, not that the chain-kind switch in `describeWithdrawal` is exhaustive — none of them prevent this divergence.

### Impact Explanation
`sdk.processWithdrawal` → `watchWithdrawal` consumes `WithdrawalStatus`; a `completed` status causes the integrator's polling/watcher logic to treat the withdrawal as settled and release downstream credit (e.g., mark an off-chain ledger entry complete) even though no destination-chain hash or finalisation was ever observed. If the transfer later fails or is delayed, funds are stranded on the bridge while the integrator has already credited the user — a status misreport causing double-credit-like risk, matching the "status misreport making an integrator credit twice" High/Critical impact category. This is repeatable for every future/unmapped chain kind and requires no funds sacrifice by the attacker.

### Likelihood Explanation
Today this path is only reachable if a bridge-supported destination chain kind exists outside `{EVM..., Sol, Fogo, Strk, Aptos, UTXO}` — i.e. it depends on the Omni Bridge protocol/API introducing a new chain kind that `makeAssetInfo` accepts as supported before the SDK's `describeWithdrawal` switch is updated to handle it. This is a real code-maintenance hazard (silent fallthrough default instead of a fail-closed default), but under the *current* fixed enum of chain kinds supported by `makeAssetInfo`, it may not be reachable by an ordinary attacker with today's live asset set — it is a latent defect that activates automatically the moment the bridge or asset config exposes a new/misclassified chain kind, with zero additional attacker action needed.

### Recommendation
Replace the `else` fallthrough with an exhaustive `switch`/explicit unknown-chain-kind handling that returns `{ status: "pending" }` (or throws) rather than `completed`, so unrecognized chain kinds never report false completion; add a compile-time exhaustiveness check (e.g., `assertUnreachable`) over `ChainKind` in this function.

### Proof of Concept
```ts
// omni-bridge.describeWithdrawal.test.ts
it("does not report completed for an unmapped ChainKind", async () => {
  const fakeChainKindRecipient = "unknown-chain:0xdead"; // decodes to ChainKind outside {EVM,Sol,Fogo,Strk,Aptos,UTXO}
  vi.spyOn(omniBridgeAPI, "getTransfer").mockResolvedValue([
    { recipient: fakeChainKindRecipient, finalised: null },
  ]);

  const status = await omniBridge.describeWithdrawal({
    tx: { hash: "fake-hash" },
    index: 0,
    withdrawalParams: /* ... */,
    landingChain: /* ... */,
  });

  // Broken equality check: status should NOT be "completed" while finalised is null
  expect(status.status).not.toBe("completed"); // currently FAILS: returns "completed"
  expect(status).not.toEqual({ status: "completed", txHash: null });
});
```
This mocks only the HTTP-backed `omniBridgeAPI.getTransfer` call and demonstrates the current code returns `completed`/`txHash: null` despite `finalised: null`.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L704-724)
```typescript
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
```
