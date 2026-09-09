### Title
Withdrawal status falsely reported "completed" for unhandled destination chains in Omni Bridge - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal` reports a withdrawal as `completed` (with `txHash: null`) whenever the destination chain of a finalized transfer does not match one of the explicitly-handled chain kinds (EVM, Solana, Fogo, Starknet, Aptos, or a UTXO chain), without verifying that any on-chain delivery actually occurred for that destination.

### Finding Description
In `describeWithdrawal`, once a transfer record is found and has a non-null `recipient`, the code branches on `destinationChain`: [1](#0-0) 

- If the destination is EVM/Sol/Fogo/Strk/Aptos, `txHash` is taken from `transfer.finalised?.transaction_hash`.
- If UTXO, `txHash` is taken from `pending_sign_id` (client) or `finalised?.transaction_hash` (server).
- For any other `destinationChain` (i.e., any chain kind not enumerated in these checks), the function unconditionally returns `{ status: "completed", txHash: null }` — it never checks `transfer.finalised` at all for this branch.

This breaks the equality "status reported == on-chain outcome": the reported `completed` status is not derived from any verified on-chain finality signal for that chain, it is simply the default fallthrough for any chain kind the implementation does not explicitly recognize. If a new chain kind is added to the `ChainKind` enum in the Omni Bridge protocol (or an existing kind's handling is missed here) before this switch is updated, or if `recipient`/`destinationChain` resolves to a value outside the four handled buckets for any reason, the SDK will report the withdrawal as `completed` before the underlying transfer is actually finalized on the destination chain.

### Impact Explanation
A consumer of `describeWithdrawal` (e.g., `watchWithdrawal` in `withdrawal-watcher.ts`, which treats `status: "completed"` as terminal success and returns immediately) will treat the withdrawal as done and stop polling/waiting, even though the funds have not landed on the destination chain. An integrator relying on this status to release credit, mark an intent as fulfilled, or notify a user could double-credit or falsely confirm delivery for a withdrawal that is still pending or could fail, which matches the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
This path is reached automatically, without any attacker action, for any transfer whose resolved `destinationChain` doesn't fall into the four explicit chain buckets in the switch. Given that Omni Bridge continues to add new supported chains, this is a plausible/likely occurrence whenever protocol coverage in `ChainKind` outpaces this function's explicit branches, and it fires silently (no error/log) with no visibility that finality wasn't actually checked.

### Recommendation
Change the fallthrough behavior in `describeWithdrawal` from an implicit "completed" default to an explicit `pending` (or unsupported/error) result unless the destination chain is explicitly recognized and its `finalised` field is verified. Add an exhaustive switch/assertion (e.g. a `never` check) over `ChainKind` so that any newly added chain kind causes a compile-time or runtime failure rather than silently reporting false completion.

### Proof of Concept
1. Craft (or await) a real/mock `getTransfer` response where `transfer.recipient` resolves via `getChain()` to a `ChainKind` value that is not `Eth`/other EVM kinds, `Sol`, `Fogo`, `Strk`, `Aptos`, or a UTXO chain (e.g. a newly-added chain kind, or any kind not yet added to `isEvmChain`/`isUtxoChain` helpers).
2. Call `bridge.describeWithdrawal({...})` for that withdrawal identifier while the actual cross-chain transfer has not yet finalized (`transfer.finalised` is `null`).
3. Observe that the function returns `{ status: "completed", txHash: null }` at line 723 regardless of `transfer.finalised`, causing `watchWithdrawal` to resolve successfully with `{ hash: null }` even though the destination-chain transfer never completed. [2](#0-1)

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
