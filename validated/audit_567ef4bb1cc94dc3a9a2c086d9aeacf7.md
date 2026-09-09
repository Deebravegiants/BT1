### Title
Withdrawal status/txHash misattribution via unchecked positional indexing in `OmniBridge.describeWithdrawal()` - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
`OmniBridge.describeWithdrawal()` selects the transfer describing a given withdrawal purely by array position (`transfers[args.index]`) returned from `omniBridgeAPI.getTransfer({transactionHash})`, with no check that the returned transfer's `recipient`/`amount` actually corresponds to the withdrawal identifier (`withdrawalParams.destinationAddress`, `assetId`, `amount`) being queried. This breaks the equality "status/txHash reported for withdrawal N == the on-chain outcome of withdrawal N."

### Finding Description
In `OmniBridge.describeWithdrawal()`:
```
const transfer = (
  await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash })
)[args.index];

if (transfer == null || transfer.recipient == null) {
  return { status: "pending" };
}
...
return { status: "completed", txHash };
``` [1](#0-0) 

The function trusts `args.index` as a reliable pointer into the array returned by the indexer for a given NEAR transaction hash, and reports "completed" with whatever `txHash` is attached to that array slot, without validating that the transfer's `recipient` matches `withdrawalParams.destinationAddress` (or that amount/asset match).

By contrast, the sibling `PoaBridge.describeWithdrawal()` explicitly guards against this exact class of bug:
```
// Response list is unsorted, so we match by assetId instead of index
const withdrawal = findMatchingWithdrawal(
  response.withdrawals,
  args.withdrawalParams.assetId,
);
``` [2](#0-1) 

This comment demonstrates that the SDK authors are aware that indexer/API responses describing multiple withdrawals originating from the same NEAR transaction are not guaranteed to preserve submission order, and therefore matching by position (`index`) is unsafe. The `OmniBridge` implementation does not apply the same defensive matching, leaving the "index == same logical withdrawal" equality unverified.

When a single NEAR transaction contains multiple withdrawal intents (a common batching pattern supported by the intents contract, as seen in the `intents` array of `MultiPayload` schemas), `watchWithdrawal()` in `withdrawal-watcher.ts` polls `bridge.describeWithdrawal()` per `WithdrawalIdentifier` (which carries only `index`, `tx.hash`, and the original `withdrawalParams`) and trusts the returned status/txHash outright:
```
const status = await args.bridge.describeWithdrawal({ ...args.wid, logger: args.logger });
...
if (status.status === "completed") {
  return status.txHash != null ? { hash: status.txHash } : { hash: null };
}
``` [3](#0-2) 

If the indexer returns transfers for that NEAR tx hash in an order that does not match the intent submission order (e.g., due to concurrent promise execution/settlement ordering — which the schema itself warns about: "Promises created by different intents are executed concurrently and does not rely on the order of the intents in this structure"), `describeWithdrawal()` for withdrawal index 0 could pick up the transfer belonging to withdrawal index 1 (a different recipient/amount), and vice versa.

### Impact Explanation
This can cause a status/txHash misreport: an integrator polling withdrawal #0 could be told "completed" with a `txHash` that actually corresponds to a different recipient's transfer (withdrawal #1), while withdrawal #1's `destinationAddress` differs. This can lead to:
- An integrator crediting/finalizing withdrawal #0 based on a transaction that did not actually deliver funds to withdrawal #0's `destinationAddress`.
- Silent double-credit or wrong completion reporting when multiple withdrawals are batched into a single NEAR transaction.

This matches the "High" impact class: a status or hash misreport making an integrator credit or refund twice/wrongly.

### Likelihood Explanation
Likelihood is moderate and depends on:
1. Multiple withdrawal intents being included in a single signed transaction (supported by the intents contract's multi-intent payload).
2. The Omni Bridge indexer (`omniBridgeAPI.getTransfer`) returning the transfer array for that transaction hash in an order that does not match intent submission order — the explicit comment in the sibling `PoaBridge` code ("Response list is unsorted") suggests this ordering assumption is known to be unreliable in this ecosystem for similar APIs, but I was not able to fully verify from the available indexed files whether `omniBridgeAPI.getTransfer`'s ordering guarantee differs from POA's. This is the main open uncertainty in this finding — without access to the Omni Bridge indexer's actual ordering contract, this cannot be confirmed as definitively exploitable versus a purely defensive-coding gap.

### Recommendation
In `OmniBridge.describeWithdrawal()`, do not rely solely on `args.index` to select the transfer. Match the transfer by validating that `transfer.recipient` corresponds to `args.withdrawalParams.destinationAddress` (accounting for chain-specific address normalization, similar to `compareAddresses`/`toPoaNetwork` matching used in `PoaBridge`) and, where possible, `amount`/`assetId`, falling back to `pending` if no transfer unambiguously matches the withdrawal identifier — mirroring the defensive `findMatchingWithdrawal` pattern already used in `PoaBridge.describeWithdrawal()`.

### Proof of Concept
1. A user submits a single NEAR transaction containing two Omni Bridge withdrawal intents in one payload: withdrawal A → `destinationAddress = addrX` (index 0) and withdrawal B → `destinationAddress = addrY` (index 1).
2. The Omni Bridge indexer processes/settles the two transfers and returns them from `getTransfer({transactionHash})` in reverse order (B before A) — plausible given intents execute concurrently per the schema note "Promises created by different intents are executed concurrently and does not rely on the order of the intents in this structure" [4](#0-3) .
3. `watchWithdrawal()` calls `describeWithdrawal({ index: 0, withdrawalParams: {destinationAddress: addrX, ...}, tx })`, which reads `transfers[0]`, which is actually B's transfer (destined for `addrY`), and reports `{status: "completed", txHash: <B's tx hash>}` for withdrawal A.
4. An integrator watching withdrawal A now believes it completed to `addrX` using a transaction hash that in fact paid `addrY`, leading to a wrong completion record / potential double-credit if withdrawal B is also independently reported as completed with the same hash.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-337)
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

		if (withdrawal == null) {
			return { status: "pending" };
		}

		if (withdrawal.status === "PENDING") {
			return { status: "pending" };
		}

		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
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

**File:** packages/contract-types/src/type-check-schemas.ts (L1859-1862)
```typescript
							intents: {
								description:
									"Sequence of intents to execute in given order. Empty list is also a valid sequence, i.e. it doesn't do anything, but still invalidates the `nonce` for the signer WARNING: Promises created by different intents are executed concurrently and does not rely on the order of the intents in this structure",
								type: "array",
```
