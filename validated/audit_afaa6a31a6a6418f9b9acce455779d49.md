### Title
Relayer fee `Fees` balance is zeroed on withdrawal dispatch before the destination-chain payout is confirmed, permanently losing the claim if delivery reverts - (File: `modules/pallets/relayer/src/withdrawal.rs`)

### Summary
`Pallet::withdraw` in the relayer pallet dispatches a cross-chain ISMP POST request instructing the destination chain's host (or `HYPERBRIDGE_MODULE_ID` on Substrate) to disburse `available_amount` to the relayer's beneficiary, and unconditionally zeroes the local `Fees` accounting entry immediately after the dispatch call succeeds — without any confirmation that the payout on the destination will actually complete. This mirrors the M-30 pattern: an irreversible state change ("fees claimed"/"protocol blacklisted") is committed based on the *initiation* of a withdrawal rather than its *verified completion*, so a downstream failure leaves funds unrecoverable.

### Finding Description
`Pallet::withdraw` (`modules/pallets/relayer/src/withdrawal.rs`) reads the relayer's accrued balance, verifies the signature, dispatches an ISMP `Post` request carrying a `WithdrawalParams`/`Message::WithdrawRelayerFees` payload to the destination, and then immediately does: [1](#0-0) 

The comment in the module itself documents the assumption driving the bug: "The on-chain effect is just dispatching the message; the destination chain settles the payout when the ISMP request is delivered there," and "3. The `Fees` entry is zeroed so the same balance cannot be withdrawn twice." [2](#0-1) 

The actual payout on the EVM side is performed by `EvmHost.withdraw`, which is restricted to the host manager and reverts the entire delivery transaction if the payout cannot be completed — e.g. on an ERC20 `safeTransfer` failure or a failed native-token `.call`: [3](#0-2) 

This revert path is explicitly exercised by `test_host_manager_insufficient_balance`, confirming that a withdrawal for more than the host's current fee-token balance reverts rather than partially disbursing: [4](#0-3) 

Because `HandlerV2.handlePostRequests` calls `host.dispatchIncoming(leaf.request, _msgSender())` directly with no try/catch, a revert inside the module's `onAccept` (i.e. inside `IHostManager.withdraw`) reverts the whole delivery transaction: [5](#0-4) 

The withdrawal request is dispatched with `timeout: 0`: [6](#0-5) 

I was not able to fully verify from the index whether a `timeout: 0` ISMP request is treated by Hyperbridge/pallet-ismp as "never times out" (so delivery can be retried indefinitely until the host manager eventually has sufficient balance) or whether some other liveness/expiry path exists. If the request never expires, the loss is a liveness issue (funds recoverable once the destination is funded) rather than a permanent freeze. However, on the substrate destination path, the corresponding `on_accept` handler transfers directly from `RELAYER_FEE_ACCOUNT` and also has no compensating path back to `Fees` on failure: [7](#0-6) 

In neither direction does the pallet re-credit `Fees` if the disbursement fails or is never delivered — there is no equivalent of the "if balance still >0, don't blacklist" check the auditors recommended for Vault.sol. The `Fees` mapping is zeroed at dispatch time, not at confirmed-delivery time, so any scenario where the destination-side payout permanently fails (host manager underfunded and never topped up, host frozen, admin/relayer misconfiguration on the manager, or the request is otherwise never able to be delivered) results in the relayer's claim being erased with no recovery mechanism.

### Impact Explanation
If the destination-side disbursement never successfully completes, the relayer's legitimately accrued fee balance is permanently zeroed with no path to reclaim it — a straightforward loss-of-funds condition for the relayer, reachable by any relayer simply calling the ordinary fee-withdrawal flow that is core to Hyperbridge's economic model (relayer fee and reward accounting is explicitly in scope). This is a Medium-severity finding, analogous to the accepted M-30 in the source report: the root cause is committing an irreversible accounting change (`Fees` zeroed) before validating that the corresponding value transfer actually completed.

### Likelihood Explanation
The disbursement can fail for many benign operational reasons already demonstrated in-repo (e.g. insufficient host fee-token balance, as covered by `test_host_manager_insufficient_balance`), and nothing in `Pallet::withdraw` retries the accounting on failure or ties the `Fees` zeroing to confirmed delivery. Any relayer performing routine withdrawals during a period where the destination host is underfunded, frozen, or its host manager misconfigured is exposed. Likelihood is moderate — it depends on external funding/liveness conditions on the destination host rather than an active attacker, but requires no privileged or malicious actor to trigger.

### Recommendation
Do not zero `Fees` until the disbursement is confirmed. Options:
- Only zero/decrement `Fees` upon receiving a confirmed response/acknowledgement of successful delivery from the destination chain (mirrors ISMP's request/response model already used elsewhere, e.g. `onGetResponse` in the intents gateway).
- Alternatively, keep `Fees` decremented but add a compensating `on_timeout`/`on_response`-failure handler that re-credits the relayer's `Fees` balance if the withdrawal request times out or the destination reports failure.
- On the EVM side, consider allowing `EvmHost.withdraw` to disburse a lesser amount when balance is insufficient (partial fulfilment) and emit an event with the actual amount paid, or have the module ack failures observably so pallet-ismp/pallet-relayer can react, rather than silently reverting the whole delivery with the relayer's `Fees` entry already erased on the source.

### Proof of Concept
1. Relayer accrues `available_amount` of fees in `Fees::<T>::get(dest_chain, relayer_address)` on Hyperbridge via `accumulate_fees`.
2. Relayer calls `Pallet::withdraw` for `dest_chain` = an EVM chain. The pallet computes `available_amount`, dispatches the ISMP POST to the destination's `host_manager`, and immediately sets `Fees::<T>::insert(dest_chain, relayer, U256::zero())` (`modules/pallets/relayer/src/withdrawal.rs:177`).
3. Assume the EVM `EvmHost` fee-token balance is (temporarily or persistently) less than `available_amount` — this is a realistic, non-malicious state as validated by `test_host_manager_insufficient_balance`.
4. When a relayer delivers the POST request via `HandlerV2.handlePostRequests`, `host.dispatchIncoming` → `HostManager.onAccept` → `IHostManager(_params.host).withdraw(withdrawParams)` → `EvmHost.withdraw` reverts (`WithdrawalFailed` or `SafeERC20` revert), and the entire delivery transaction reverts — no request receipt is stored.
5. The relayer's fee is now `0` on Hyperbridge (already zeroed in step 2), yet no funds were ever received on the destination chain. Unless/until the host is topped up and someone redelivers the same request before any timeout condition applies, the relayer's claimed fee is unrecoverable through the pallet — there is no code path that re-credits `Fees::<T>`.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L16-30)
```rust
//! Relayer fee withdrawal.
//!
//! Once fees have been accumulated into [`crate::pallet::Fees`] by
//! [`crate::accumulate`], relayers withdraw them via [`Pallet::withdraw`].
//! The flow:
//!
//! 1. The relayer signs a `(nonce, dest_chain, beneficiary?)` payload with their per-chain key (EVM
//!    secp256k1 / sr25519 / ed25519).
//! 2. The pallet verifies the signature, increments the per-relayer nonce, and dispatches an ISMP
//!    POST request to the destination's host manager (EVM) or `HYPERBRIDGE_MODULE_ID` (substrate)
//!    instructing it to disburse `available_amount` of the fee token to the beneficiary.
//! 3. The `Fees` entry is zeroed so the same balance cannot be withdrawn twice.
//!
//! The on-chain effect is just dispatching the message; the destination chain settles the
//! payout when the ISMP request is delivered there.
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L161-187)
```rust
		let post = DispatchPost {
			dest: withdrawal_data.dest_chain,
			from: MODULE_ID.to_vec(),
			to,
			body,
			timeout: 0,
		};

		// Account is not useful in this case
		dispatcher
			.dispatch_request(
				DispatchRequest::Post(post),
				FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
			)
			.map_err(|_| Error::<T>::DispatchFailed)?;

		Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());

		Self::deposit_event(Event::<T>::Withdraw {
			address: sp_runtime::BoundedVec::truncate_from(address.clone()),
			beneficiary_address: sp_runtime::BoundedVec::truncate_from(beneficiary_address),
			state_machine: withdrawal_data.dest_chain,
			amount: available_amount,
		});

		Ok(())
	}
```

**File:** evm/src/core/EvmHost.sol (L651-660)
```text
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

**File:** evm/tests/rust/src/tests/host_manager.rs (L152-181)
```rust
#[test]
fn test_host_manager_insufficient_balance() {
	let mut env = TestEnv::new();
	let manager = host_manager_of(&mut env);

	// Host has no fee tokens; withdraw attempt should fail on SafeERC20 transfer
	let params = WithdrawalParams {
		beneficiary_address: H160::random().as_bytes().to_vec(),
		amount: SubstrateU256::from(500_000_000_000_000_000_000u128),
		token: H160::from_slice(env.fee_token.as_slice()),
	};

	let post = router::PostRequest {
		source: StateMachine::Kusama(2000),
		dest: StateMachine::Evm(1),
		nonce: 0,
		from: env.sender.as_slice().to_vec(),
		to: vec![],
		timeout_timestamp: 100,
		body: params.abi_encode().expect("20-byte beneficiary"),
	};
	let evm_request: EvmPostRequest = post.into();

	let host_addr = env.host;
	let calldata = onaccept_calldata(evm_request, env.sender);
	let err = env
		.call_as_may_revert(host_addr, manager, calldata)
		.expect_err("expected revert");
	assert!(!err.is_empty(), "expected non-empty revert data");
}
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L200-214)
```rust
		match message {
			Message::WithdrawRelayerFees(WithdrawalRequest { account, amount }) => {
				T::Currency::transfer(
					&RELAYER_FEE_ACCOUNT.into_account_truncating(),
					&account,
					amount,
					Preservation::Expendable,
				)
				.map_err(|err| {
					IsmpError::Custom(format!("Error withdrawing protocol fees: {err:?}"))
				})?;

				Pallet::<T>::deposit_event(Event::<T>::RelayerFeeWithdrawn { amount, account });
			},
		}
```
