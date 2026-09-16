## Analog Found

### Title
Relayer fee entitlement is zeroed before destination-chain payout is confirmed, permanently losing the claim if delivery cannot complete - ([File: modules/pallets/relayer/src/withdrawal.rs])

### Summary
The Tap.sol bug class is: an accounting value representing "amount the caller is entitled to withdraw" is computed, a transfer/dispatch attempting to realize part or all of it is initiated, and the source-side accounting is unconditionally reset to zero/consumed — even when the actual settlement of that amount is not (yet) guaranteed to succeed — permanently stranding the un-delivered remainder. `pallet-ismp-relayer`'s fee withdrawal flow exhibits the same pattern: it reads the relayer's full accrued `Fees` balance, fires off a single one-way ISMP dispatch instructing the destination chain to pay it, and immediately zeroes the `Fees` entry — with no confirmation that the destination-side payout will (or even can) succeed.

### Finding Description
`Pallet::withdraw` in `modules/pallets/relayer/src/withdrawal.rs` implements the relayer fee withdrawal:

1. `available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone())` — reads the relayer's entire accrued, unclaimed balance for a destination chain. [1](#0-0) 
2. An ISMP `DispatchPost` is fired to the destination's `host_manager` (EVM) or `HYPERBRIDGE_MODULE_ID` (substrate), instructing it to pay out `available_amount` in the fee token. [2](#0-1) 
3. Immediately after the dispatch call returns `Ok`, `Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero())` unconditionally zeroes the relayer's balance — before any evidence that the destination chain actually credited the relayer. [3](#0-2) 

The module's own doc comment confirms this design: *"The `Fees` entry is zeroed so the same balance cannot be withdrawn twice… The on-chain effect is just dispatching the message; the destination chain settles the payout when the ISMP request is delivered there."* [4](#0-3) 

On the EVM destination side, the payout is realized by `EvmHost.withdraw`, which performs a plain `IERC20(params.token).safeTransfer(params.beneficiary, params.amount)` with **no check that the host's fee-token balance actually covers `params.amount`**: [5](#0-4) 

