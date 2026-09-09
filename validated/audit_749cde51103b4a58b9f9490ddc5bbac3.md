### Title
Batch/composed withdrawals misindex `getTransfer` results causing OmniBridge `describeWithdrawal` to report another withdrawal's status/txHash - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal` resolves a withdrawal's status by indexing `getTransfer({transactionHash})[args.index]`, where `args.index` is a per-route counter computed only from the caller's own `withdrawalParams` array in `createWithdrawalIdentifiers`. When a withdrawal is signed together with unrelated pre-signed intents via `signedIntents.before`/`.after` and published atomically in a single NEAR transaction (`IntentExecuter.signAndSendIntent` → `publishIntents`), any OmniBridge `ft_withdraw` calls contained in the `before` intents occupy earlier positions in that same transaction's transfer list, shifting the indexer's per-transaction array without the SDK's local index accounting for it.

### Finding Description
The equality the SDK relies on is:

> position of the i-th OmniBridge withdrawal in the caller's `withdrawalParams` array == position of the corresponding transfer in `getTransfer({transactionHash: tx.hash})` for that NEAR transaction.

`createWithdrawalIdentifiers` builds this index purely from the caller-supplied `withdrawalParams` array, with one counter per bridge `route`: [1](#0-0) 

`OmniBridge.describeWithdrawal` then trusts that local index to pick the transfer out of the *entire* transaction's transfer list: [2](#0-1) 

That NEAR transaction, however, is not guaranteed to contain only the caller's own intents. `signAndSendIntent`/`IntentExecuter.signAndSendIntent` explicitly supports composing arbitrary pre-signed `before`/`after` `MultiPayload`s and publishing them **atomically in one call to `publishIntents`**, returning only the ticket for the "new" intent (`tickets[beforeCount]`): [3](#0-2) [4](#0-3) 

The feature is explicitly documented as usable "for multi-user coordination" with withdrawals: [5](#0-4) 

If any of the `before` payloads themselves contain OmniBridge `ft_withdraw` intents (e.g., another user's/counterparty's pre-signed withdrawal, forwarded by an integrator through the `signedIntents` boundary that the question lists as attacker-controlled), those `ft_withdraw` calls execute *before* the current withdrawal's own `ft_withdraw` call(s) inside the same NEAR transaction. The OmniBridge indexer's `getTransfer({transactionHash})` array reflects on-chain call order for that whole transaction, so the current withdrawal's transfer is no longer at position 0 (or whatever local index `createWithdrawalIdentifiers` assigned) — it is shifted by however many OmniBridge transfers the `before` intents injected. Since `describeWithdrawal` blindly indexes by the locally-computed `args.index`, it returns the `before` intent's transfer status and `txHash` instead of the caller's own.

None of the existing guards prevent this: `supports()`/route detection only decides *which bridge* handles a withdrawal, not cross-transaction index alignment; `createWithdrawalIdentifiers`'s per-route counter (`indexes.get(bridge.route)`) is local to the array the caller passed to `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` and has no knowledge of `signedIntents.before/after` used when the withdrawal was originally signed and sent — that information is not threaded through `intentTx`/`WithdrawalParams` at all. There is no cross-check that `getTransfer(transactionHash).length` matches expectations, nor any correlation by `external_id`/`msg` (the OmniBridge intents do carry a unique `external_id` per withdrawal, generated in `deriveOmniWithdrawIntentParams`, but `describeWithdrawal` does not use it to disambiguate — it only uses positional index).

### Impact Explanation
An integrator that calls `waitForWithdrawalCompletion` (or `createWithdrawalCompletionPromises`) with `withdrawalParams` for a withdrawal that was originally signed with `signedIntents.before` containing another OmniBridge withdrawal will receive `(status: "completed", txHash: <someone else's tx hash>)` for its own withdrawal's index once that unrelated transfer finalizes — while the user's own transfer might still be pending, failed, or resolve to a different destination. If the integrator credits/refunds based on this misreported `(status, txHash)`, it can credit the wrong outcome or duplicate payout logic, matching the "High — a status or hash misreport making an integrator credit or refund twice" category. The effect is repeatable any time `signedIntents.before/after` bundling OmniBridge withdrawals is used, since the index-vs-transfer-array mismatch is deterministic given a fixed batch composition.

### Likelihood Explanation
This requires the integrator/user to actively use the `signedIntents.before`/`.after` composition feature with OmniBridge-routed withdrawals mixed with unrelated pre-signed intents — a documented, intentionally-supported multi-user coordination flow, and the "attacker controls: signedIntents" precondition is explicitly called out in the question's attack surface. No privileged access is needed: the attacker only needs to supply a pre-signed `MultiPayload` (their own signed intent, or one obtained as counterparty) into the `signedIntents.before` field that an integrator forwards. Given the feature's documented intent (accepting other users' pre-signed intents), this is a realistic and low-cost precondition, though it depends on the integrator actually using batch/composition withdrawals with OmniBridge routes rather than plain single withdrawals (the common case is unaffected, since without `signedIntents` the transaction contains only the caller's own intents and the indexer's array order matches the caller's local index).

### Recommendation
- Do not rely on purely positional indexing into `getTransfer({transactionHash})`. Correlate each returned transfer to the specific withdrawal via a unique, verifiable identifier such as the `external_id` (or `msg`) embedded in the `ft_withdraw` intent by `deriveOmniWithdrawIntentParams`, matching it against the transfer's `msg`/`external_id` field returned by the indexer instead of `args.index`.
- Alternatively, when `signedIntents.before/after` are used with withdrawals, thread the number of OmniBridge transfers contributed by `before` intents into the per-route index offset in `createWithdrawalIdentifiers`, or reject/flag combining withdrawal signing with third-party `signedIntents` composition unless the caller supplies enough information to compute the correct offset.

### Proof of Concept
Vitest plan (mock only the OmniBridge `getTransfer` HTTP call):
```ts
// omni-bridge.test.ts — describeWithdrawal() index-shift scenario
it("misreports another withdrawal's txHash when transfers are shifted by an unrelated prior withdrawal in the same tx", async () => {
  // Simulate a NEAR tx that contains: [before-intent's ft_withdraw transfer, current withdrawal's ft_withdraw transfer]
  vi.spyOn(BridgeAPI.prototype, "getTransfer").mockResolvedValue([
    createTransferMock({
      recipient: "eth:0xBEFORE00000000000000000000000000000000",
      finalised: { transaction_hash: "0xBEFORE-tx", chain: "Eth", timestamp_seconds: 1, details: { type: "evm", block_number: 1, transaction_index: null, log_index: null } },
    }),
    createTransferMock({
      recipient: "eth:0xOWN0000000000000000000000000000000000",
      finalised: null, // caller's own withdrawal still pending
    }),
  ]);

  const bridge = new OmniBridge({ envConfig: configsByEnvironment.production, nearProvider });

  // createWithdrawalIdentifiers assigns index 0 for caller's single OmniBridge withdrawal,
  // unaware that a "before" intent injected one OmniBridge transfer ahead of it.
  const result = await bridge.describeWithdrawal({
    landingChain: Chains.Ethereum,
    index: 0, // caller's local index — but should be 1 in the shared tx's transfer array
    withdrawalParams: {
      assetId: "nep141:eth.bridge.near",
      amount: 100000n,
      destinationAddress: "0xOWN0000000000000000000000000000000000",
      feeInclusive: false,
    },
    tx: { hash: "shared-near-tx-hash", accountId: "test.near" },
  });

  // BROKEN EQUALITY: SDK reports "completed" with the BEFORE intent's txHash,
  // even though the caller's own withdrawal (index 1 in the real array) is still pending.
  expect(result).toEqual({ status: "completed", txHash: "0xBEFORE-tx" }); // WRONG — should be { status: "pending" }
});
```
This demonstrates that `describeWithdrawal`'s reliance on a locally-computed `args.index` against a transfer array that can be extended by unrelated `signedIntents.before/after` intents produces a status/hash misreport for the caller's own withdrawal.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L88-104)
```typescript
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-698)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L99-124)
```typescript
		// Compose with pre-signed intents if provided
		const composedPayloads = composeMultiPayloads(multiPayload, signedIntents);

		// If we have multiple payloads (with signed intents), publish them atomically
		if (composedPayloads.length > 1) {
			const quoteHashes =
				(relayParams as { quoteHashes?: string[] }).quoteHashes ?? [];

			// Publish all payloads atomically using the relayer's batch method
			const tickets = await this.intentRelayer.publishIntents(
				{
					multiPayloads: composedPayloads,
					quoteHashes,
				},
				{ logger: this.logger },
			);

			// Calculate the index of the newly created intent
			// Order is: [before...] -> newPayload -> [after...]
			const beforeCount = signedIntents?.before?.length ?? 0;
			const newIntentTicket = tickets[beforeCount];

			// Return the ticket for the newly created intent
			// Note: All composed intents execute atomically, but we return the main one
			return { ticket: newIntentTicket as Ticket };
		}
```

**File:** packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts (L190-214)
```typescript
function composeMultiPayloads(
	newPayload: MultiPayload,
	signedIntents?: SignedIntentsComposition,
): MultiPayload[] {
	if (!signedIntents) {
		return [newPayload];
	}

	const result: MultiPayload[] = [];

	// Add "before" intents first
	if (signedIntents.before && signedIntents.before.length > 0) {
		result.push(...signedIntents.before);
	}

	// Add the new payload
	result.push(newPayload);

	// Add "after" intents last
	if (signedIntents.after && signedIntents.after.length > 0) {
		result.push(...signedIntents.after);
	}

	return result;
}
```

**File:** packages/intents-sdk/README.md (L952-979)
```markdown
### Atomic Multi-Intent Publishing

Include pre-signed intents (from other users or prior operations) to be published atomically with your new intent. 
Useful for multi-user coordination and batch operations.

```typescript
import type { MultiPayload } from '@defuse-protocol/intents-sdk';

// Include pre-signed intents before/after your new intent
await sdk.signAndSendIntent({
    intents: [{ intent: "transfer", receiver_id: "alice.near", tokens: {...} }],
    signedIntents: {
        before: [preSigned1],  // Execute before new intent
        after: [preSigned2]    // Execute after new intent
    }
});

// Also works with withdrawals
await sdk.processWithdrawal({
    withdrawalParams: {...},
    intent: {
        signedIntents: {
            before: [preSigned1],
            after: [preSigned2]
        }
    }
});
```
```
