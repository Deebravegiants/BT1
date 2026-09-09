### Title
`OmniBridge.describeWithdrawal` reports "completed" status by array index without verifying recipient/amount match the requested withdrawal - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal` fetches all on-chain transfers associated with a NEAR transaction hash and picks the transfer at position `args.index` in the returned array, then reports it as `completed` with that transfer's destination `txHash` — without ever checking that the transfer's `recipient`/amount actually correspond to the withdrawal being queried (`args.withdrawalParams.destinationAddress` / `args.withdrawalParams.amount`).

### Finding Description [1](#0-0) 

```
async describeWithdrawal(...) {
    const transfer = (
        await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash })
    )[args.index];

    if (transfer == null || transfer.recipient == null) {
        return { status: "pending" };
    }
    ...
    return { status: "completed", txHash };
}
```

The function trusts positional ordering of the array returned by `omniBridgeAPI.getTransfer()` to correlate a specific withdrawal (identified by `args.index`, assigned client-side when multiple withdrawals are batched into one NEAR tx, see `createWithdrawalIdentifiers()` in `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`) with the transfer object at the same array position from an external indexer API. There is no equality check comparing `transfer.recipient` against `args.withdrawalParams.destinationAddress`, nor `transfer` amount against `args.withdrawalParams.amount`.

This is notable because a sibling implementation, `PoaBridge.describeWithdrawal`, explicitly documents and defends against exactly this class of bug: [2](#0-1) 
```
async describeWithdrawal(...) {
    const response = await this.getWithdrawalStatusWithRetry(args);
    // Response list is unsorted, so we match by assetId instead of index
    const withdrawal = findMatchingWithdrawal(
        response.withdrawals,
        args.withdrawalParams.assetId,
    );
    ...
```
The PoA bridge's inline comment ("Response list is unsorted, so we match by assetId instead of index") confirms that positional/index-based matching against an external API's response list is an established anti-pattern in this codebase precisely because ordering is not guaranteed. `OmniBridge.describeWithdrawal`, however, still relies purely on `[args.index]` without any content-based verification (no recipient check, no amount check), breaking the equality "transfer reported at index N is the transfer that corresponds to withdrawal N."

If a user submits multiple withdrawals in a single batched intent (a supported feature per `createWithdrawalIdentifiers`), and the indexer returns the transfers for that NEAR tx hash in an order that does not exactly match on-chain emission/creation order (e.g., due to indexing race conditions, multiple `ft_withdraw` intents processed concurrently, or backend re-ordering), `describeWithdrawal` will silently attribute one withdrawal's destination chain tx hash/status to a different withdrawal's identifier.

### Impact Explanation
An integrator or the SDK's own withdrawal-watcher (`packages/intents-sdk/src/core/withdrawal-watcher.ts`) uses `describeWithdrawal`'s returned `status: "completed"` / `txHash` to determine that a specific withdrawal (identified by asset, destination address, and amount) has landed. If the wrong transfer object is matched due to index misalignment, the SDK reports completion (and a settlement tx hash) for a withdrawal that has not actually settled at the expected destination address/amount, while the withdrawal that truly needs tracking may remain unreported or matched to the wrong hash. This falls into the "status or hash misreport making an integrator credit or refund twice" category — an integrator polling this API could mark a user's withdrawal as settled based on another withdrawal's transfer data, or conversely fail to detect that the correct withdrawal never completed.

### Likelihood Explanation
This requires: (1) a batched multi-withdrawal intent processed through the Omni Bridge route (a documented, supported feature), and (2) the external Omni Bridge indexer (`omniBridgeAPI.getTransfer`) returning transfers for that tx hash in an order that doesn't align with the client-assigned index. Given that the PoA bridge implementation in the same codebase explicitly states this ordering assumption is false for its own API ("Response list is unsorted"), it is plausible the Omni Bridge indexer has similar characteristics, though this specific behavior was not directly confirmed for the Omni indexer within the available code/tests. This uncertainty should be validated against the actual `@omni-bridge/core` `BridgeAPI.getTransfer` ordering guarantees, which are outside this repo's scope and not something I could verify from the indexed files.

### Recommendation
Match transfers by content (e.g., recipient address plus token/asset) similar to `PoaBridge.findMatchingWithdrawal`, rather than by raw array index, or additionally assert that `transfer.recipient` corresponds to the expected `omniAddress(omniChainKind, args.withdrawalParams.destinationAddress)` before reporting `status: "completed"`.

### Proof of Concept
Not independently reproducible from the indexed code alone — reproduction depends on `@omni-bridge/core`'s `BridgeAPI.getTransfer` ordering behavior for a NEAR tx containing 2+ Omni Bridge withdrawals with different destination addresses, which is external to this repo and not available to fully verify from the indexed files.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-731)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];

		if (transfer == null || transfer.recipient == null) {
			return { status: "pending" };
		}

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

		if (!txHash) {
			return { status: "pending" };
		}

		return { status: "completed", txHash };
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const response = await this.getWithdrawalStatusWithRetry(args);

		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);
```
