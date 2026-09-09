### Title
`DirectBridge.describeWithdrawal` reports "completed" without verifying the on-chain withdrawal outcome - (File: `packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts`)

### Summary
For the `near_withdrawal` route, the SDK's `DirectBridge.describeWithdrawal` unconditionally returns `{ status: "completed", txHash: args.tx.hash }` without ever checking whether the underlying `ft_withdraw`/token transfer actually succeeded on-chain. Every other bridge implementation in this SDK (`PoaBridge`, `OmniBridge`, `HotBridge`) queries an external source of truth (indexer/API/contract view) before reporting `"completed"`. `DirectBridge` is the outlier: it echoes back the caller-supplied intent tx hash as proof of success.

### Finding Description
`describeWithdrawal` is the function all bridges implement to answer "did the withdrawal land on the destination chain?" `watchWithdrawal` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` polls this method and, the moment it sees `status: "completed"`, resolves the promise and hands back a tx hash to the caller/integrator as proof of settlement: [1](#0-0) 

For `PoaBridge`, `OmniBridge`, and `HotBridge`, `describeWithdrawal` actually inspects an external status source (POA relayer API, Omni Bridge indexer, HOT SDK/bridge indexer) and only returns `"completed"` when a real destination transaction/hash is confirmed: [2](#0-1) [3](#0-2) 

`DirectBridge`, used for the `near_withdrawal` route (NEP-141 transfers to a NEAR account via the `ft_withdraw` intent), does none of this: [4](#0-3) 

It simply returns the NEAR intent transaction hash it was given and claims `"completed"`. The `ft_withdraw` intent is executed via a cross-contract call/promise from the intents contract to the target NEP-141 token contract. NEAR cross-contract promises are asynchronous: the outer transaction (and the solver-relay "SETTLED" status the SDK observed earlier via `waitForIntentSettlement`) can report success for the *intents contract's own receipt* while the *nested* `ft_transfer` promise to the token contract still fails afterward (e.g., destination not registered for storage on that specific token, in insufficient token balance held by the bridge/omft contract, or any other panic in the downstream call). Unless the intents contract has a receiver callback that reverts internal balance state on transfer failure (that logic lives in `intents.near`, out of scope here), the SDK has no way to know the transfer failed — and `DirectBridge.describeWithdrawal` doesn't even try to check.

This breaks the same equality as the H02 report: *"a status reported that is not the on-chain outcome."* In the original bug, the L1 gateway didn't check `transfer()`'s return value, so a failed ERC20 transfer was still treated as successful, desynchronizing L1/L2 state. Here, the SDK doesn't check the actual result of the `near_withdrawal` transfer at all before reporting `"completed"` to the caller.

### Impact Explanation
Per the rubric, a "status or hash misreport making an integrator credit or refund twice" is a High-severity outcome. Any integrator relying on `sdk.waitForWithdrawalCompletion` / `watchWithdrawal` for the `near_withdrawal` route will see `status: "completed"` and a tx hash immediately after intent settlement, and may credit the user or mark the withdrawal as delivered — even if the actual token transfer to the destination NEAR account failed downstream. This is a genuine "status misreport" bug: the described equality (`describeWithdrawal` output == real destination-chain outcome) is broken specifically for this route, unlike all sibling bridge implementations that do verify.

### Likelihood Explanation
The condition under which the nested transfer can fail while the outer settlement succeeds depends on details of the `intents.near` contract's callback/rollback behavior for `ft_withdraw`, which is out of scope to fully verify from this repo. However, the SDK code itself provides no verification path at all — regardless of how often the nested failure occurs in practice, the client-side status-reporting logic is unconditionally wrong by construction, and every other route in this same codebase treats this as something that must be actively checked.

### Recommendation
For the `near_withdrawal` route, `describeWithdrawal` should verify the actual outcome of the withdrawal (e.g., by inspecting the NEAR transaction/receipt execution outcome for the `ft_withdraw` cross-contract call, or via a similar mechanism used for `internal_transfer`/`virtual_chain` withdrawals) instead of unconditionally returning `"completed"`. At minimum, it should check the FunctionCall execution status/receipt outcomes of the transaction referenced by `args.tx.hash` and return `"failed"` if the nested transfer receipt failed, mirroring the verification done in `PoaBridge`, `OmniBridge`, and `HotBridge`.

### Proof of Concept
1. Initiate a `near_withdrawal` (`DirectBridge`) withdrawal for a NEP-141 token to a destination NEAR account.
2. Arrange for the destination account/token pairing such that the internal `ft_transfer` triggered inside the intents contract's execution fails after the outer intent settlement is marked `SETTLED` (e.g., a storage-registration edge case not covered by `validateWithdrawal`'s general account-existence check, or a downstream panic in the token contract not rolled back by a callback).
3. Call `sdk.waitForWithdrawalCompletion` / `watchWithdrawal`; observe that `DirectBridge.describeWithdrawal` returns `{ status: "completed", txHash: args.tx.hash }` unconditionally: [4](#0-3) 
4. An integrator consuming this result treats the withdrawal as delivered and credits/finalizes it, despite the underlying transfer having failed on-chain.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-343)
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

		return {
			status: "failed",
			reason: withdrawal.status,
		};
	}
```

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

**File:** packages/intents-sdk/src/bridges/direct-bridge/direct-bridge.ts (L334-338)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier,
	): Promise<WithdrawalStatus> {
		return { status: "completed", txHash: args.tx.hash };
	}
```
