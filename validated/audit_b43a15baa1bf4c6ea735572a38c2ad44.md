### Title
Relayer/governance fee withdrawals can get stuck when `EvmHost` lacks sufficient fee-token balance, because the payout is all-or-nothing and the claim is zeroed before delivery succeeds - (File: `evm/src/core/EvmHost.sol`, `modules/pallets/relayer/src/withdrawal.rs`)

### Summary
`pallet-ismp-relayer`'s `withdraw` extrinsic lets any relayer redeem their accumulated cross-chain delivery fees. It zeroes the relayer's `Fees` balance on Hyperbridge and dispatches an ISMP POST request that, once delivered, causes the destination `EvmHost` to pay out the full amount via `safeTransfer`. If the destination `EvmHost`'s fee-token balance is smaller than the owed amount at delivery time, the transfer reverts entirely (no partial payout, no capping), so the withdrawal fails and cannot be delivered until the host's fee-token balance is replenished - the same "all-or-nothing transfer causes rewards to get stuck" bug class as the referenced SSLV report.

### Finding Description
`pallet_relayer::withdrawal::Pallet::withdraw` reads the relayer's `available_amount` from `Fees` and immediately zeros the entry once the withdrawal request is dispatched, before delivery to the destination is confirmed: [1](#0-0) 

The request is routed to the destination `HostManager`, whose `onAccept` handles the `Withdraw` action by calling `EvmHost.withdraw()` directly, with no try/catch around the app-level call: [2](#0-1) 

`EvmHost.withdraw()` performs an unconditional `safeTransfer` for the full `params.amount` requested, with no cap against the host's actual fee-token balance: [3](#0-2) 

This is confirmed to revert on insufficient balance by the project's own test: [4](#0-3) 

This mirrors the reported SSLV bug class exactly: the accounting side (`Fees` map / relayer's accrued reward) is cleared/committed eagerly, while the payout side transfers the full amount with no fallback to a partial/capped transfer when the paying contract is short on funds. Because the `DispatchPost` for withdrawal is submitted with `timeout: 0` (no timeout), the request commitment persists and delivery can be retried indefinitely, but every attempt will keep reverting for as long as the destination `EvmHost`'s fee-token balance remains below the owed amount, e.g., if governance drained the pool via `HostManager`/`EvmHost.withdraw` for treasury purposes, or if per-chain fee revenue simply hasn't caught up with accumulated relayer rewards on that route: [5](#0-4) 

### Impact Explanation
A relayer's legitimately earned fees become unclaimable (stuck) for an indefinite period whenever the specific destination `EvmHost`'s fee-token balance dips below the claimed amount, which can happen through normal operation (e.g. governance withdrawing accumulated revenue via the same `EvmHost.withdraw` path, or low fee-paying traffic on that route). Since `Fees` was already zeroed at dispatch time on Hyperbridge, the relayer has no way to retrieve a partial amount and must wait for the host balance to be replenished before the withdrawal message can be re-delivered successfully — funds are temporarily frozen and depend on external/governance intervention, the same impact class described in the referenced report (medium severity: rewards get stuck / unavailable for some time).

### Likelihood Explanation
Any unprivileged relayer that has accumulated fees on a given destination chain can trigger this by simply calling `withdraw_fees` when that destination `EvmHost`'s current fee-token balance is less than their owed amount — a state reachable through normal, permissionless operation of the protocol (fee accrual timing mismatches per chain, or governance fee withdrawals). No malicious actor or privileged role is required to trigger the freeze; it's an emergent property of the eager-zero/full-transfer design.

### Recommendation
Cap the payout to the available balance and re-credit any shortfall instead of reverting/losing the difference, mirroring the original report's fix:
- In `EvmHost.withdraw()`, when `params.token != address(0)`, cap the transferred amount to `IERC20(params.token).balanceOf(address(this))` and emit an event/return the actually-transferred amount rather than reverting outright.
- On the Hyperbridge side, don't unconditionally zero `Fees` before confirmed delivery; either credit back any un-delivered/reverted amount, or only debit the amount actually reported as transferred by the destination (e.g., via a response message), so relayers always retain a claim on the true shortfall rather than losing visibility into it once the source-side entry is cleared.

### Proof of Concept
1. On Hyperbridge, relayer accumulates fees via `accumulate_fees`, then calls `withdraw_fees` for destination chain X; `Fees[X][relayer]` is zeroed at `modules/pallets/relayer/src/withdrawal.rs:177` and a POST `Withdraw` request is dispatched.
2. Separately (or concurrently), governance calls the same `withdraw` path on `EvmHost` for chain X (draining its fee-token balance for a treasury sweep), or fee revenue on chain X is simply lower than the relayer's accrued claim.
3. The withdrawal POST request is delivered to `HostManager.onAccept` → `EvmHost.withdraw()`; `IERC20(feeToken).safeTransfer(beneficiary, amount)` reverts because `amount > IERC20(feeToken).balanceOf(address(host))`, matching the behavior verified in `test_host_manager_insufficient_balance` (`evm/tests/rust/src/tests/host_manager.rs:152-181`).
4. The relayer's `Fees` entry on Hyperbridge is already zero; the relayer must wait until chain X's `EvmHost` fee-token balance is replenished by future traffic (or governance action) before any delivery of the same commitment can succeed.

### Citations

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
