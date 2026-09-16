Confirmed: `EvmHost.withdraw` (evm/src/core/EvmHost.sol:651-660) uses `SafeERC20.safeTransfer` for ERC20 fee tokens, which reverts the entire `onAccept` call (and therefore the whole ISMP message-handling transaction) if the host's fee-token balance is insufficient — exactly as demonstrated in `evm/tests/rust/src/tests/host_manager.rs` `test_host_manager_insufficient_balance` (lines 152-182). This confirms delivery-time failure is a real, reachable outcome, not a hypothetical, and it never rolls back `Fees` on the source chain.

### Title
Relayer's accrued fee balance is zeroed on dispatch before destination-chain disbursement is confirmed, permanently losing funds on delivery failure - (File: modules/pallets/relayer/src/withdrawal.rs)

### Summary
`Pallet::<T>::withdraw` in `pallet-ismp-relayer` reads the relayer's `available_amount` from the `Fees` storage map, dispatches an asynchronous ISMP POST request instructing the destination chain (via `HostManager`/`EvmHost::withdraw` or the substrate `HyperbridgeWithdrawalModule`) to pay that amount to the beneficiary, and then unconditionally zeroes the `Fees` entry — all within the same extrinsic, before there is any confirmation that the destination-chain disbursement will ever succeed.

### Finding Description
In `modules/pallets/relayer/src/withdrawal.rs`, `Pallet::withdraw` computes `available_amount` from `Fees::<T>::get(...)`, builds a `DispatchPost` with `timeout: 0` (never times out) that tells the destination `HostManager` to pay `available_amount` to the beneficiary, dispatches it, and then does: [1](#0-0) 
```
dispatcher.dispatch_request(...)...;
Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());
Self::deposit_event(...);
```
The `Fees` balance is deleted to zero the instant the outbound POST is dispatched — not when the destination confirms payout. On the EVM side, the eventual handler is `EvmHost::withdraw`, which uses `SafeERC20.safeTransfer` for ERC20 fee tokens: [2](#0-1) 
```
function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
    if (params.token == address(0)) {
        (bool sent,) = params.beneficiary.call{value: params.amount}("");
        if (!sent) revert WithdrawalFailed();
    } else {
        IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
    }
    ...
}
```
If the `EvmHost`'s fee-token balance is insufficient to cover `params.amount` (e.g. protocol revenue on that destination hasn't yet accumulated enough, was already drained by another concurrent withdrawal/governance action, or the fee token was swapped/changed), `safeTransfer` reverts the entire `onAccept` call, as directly demonstrated by the test: [3](#0-2) 
Because the request never times out (`timeout: 0`), it stays "in flight" and can be resubmitted by relayers indefinitely, but there is no mechanism anywhere in `pallet-ismp-relayer` to re-credit `Fees` if the destination-side payout never succeeds. The relayer's `Fees` entry has already been permanently set to zero on the source chain the moment the withdrawal was dispatched: [4](#0-3) 
This is structurally the same root cause as the reported `MainVault.withdrawAllowance()` bug: the accounting entry that backs a claim is destroyed based on the *requested* amount rather than the amount actually confirmed as delivered, so any shortfall between "recorded balance" and "successfully disbursed balance" is permanently and irrecoverably lost to the user (here, the relayer).

### Impact Explanation
Any relayer who has accumulated protocol fees can lose that entire balance permanently if the destination chain cannot fulfill the disbursement at delivery time — a condition entirely outside the relayer's control (destination host under-capitalized for that fee token, a fee-token migration in progress, or another relayer/governance action draining the host's balance between accumulation and delivery). Since `Fees` is zeroed unconditionally and there is no compensating/restoring path on delivery failure, this is a permanent loss of legitimately earned relayer rewards — a real accounting/fund-safety defect reachable by any relayer through the normal, permissionless `withdraw_fees` extrinsic.

### Likelihood Explanation
This requires no malicious actor: normal operational conditions (fee token balance changes on the destination host between the relayer's `withdraw` call and eventual `onAccept` execution, especially under concurrent withdrawals by multiple relayers or during a fee-token swap) can trigger the revert path in `EvmHost::withdraw`. The relayer has no way to detect or prevent this before submitting, and by the time delivery fails, `Fees` has already been zeroed on Hyperbridge with no recovery mechanism.

### Recommendation
Do not zero `Fees` at dispatch time. Instead, track the withdrawal as "pending" and only clear/decrement `Fees` once the destination chain has confirmed successful disbursement (e.g., via a response/callback path), or restore the `Fees` balance (or the shortfall) if the destination-side execution ultimately reverts or the request is otherwise proven undeliverable. At minimum, mirror the ERC20-vault fix pattern: only clear the amount that was actually confirmed disbursed, never delete the full recorded balance speculatively.

### Proof of Concept
1. Relayer accumulates `250e18` in `Fees` for `StateMachine::Evm(X)` via `accumulate_fees`.
2. Destination `EvmHost` for chain `X` currently holds less than `250e18` of the fee token (e.g., protocol revenue hasn't accrued that much yet, or another relayer/governance withdrawal just drained it).
3. Relayer calls `withdraw_fees` — `Pallet::withdraw` dispatches the POST request and immediately sets `Fees::<T>::insert(X, relayer, U256::zero())` (`modules/pallets/relayer/src/withdrawal.rs:177`).
4. When the POST is eventually delivered and executed by `HostManager::onAccept` → `EvmHost::withdraw`, `IERC20(feeToken).safeTransfer(beneficiary, 250e18)` reverts because the host's balance is insufficient (as reproduced by `test_host_manager_insufficient_balance`).
5. The relayer's `Fees` entry for chain `X` remains `0` forever; there is no code path that restores it. The relayer has permanently lost the `250e18` of legitimately earned fees.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-123)
```rust
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L169-184)
```rust
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
```

**File:** evm/src/core/EvmHost.sol (L651-659)
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
