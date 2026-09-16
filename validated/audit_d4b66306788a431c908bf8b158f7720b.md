### Title
Relayer fee balance is zeroed on Hyperbridge before the destination-chain payout is confirmed, permanently losing funds if the destination `withdraw` call reverts - (File: modules/pallets/relayer/src/withdrawal.rs)

### Summary
`pallet-ismp-relayer`'s `withdraw` function dispatches an ISMP POST request that will eventually trigger a token transfer to the relayer's beneficiary on the destination chain (`EvmHost.withdraw` via `HostManager`, or the substrate `RefundingRouter`), and then unconditionally zeroes the relayer's `Fees` entry on Hyperbridge in the same transaction, before any confirmation that the destination-side transfer actually succeeds.

### Finding Description
`Pallet::withdraw` reads `available_amount` from `Fees::<T>::get(...)`, builds a `WithdrawalParams`/`WithdrawalRequest` payload, dispatches it as a POST request via `dispatcher.dispatch_request(...)`, and immediately after — in the very same call, regardless of the eventual outcome of that dispatched message — sets `Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero())`. [1](#0-0) 

`dispatch_request` only guarantees that the message was accepted into the outbound queue on Hyperbridge — not that it will be executed successfully on the destination chain. The module doc comment for this file explicitly acknowledges the message "will not timeout" and settlement happens later, entirely decoupled from the balance-zeroing step: [2](#0-1) 

On the EVM destination side, the corresponding `EvmHost.withdraw` (called only by the authorized `HostManager`) performs the actual transfer and can revert, e.g. on insufficient balance for an ERC-20 `safeTransfer`, or `WithdrawalFailed` for a failed native transfer: [3](#0-2) 

This is confirmed by the existing test `test_host_manager_insufficient_balance`, which shows the destination-side withdrawal reverting when the host lacks the requested fee-token balance: [4](#0-3) 

Because the `Fees` entry is zeroed on Hyperbridge unconditionally at dispatch time — not upon confirmed destination delivery — a reverted or otherwise failed destination-side transfer (e.g., due to a temporary balance shortfall on the `EvmHost`, an admin/relayer misconfiguration in `HostManager`, or a `SetHostParam`/`SetAdmin` race that changes `host_manager`/fee token before delivery) leaves the relayer with zero accrued balance on Hyperbridge and no successfully delivered payout on the destination chain. There is no retry, re-credit, or reconciliation path coded for this failure mode; the fee is simply gone. This mirrors the reported bug class: an irreversible/destructive state change (zeroing the balance) proceeds without regard to whether the paired token transfer succeeds, and the resulting fund-loss/ownership implications are undocumented.

### Impact Explanation
This is a real-funds loss for relayers, the entities Hyperbridge economically depends on to deliver cross-chain messages. If the destination transfer fails after the source-side `Fees` entry has already been zeroed, the accrued relayer fee for that withdrawal is permanently unrecoverable through the documented flow — there's no code path shown that re-credits `Fees` on a failed/reverted delivery. Given relayers rely on `pallet-ismp-relayer` + `pallet-host-executive` for revenue accrual and withdrawal, an unrecoverable balance loss undermines the entire fee-incentive model relied upon for message delivery (a core "relayer fee and reward accounting" surface explicitly in scope).

### Likelihood Explanation
The precondition for the destination transfer to fail (e.g., insufficient `feeToken` balance held by `EvmHost` at the moment the request lands, or a mismatched fee token/host-manager configuration mid-flight) is plausible in production: fee revenue accrues gradually and withdrawal timing is not synchronized with the exact available balance on each destination chain, and host-executive periodically triggers protocol-level withdrawals from the same balance pool that funds relayer payouts. No malicious actor is required — this can occur from ordinary operational conditions (race between protocol withdrawal and relayer withdrawal draining the same on-chain balance, or delayed message delivery during which balance is drawn down elsewhere).

### Recommendation
Do not zero (or don't permanently zero) the `Fees` entry until receipt of a confirmed success response from the destination chain. Options:
1. Move the zeroing to happen only after an ISMP response confirming the destination-side transfer succeeded (dispatch as a request expecting a response/timeout callback), refunding/re-crediting `Fees` on timeout or failure response.
2. At minimum, explicitly document this design trade-off (as the analog report recommends) — clarify that a destination-side revert after the source-side balance is zeroed results in permanent, unrecoverable loss of the relayer's fee, and that no automatic reconciliation exists.
3. Consider having the destination-side manager emit a distinguishable failure signal (rather than reverting silently) so any accounting/monitoring tooling can detect stuck payouts, and provide a governance-driven manual re-credit path for confirmed lost withdrawals.

### Proof of Concept
1. A relayer accrues fees via `accumulate_fees`, giving them `Fees::<T>::get(dest_chain, relayer) = X` on Hyperbridge.
2. `EvmHost` on the destination chain temporarily holds less than `X` in `feeToken` balance (e.g., because `pallet-host-executive::withdraw` recently drained protocol revenue from the same pool, or fee-token was rotated via `HostManager.SetHostParam` before delivery).
3. Relayer calls `withdraw`, which dispatches the `WithdrawalParams` POST request and, in the same transaction, sets `Fees::<T>::insert(dest_chain, relayer, U256::zero())` per `modules/pallets/relayer/src/withdrawal.rs` lines 160-187.
4. When the message is eventually delivered and executed on the destination chain, `EvmHost.withdraw` (`evm/src/core/EvmHost.sol` lines 651-660) reverts due to insufficient balance (as reproduced by `test_host_manager_insufficient_balance`, `evm/tests/rust/src/tests/host_manager.rs` lines 152-181).
5. The relayer's `Fees` balance is already zero on Hyperbridge, and the destination transfer never completed — the fee amount `X` is permanently lost with no re-credit mechanism.

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

**File:** modules/pallets/relayer/src/withdrawal.rs (L160-187)
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

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
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
