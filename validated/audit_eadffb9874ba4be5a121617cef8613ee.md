### Title
`EvmHost.withdraw` lets cross-chain governance drain fee-token balance reserved for pending relayer-fee refunds/rewards, causing delivery and timeout callbacks to revert - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.withdraw` (invoked via `HostManager.onAccept` cross-chain governance) transfers an arbitrary `params.amount` of the fee token out of the host contract with no check against fee-token amounts that are already earmarked for in-flight requests. The same fee-token balance is shared between "withdrawable bridge revenue" and per-request relayer-fee escrow (`_requestCommitments[commitment].fee`), so a normal revenue withdrawal executed while requests are still pending can leave the balance too low to pay out the relayer on successful delivery or to refund the payer on timeout — the same "privileged withdrawal races an escrow-backed balance and there is no accounting to prevent over-withdrawal" bug class as the reported `claim_revenue`/`withdraw_token` issue.

### Finding Description
`EvmHost` collects relayer fees from applications dispatching POST/GET requests and holds them in the same `feeToken()` ERC-20 balance as any other bridge revenue. `dispatch()` collects `post.fee` from the caller into the host's own balance [1](#0-0) , and that fee is tracked per-commitment in `_requestCommitments[commitment].fee` [2](#0-1) . When the request is later delivered or times out, the host pays that escrowed fee back out of its balance: on GET delivery, `IERC20(feeToken()).safeTransfer(relayer, fee)` [3](#0-2) , and on POST/GET timeout, `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` [4](#0-3) .

Separately, `IHostManager.withdraw` allows cross-chain governance to pull "bridge revenue" out of the same contract balance:
```solidity
function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
    if (params.token == address(0)) {
        (bool sent,) = params.beneficiary.call{value: params.amount}("");
        if (!sent) revert WithdrawalFailed();
    } else {
        IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
    }
    emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
}
``` [5](#0-4) 

There is no invariant anywhere in this function, or in `dispatch()`/`dispatchTimeOut()`, that reserves the sum of all outstanding `_requestCommitments[*].fee` before allowing a `withdraw()` to execute. The contract's own test suite confirms `withdraw` will simply run against whatever balance is present and reverts only when the balance is literally insufficient for the requested amount (`test_host_manager_insufficient_balance`) [6](#0-5)  — i.e., the contract has no concept of "reserved" vs "free" balance, exactly mirroring the launchpad's `claim_revenue` transferring against `token_stats.revenue` without checking `stats_pay_token`'s true available (non-escrowed) balance.

This is structurally the same defect as the analog report: a threshold/accounting-free privileged withdrawal path draining a token balance that is simultaneously the source of funds for a separate, legitimate class of pending withdrawals (there: user `withdraw_token` reclaims; here: relayer fee payout / payer timeout refund).

### Impact Explanation
If a normal, non-malicious governance withdrawal of accumulated protocol/bridge revenue is dispatched while there are still outstanding dispatched requests whose relayer fee is sitting in the same balance, the withdrawal can reduce the fee-token balance below the sum of escrowed fees. When those pending requests are subsequently delivered or time out, the `safeTransfer` calls in `dispatchIncoming`'s GET-response handling and in both `dispatchTimeOut` overloads will revert due to insufficient balance. Because `dispatchTimeOut` first deletes the request commitment and only re-persists it for retry if the *module callback* fails [7](#0-6) , a revert in the final `safeTransfer` step (which happens *after* the module callback succeeds) is not caught/retried by that guard — the relayer or the fee payer is left permanently unable to collect their entitled fee/refund for that request, a concrete freezing of funds reachable from a single relayed/timed-out ISMP message. High impact (frozen relayer rewards / payer refunds, breaking delivery incentives across the whole bridge), and the likelihood is Medium since it only requires ordinary governance revenue-collection cadence to overlap with a set of in-flight requests whose fees have not yet been paid out — no attacker or malicious actor is required.

### Likelihood Explanation
Governance/treasury withdrawals of "bridge revenue" are an expected, routine operation (this is exactly the operation `IHostManager.withdraw` exists for), and EvmHost has many chains, many concurrently in-flight requests, and no reserved-balance bookkeeping to prevent a routine sweep from cutting into escrowed relayer fees. This does not require any malicious behavior by governance — only that the withdrawal amount is computed from an off-chain revenue estimate that does not subtract pending relayer-fee escrow, which is a very plausible/likely operational scenario, not an edge case requiring subverted keys.

### Recommendation
Track a running total of currently-escrowed relayer fees (sum of `_requestCommitments[*].fee` for undelivered/untimed-out requests) and enforce `withdraw()` (and any other beneficiary-facing drain path) to only allow withdrawal of `balance - totalEscrowedFees`, i.e. mirror one of the report's two recommended fixes: either (1) disallow/cap withdrawal so it can never dip below the sum of unresolved relayer-fee escrow, or (2) restructure so relayer-fee escrow is held in a separate ledger/vault from freely withdrawable revenue, so a revenue sweep can never touch funds owed for pending request delivery/timeout.

### Proof of Concept
1. App A dispatches a POST request via `EvmHost.dispatch` with `fee = F`, paid into the host's fee-token balance and recorded at `_requestCommitments[commitment].fee = F` [1](#0-0) .
2. Before the request is delivered or times out, cross-chain governance calls `IHostManager.withdraw(WithdrawParams{ beneficiary, amount = fullFeeTokenBalance, token = feeToken() })`, which `EvmHost.withdraw` executes unconditionally against the full balance [5](#0-4) , draining the balance below `F`.
3. Either the request is later delivered as a GET (host attempts `IERC20(feeToken()).safeTransfer(relayer, fee)` [3](#0-2) ) or it times out (host attempts `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` after the module timeout callback succeeds [8](#0-7) ) — both revert due to insufficient balance, and since the commitment was already deleted for replay protection before the transfer step in the success path, the relayer/payer cannot recover the owed fee.

Note: I was not able to fully trace the exact ordering/retry semantics of the GET-delivery success path (`dispatchIncoming`/`handleGetResponses`) beyond the snippet shown, since the index does not surface the complete function; a Devin session with full repo access would be needed to confirm whether any retry guard exists there identical to `dispatchTimeOut`'s pattern.

### Citations

**File:** evm/src/core/EvmHost.sol (L117-118)
```text
    // commitment of all outgoing requests and amount put up for relayers.
    mapping(bytes32 => FeeMetadata) private _requestCommitments;
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

**File:** evm/src/core/EvmHost.sol (L841-847)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L856-906)
```text
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

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
    }
```

**File:** evm/src/core/EvmHost.sol (L921-930)
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
