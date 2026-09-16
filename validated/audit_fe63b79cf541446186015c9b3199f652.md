Confirmed: `withdraw()` (evm/src/core/EvmHost.sol:651-660) transfers `params.amount` of `params.token` with no check against outstanding `_requestCommitments` fee obligations. This is exactly analogous to `Unitas.sendPortfolio()` — an authorized function that moves funds out of a pool that also serves as the guaranteed backing/refund reserve for a separate operation the protocol promises will always succeed.

### Title
Host-manager fee-token withdrawal can drain the pool backing outstanding relayer-fee refunds and rewards, causing legitimate request delivery/timeout to revert - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.withdraw()` lets the configured `hostManager` (driven by cross-chain governance dispatch from `pallet-host-executive::withdraw`) transfer an arbitrary amount of the `feeToken` balance to any beneficiary, with no accounting for fees already escrowed against outstanding (undelivered/untimed-out) requests and responses. Because the same `feeToken` balance backs both "protocol revenue available for withdrawal" and "fees owed to relayers/payers for pending cross-chain messages," an authorized (non-malicious, as-designed) revenue withdrawal can leave the host's balance below the sum of its outstanding fee obligations. This mirrors the Unitas defect: reserve funds are used for a secondary purpose (yield/portfolio there, revenue extraction here) without ring-fencing the amount required to satisfy a stated protocol guarantee, so an ordinary relayed message can then revert. [1](#0-0) 

### Finding Description
Every dispatched POST/GET request escrows a relayer fee in `_requestCommitments[commitment].fee`, held as `feeToken` balance on `EvmHost`: [2](#0-1) 

When a relayer delivers a `GetResponse` or the module accepts a `PostRequest`, the host pays the escrowed fee straight out of its current `feeToken` balance via `safeTransfer`: [3](#0-2) 

Likewise, on timeout, the payer is refunded the escrowed fee out of the same pooled balance: [4](#0-3) 

None of these code paths distinguish "the host's spendable revenue" from "fees earmarked for a specific still-open commitment" — they simply assume `IERC20(feeToken()).balanceOf(address(this))` is always ≥ the escrowed amount. But `withdraw()`, callable by `hostManager` for the stated purpose of "withdraw[ing] bridge revenue," moves out an arbitrary `params.amount` of the fee token with zero validation that the remaining balance still covers the sum of all currently escrowed `_requestCommitments` fees: [5](#0-4) 

The withdrawal amount is chosen off-chain by `pallet-host-executive::withdraw`/`pallet-ismp-relayer::withdraw`, based on whatever the governance/relayer-fee-accumulation logic believes is "available," without any on-chain cross-check of the destination `EvmHost`'s currently outstanding fee commitments: [6](#0-5) 

Once the host's `feeToken` balance drops below the outstanding escrowed total, any subsequent relayer delivering a legitimately proven `PostRequest`/`GetResponse`, or submitting a legitimately proven timeout, will hit an `ERC20: transfer amount exceeds balance` revert inside `dispatchIncoming`/`dispatchTimeOut`. Unlike `dispatchIncoming`'s POST path (which tolerates a failed `onAccept` call and deletes the receipt for retry), the relayer-fee `safeTransfer` in the GET-response path and the payer refund `safeTransfer` in both timeout paths have no fallback — a revert there reverts the entire handler transaction, blocking delivery of that message (and any other messages batched with it) until the host's balance is topped back up.

### Impact Explanation
This breaks the same class of guarantee the Unitas report flags: users and relayers submitting fully valid, proven ISMP messages should always be able to have them processed and be paid/refunded, but a routine, intended host-manager withdrawal (not requiring any admin compromise) can transiently make that impossible. Concretely:
- A relayer that already incurred gas cost to deliver a `GetResponse` can be denied its escrowed reward because the transfer reverts.
- A payer whose request has legitimately timed out can be denied their fee refund.
- Because `dispatchTimeOut`/`dispatchIncoming` are invoked by the handler as part of processing a batch of relayed messages, a single underfunded transfer can revert the whole handler call, stalling delivery of otherwise-valid proofs for that batch.

This is a medium-severity availability/fund-freezing issue: it does not let an attacker steal funds directly, but it can freeze/DoS legitimate relayer reward and payer refund transactions and create a "no one can withdraw fees they're owed until governance replenishes the pool" state, echoing the reputational/functional risk in the original report.

### Likelihood Explanation
Likelihood depends on operational parameters governance/relayer withdrawal logic uses to decide "available" balance versus actual outstanding commitments on a given destination `EvmHost`; there is no on-chain enforcement preventing an over-withdrawal, so the safety of the system rests entirely on off-chain bookkeeping in `pallet-host-executive`/`pallet-ismp-relayer` correctly modeling every open request/response fee across every connected `EvmHost`. Any drift (e.g., timing race between accumulation/withdrawal messages in flight and new requests being dispatched, or fee amounts increased via `fundRequest`) can produce a temporary shortfall, and the resulting revert is a straightforward, permissionless consequence reachable by any relayer submitting a normal delivery/timeout message.

### Recommendation
Track total outstanding escrowed fees on `EvmHost` (sum of live `_requestCommitments`/response fee metadata) and have `withdraw()` revert if `params.amount` would bring the `feeToken` balance below that reserved total (analogous to reserving reads before allowing revenue extraction). Alternatively, require `pallet-host-executive`'s withdrawal instruction to be informed by a queryable "reserved" amount on `EvmHost` (e.g., via a GET request) before dispatching the withdraw instruction, so honest governance withdrawals can never strand pending relayer rewards or payer refunds.

### Proof of Concept
1. Multiple users/apps dispatch POST/GET requests via `EvmHost.dispatch(...)`, each escrowing `fee` in `_requestCommitments`, so `feeToken.balanceOf(host)` now equals the sum of all outstanding fees (say, `1000e18`).
2. Governance dispatches a cross-chain withdrawal instructing `hostManager` to call `EvmHost.withdraw({beneficiary, amount: 1000e18, token: feeToken})` — a normal, intended "withdraw bridge revenue" action, exactly as exercised in `HostManagerTest.HostManagerWithdraw`/`test_host_manager_withdraw`. Balance is now `0`. [7](#0-6) 
3. A relayer submits a valid proof of a previously-dispatched GET request's response (or a valid timeout proof for a still-escrowed POST/GET). `EvmHost.dispatchIncoming`/`dispatchTimeOut` attempts `IERC20(feeToken()).safeTransfer(relayer_or_payer, fee)` against a `0` balance and reverts, per: [3](#0-2) 
4. The relayer/payer cannot collect their legitimately owed fee/refund until new fee-token inflow (new dispatches) replenishes the host's balance — an unrestricted-in-theory guarantee ("submit a valid proof, get paid/refunded") is broken by ordinary use of an authorized function.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L841-846)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
```