Crucially, the same fee-token balance held by `EvmHost` is also the source of funds for a *separate, independent* withdrawal path — governance's "host revenue" withdrawal via `pallet-host-executive::withdraw`, which dispatches its own `WithdrawalParams` to the same `HostManager`/`EvmHost.withdraw` with no reservation logic protecting relayers' already-accrued, not-yet-delivered fee entitlements: [6](#0-5) 

There is no shared accounting between "relayer unclaimed fees en route" and "governance-withdrawable host revenue" — both draw from the same on-chain ERC-20 balance of `EvmHost`. If governance (or repeated fee-token changes/host-revenue sweeps) drains the balance below the sum of relayers' in-flight `WithdrawRelayerFees`/`Withdraw` POSTs, those payouts will revert on delivery (`safeTransfer` reverts on insufficient balance), yet the relayer's `Fees` record on Hyperbridge is already zero — the claim cannot be recomputed or re-dispatched from anything but the same (already-cleared) source balance. This is functionally identical to the Tap.sol pattern: the withdrawable amount is computed once, an attempt to move it is made, and the internal ledger is cleared regardless of whether the movement can actually complete, with no mechanism to later reclaim the shortfall.

### Impact Explanation
A relayer's legitimately earned, already-verified (via delivered-message state proofs) fee balance can become permanently unrecoverable if the destination `EvmHost`'s fee-token balance is insufficient at delivery time and never becomes sufficient again before the underlying request's supporting proof/commitment becomes unobtainable (offchain storage retention, MMR leaf pruning, or simply because the relayer has no further lever to re-trigger accounting once `Fees` is zero and the nonce has advanced). This directly undermines "relayer fee and reward accounting," an explicitly in-scope Hyperbridge invariant — relayers are the permissionless actors incentivized to deliver messages, and a design that can silently zero their reward ledger against an unconfirmed transfer erodes the fee-based security assumption of the whole delivery network.

### Likelihood Explanation
This does not require any malicious actor: it can be triggered purely by the normal, permissionless operation of the protocol — a relayer earns fees via ordinary message delivery (accumulate) and calls the unsigned, permissionless `withdraw` extrinsic (reachable by any relayer address with a valid signature), while governance independently and validly withdraws "host revenue" from the exact same commingled EVM balance via `host-executive::withdraw`. No coordination or malice between the two paths is required — a normal governance sweep timed against relayer withdrawals is sufficient to trigger the shortfall.

### Recommendation
Do not zero the `Fees` entry until destination-side settlement is confirmed (e.g., via an acknowledgement/response message back to Hyperbridge, or by only debiting `Fees` on confirmed delivery rather than at dispatch time). Alternatively, reserve/earmark relayer-owed fee-token balances on the destination `EvmHost` so `host-executive::withdraw` (governance) cannot draw the balance below the sum of relayers' outstanding, in-flight withdrawal requests, and make `EvmHost.withdraw` explicitly check `amount <= balance - reservedForRelayers` rather than relying on an unconditioned `safeTransfer`.

### Proof of Concept
1. Relayer R accumulates a `Fees[EVM-chain][R] = X` balance on Hyperbridge via `accumulate_fees` after delivering messages. [7](#0-6) 
2. R calls `Pallet::withdraw`, which dispatches a POST to `EvmHost`'s `HostManager` for amount `X` and immediately sets `Fees[EVM-chain][R] = 0`. [8](#0-7) 
3. Before this POST is delivered/relayed, governance calls `host-executive::withdraw` to sweep the `EvmHost`'s fee-token balance down below `X` (a routine operation, not requiring any wrongdoing) via `HostManager.onAccept` -> `EvmHost.withdraw`. [9](#0-8) [5](#0-4) 
4. When R's withdrawal POST is eventually delivered to `EvmHost`, `safeTransfer` reverts due to insufficient balance; `dispatchIncoming` marks it retryable, but R's Hyperbridge-side `Fees` entry is already `0` and cannot be restored except by the balance recovering and a relayer resubmitting the same never-expiring request — which may never happen if the balance never recovers or the supporting proof/commitment becomes unavailable, permanently forfeiting R's fee.

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

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-177)
```rust
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}

		let dispatcher = <T as Config>::IsmpHost::default();

		Nonce::<T>::try_mutate(address.clone(), withdrawal_data.dest_chain, |value| {
			*value += 1;
			Ok::<(), ()>(())
		})
		.map_err(|_| Error::<T>::ErrorCompletingCall)?;

		let beneficiary_address = withdrawal_data.beneficiary.clone().unwrap_or(address.clone());
		let (to, body) = match withdrawal_data.dest_chain {
			s if s.is_substrate() => (
				HYPERBRIDGE_MODULE_ID.to_vec(),
				Message::WithdrawRelayerFees(WithdrawalRequest {
					amount: available_amount.low_u128(),
					account: AccountId32::try_from(&beneficiary_address[..])
						.map_err(|_| Error::<T>::InvalidPublicKey)?,
				})
				.encode(),
			),
			_ => {
				let HostParam::EvmHostParam(params) =
					HostParams::<T>::get(withdrawal_data.dest_chain)
						.ok_or_else(|| Error::<T>::MissingMangerAddress)?;

				let body = WithdrawalParams {
					beneficiary_address: beneficiary_address.clone(),
					amount: available_amount.into(),
					token: params.fee_token,
				}
				.abi_encode()
				.map_err(|_| Error::<T>::InvalidPublicKey)?;

				(params.host_manager.0.to_vec(), body)
			},
		};

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

**File:** modules/pallets/host-executive/src/lib.rs (L287-333)
```rust
		/// Issues a call to withdraw the protocol fees from an evm chain
		#[pallet::weight(T::DbWeight::get().writes(1))]
		#[pallet::call_index(4)]
		pub fn withdraw(
			origin: OriginFor<T>,
			state_machine: StateMachine,
			withdrawal_params: WithdrawalParams,
		) -> DispatchResult {
			T::HostExecutiveOrigin::ensure_origin(origin)?;

			ensure!(state_machine.is_evm(), Error::<T>::UnsupportedStateMachine);

			let HostParam::EvmHostParam(params) = HostParams::<T>::get(state_machine)
				.ok_or_else(|| Error::<T>::UnknownStateMachine)?;

			let data = withdrawal_params
				.abi_encode()
				.map_err(|_| Error::<T>::InvalidBeneficiaryAddress)?;

			let post = DispatchPost {
				dest: state_machine,
				from: PALLET_ID.to_bytes(),
				to: params.host_manager.0.to_vec(),
				timeout: 0,
				body: data,
			};

			let dispatcher = <T as Config>::IsmpHost::default();

			// Account is not useful in this case
			dispatcher
				.dispatch_request(
					DispatchRequest::Post(post),
					FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
				)
				.map_err(|_| Error::<T>::DispatchFailed)?;

			Self::deposit_event(Event::<T>::Withdraw {
				address: sp_runtime::BoundedVec::truncate_from(
					withdrawal_params.beneficiary_address,
				),
				state_machine,
				amount: withdrawal_params.amount,
			});

			Ok(())
		}
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp_relayer.rs (L930-971)
```rust
#[test]
fn test_withdrawal_fees() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let pair = sp_core::sr25519::Pair::from_seed_slice(H256::random().as_bytes()).unwrap();
		let public_key = pair.public().0.to_vec();
		pallet_ismp_relayer::Fees::<Test>::insert(
			StateMachine::Kusama(2000),
			public_key.clone(),
			U256::from(250_000_000_000_000_000_000u128),
		);
		let message = message(0, StateMachine::Kusama(2000), None);
		let signature = pair.sign(&message).0.to_vec();

		let withdrawal_input = WithdrawalInputData {
			signature: Signature::Sr25519 { public_key: public_key.clone(), signature },
			beneficiary: None,
			dest_chain: StateMachine::Kusama(2000),
		};

		pallet_ismp_relayer::Pallet::<Test>::withdraw_fees(
			RuntimeOrigin::none(),
			withdrawal_input.clone(),
		)
		.unwrap();
		assert_eq!(
			pallet_ismp_relayer::Fees::<Test>::get(StateMachine::Kusama(2000), public_key.clone()),
			U256::zero()
		);

		assert_eq!(
			pallet_ismp_relayer::Nonce::<Test>::get(public_key, StateMachine::Kusama(2000)),
			1
		);

		assert!(pallet_ismp_relayer::Pallet::<Test>::withdraw_fees(
			RuntimeOrigin::none(),
			withdrawal_input.clone()
		)
		.is_err());
	})
}
```

**File:** evm/src/core/HostManager.sol (L134-159)
```text
    function onAccept(IncomingPostRequest calldata incoming)
        external
        override
        restrict(msg.sender, _params.host)
        restrict(incoming.relayer, _params.admin)
    {
        PostRequest calldata request = incoming.request;
        // Only the Hyperbridge parachain can send requests to this module.
        if (!request.source.equals(IHost(_params.host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
        } else if (action == OnAcceptActions.SetHostParam) {
            HostParams memory hostParams = abi.decode(request.body[1:], (HostParams));
            IHostManager(_params.host).updateHostParams(hostParams);
        } else if (action == OnAcceptActions.SetAdmin) {
            // Rotates the governance relayer.
            address newAdmin = abi.decode(request.body[1:], (address));
            if (newAdmin == address(0)) revert InvalidAdmin();
            emit AdminUpdated({previous: _params.admin, current: newAdmin});
            _params.admin = newAdmin;
        }
    }
```
