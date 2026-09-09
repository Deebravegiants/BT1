### Title
Unvalidated `index` used to select Omni Bridge transfer, allowing status/txHash misreport for a different withdrawal - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal` selects the transfer to report on purely by numeric array index into the API response from `getTransfer`, without validating that the transfer at that index actually corresponds to the `withdrawalParams` (asset, destination address, amount) being queried. This mirrors the reported bug class of trusting an unvalidated index into an array that may not contain what the caller expects at that position.

### Finding Description
`OmniBridge.describeWithdrawal` does: [1](#0-0) 

It fetches all transfers for a NEAR tx hash and picks `[args.index]` directly, then trusts whatever `recipient`/`finalised.transaction_hash`/`utxo_meta` is on that array element to build the returned `WithdrawalStatus` (including the destination `txHash`): [2](#0-1) 

There is no check that `transfer` at `args.index` matches the requested `withdrawalParams.assetId`, `destinationAddress`, or `amount`. Contrast this with `PoaBridge.describeWithdrawal`, which explicitly avoids index-based matching because the API's list is unsorted, and instead matches by `assetId`: [3](#0-2) 

The equality that should hold — "the withdrawal status/hash returned corresponds to the exact withdrawal (asset + destination + amount) the caller asked about" — is not enforced in `omni-bridge.ts`; it is only enforced by position in the returned array, which the code itself elsewhere acknowledges (via the sibling `poa-bridge.ts` fix) may not be a safe assumption for bridge API responses. If `getTransfer` returns transfers in an order that does not deterministically match input withdrawal order (e.g., for a single NEAR transaction containing multiple withdraw intents, or if the indexer reorders/dedupes entries), `describeWithdrawal` can report the `txHash` and `completed`/`pending` status of a *different* transfer than the one requested.

### Impact Explanation
If the transfer order returned by the Omni Bridge indexer does not strictly match the input withdrawal order for a batch of withdrawals in one NEAR transaction, an integrator relying on `describeWithdrawal` per `WithdrawalIdentifier.index` could be told that withdrawal N is `completed` with a specific `txHash`, when that `txHash`/status actually belongs to a different withdrawal (different asset/destination/amount). This is a "status reported that is not the on-chain outcome" class issue: it can cause an integrator to credit or reconcile the wrong withdrawal as complete, or mark a still-pending withdrawal as completed with an unrelated transaction hash, leading to a double-credit / no-payout mismatch for the affected withdrawal.

### Likelihood Explanation
Likelihood depends entirely on whether `BridgeAPI.getTransfer`'s ordering is a strict, stable 1:1 mapping to input withdrawal intent order for a given NEAR tx hash. This repo does not contain the indexer/API implementation (it comes from `@omni-bridge/core`), so I could not verify server-side ordering guarantees. The sibling `poa-bridge.ts` code explicitly documents ("Response list is unsorted, so we match by assetId instead of index") that at least one comparable bridge API in this codebase does NOT guarantee order-based correspondence, which is a strong signal that assuming positional correspondence for `omni-bridge.ts` is risky. This is most reachable in the batch-withdrawal path where multiple withdrawal params share one NEAR tx hash.

### Recommendation
In `omni-bridge.ts`'s `describeWithdrawal`, do not select the transfer purely by `args.index`. Instead, match the transfer against the caller-supplied `withdrawalParams` (asset id / token id, recipient/destination address, and amount) similar to the `findMatchingWithdrawal` approach used in `poa-bridge.ts`, or otherwise obtain a stable, bridge-issued identifier from the initial withdraw call and match on that rather than positional index.

### Proof of Concept
Not independently reproducible from this repo alone because it depends on the ordering behavior of `BridgeAPI.getTransfer` from `@omni-bridge/core`, which is out of scope/unavailable in the indexed code. Conceptually: for a single NEAR transaction batching two withdrawals (e.g., withdrawal A to `assetX`/`addrX` at logical index 0, and withdrawal B to `assetY`/`addrY` at logical index 1), if `getTransfer` returns entries in an order that does not match the intents' emission order, `describeWithdrawal({index: 0, withdrawalParams: paramsForA, ...})` would read `transfer[0]`, which could be the entry for withdrawal B, causing the SDK to report `assetX`'s withdrawal as `completed` with B's `txHash`.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-702)
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
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L704-731)
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