**File:** evm/src/core/EvmHost.sol (L872-905)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }

    /**
     * @dev Dispatch an incoming POST timeout to the source module
     * @param timeout - timed-out post request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
```

**File:** evm/src/core/EvmHost.sol (L921-948)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** modules/pallets/host-executive/src/lib.rs (L287-322)
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
```

**File:** evm/tests/rust/src/tests/host_manager.rs (L81-118)
```rust
#[test]
fn test_host_manager_withdraw() {
	let mut env = TestEnv::new();
	let manager = host_manager_of(&mut env);

	// Mint 1000e18 fee tokens to the host
	let amount_to_mint = U256::from(1000u128) * U256::from(10u128.pow(18));
	env.call(env.fee_token, mintCall { to: env.host, amount: amount_to_mint }.abi_encode());
	assert_eq!(host_balance(&mut env), amount_to_mint);

	// Build a withdraw request (body = [0] + abi.encode(WithdrawParams)).
	// Withdraw the fee token (non-zero `token`) — the zero address would be
	// the native-ETH path which this test isn't exercising.
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

	// HostManager.onAccept is `restrict(_params.host)` — must call AS the host
	let host_addr = env.host;
	let calldata = onaccept_calldata(evm_request, env.sender);
	env.call_as(host_addr, manager, calldata);

	let withdraw_amount = U256::from(500u128) * U256::from(10u128.pow(18));
	assert_eq!(host_balance(&mut env), amount_to_mint - withdraw_amount);
}
```
