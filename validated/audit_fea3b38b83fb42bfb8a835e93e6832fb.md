### Title
`EvmHost.withdraw` pays out fee-token revenue without checking free balance, blocking relayers from collecting fees on in-flight GET/POST responses and timeouts - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.withdraw()` transfers `params.amount` of `feeToken()` straight out of the host's ERC20 balance to a beneficiary with no check that the remaining balance still covers the relayer fees owed on requests that were dispatched *from* this host and are still pending delivery of their response/timeout. Those pending fees sit in the exact same ERC20 balance and are paid out later via unconditional `safeTransfer` calls in `dispatchIncoming`/`dispatchTimeOut`. Draining the balance via `withdraw()` can make those later transfers revert, blocking legitimate message delivery, exactly analogous to `amoMinterBorrow` lacking a `freeCollateralBalance` check before transferring collateral out of the Ubiquity pool.

### Finding Description
When a user dispatches a POST/GET request from an `EvmHost`, the relayer fee is pulled into the host's own `feeToken` balance and only tracked per-commitment in `_requestCommitments[commitment].fee`: [1](#0-0) 

That fee is paid out later, from the same pooled ERC20 balance, when the response/timeout is processed by the handler: [2](#0-1) [3](#0-2) [4](#0-3) 

There is no separate escrow/reservation for these pending fees — they are indistinguishable from the host's general `feeToken` balance (which also holds accumulated relayer withdrawal balances and protocol revenue).

Separately, `withdraw()` (restricted to `_hostParams.hostManager`) unconditionally transfers `params.amount` of `feeToken` out of the host to a beneficiary, with no check against a "free" balance concept: [5](#0-4) 

This function is reachable by an ordinary, unprivileged relayer: `pallet-relayer::withdraw` lets any relayer who has legitimately accumulated `Fees` (via `accumulate_fees` proofs of past deliveries) sign a withdrawal, which dispatches a POST to the destination `HostManager`: [6](#0-5) 

`HostManager.onAccept` then calls `IHostManager(_params.host).withdraw(withdrawParams)` for the `Withdraw` action, with no balance-reservation logic in between: [7](#0-6) 

Because `EvmHost.withdraw()` never checks that `feeToken().balanceOf(address(this))` minus the sum of outstanding `_requestCommitments[...].fee` (relayer fees owed on pending outbound dispatches from this host) remains non-negative, a legitimate relayer fee withdrawal (or a protocol-revenue withdrawal via `pallet-host-executive::withdraw`, which follows the identical code path) can drain the contract's `feeToken` balance below what is required to pay out relayer fees on requests dispatched earlier from this same host that are still awaiting their GET response or timeout.

### Impact Explanation
When the balance is insufficient, the subsequent `safeTransfer` calls inside `dispatchIncoming(GetResponse,...)`, `dispatchTimeOut(GetRequestTimeout,...)`, and `dispatchTimeOut(PostRequestTimeout,...)` revert (SafeERC20 reverts on failed ERC20 transfer). Unlike the sibling `dispatchIncoming(PostRequest,...)` path, which is designed to tolerate destination-call failure by early-returning, these three functions have no fallback for a failed fee transfer — the whole call, and thus the entire delivery of that GET response / timeout (which is invoked by the trusted `handler`, restricted via `restrict(_hostParams.handler)`), reverts. This:
- Blocks legitimate relayers from being paid for GET-response/timeout deliveries they already performed correctly, and
- Makes the underlying message (GET response, GET timeout, or POST timeout) permanently non-deliverable through the batch until the host's `feeToken` balance is topped back up — i.e. "a route unable to deliver messages," and a freezing of the fee owed to the relayer and of the state transition the message was meant to carry.

This mirrors the Ubiquity issue precisely: an authorized withdrawal path (`amoMinterBorrow` / `EvmHost.withdraw`) moves funds out of a shared pool without checking a "free" balance that accounts for amounts already earmarked for other claimants (`unclaimedPoolCollateral` / pending `_requestCommitments[...].fee`), causing later legitimate claims to fail.

### Likelihood Explanation
No malicious governance/admin action is required: any relayer that has honestly accumulated fees can trigger `pallet-relayer::withdraw` for a large amount at any time, and the periodic auto-withdraw task in the relayer software does this routinely and automatically: [8](#0-7) 

Because outstanding per-request relayer fees are never reserved separately from the host's general balance, ordinary, expected relayer/host-executive withdrawal activity combined with normal outstanding-request volume is sufficient to trigger the condition — no attacker collusion is needed, only unfortunate but foreseeable timing between two legitimate flows sharing the same pool.

### Recommendation
Track the sum of outstanding relayer fees committed to undelivered requests dispatched from the host (e.g., a running total incremented in `dispatch()`/`dispatchGet` fee-taking paths and decremented in `dispatchIncoming`/`dispatchTimeOut`), and have `EvmHost.withdraw()` (and any other path that pulls `feeToken` out, including host-executive protocol-revenue withdrawals) check that:

```solidity
IERC20(feeToken()).balanceOf(address(this)) - outstandingCommittedFees >= params.amount
```
before transferring, reverting otherwise. Alternatively, escrow relayer fees for pending requests in a way that is not commingled with governance/relayer-withdrawable revenue.

### Proof of Concept
1. Multiple users dispatch POST/GET requests from `EvmHost` with non-zero `fee`, each pulling `fee` into the host's `feeToken` balance via `dispatch()` (`evm/src/core/EvmHost.sol:930-931`), with `_requestCommitments[commitment].fee` recording the amount owed later.
2. Before those requests' responses/timeouts are delivered, a relayer with a large accumulated `Fees` balance on `pallet-relayer` calls `withdraw` for that state machine; this dispatches a POST that `HostManager.onAccept` routes to `EvmHost.withdraw()`, transferring `params.amount` out of the host's `feeToken` balance with no free-balance check (`evm/src/core/EvmHost.sol:651-658`).
3. If `params.amount` plus already-spent balance exceeds `balanceOf(host) - sum(outstanding _requestCommitments fees)`, the host's `feeToken` balance is now insufficient to cover the pending commitments.
4. When the handler later delivers one of the pending GET responses or timeouts, `IERC20(feeToken()).safeTransfer(relayer, fee)` in `dispatchIncoming(GetResponse,...)` / `dispatchTimeOut(...)` (`evm/src/core/EvmHost.sol:841-847`, `872-877`, `901-906`) reverts due to insufficient balance, reverting the entire delivery call and leaving that relayer unpaid and the message undelivered until the host is refunded.

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

**File:** evm/src/core/EvmHost.sol (L872-877)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L901-906)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
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

**File:** modules/pallets/relayer/src/withdrawal.rs (L144-159)
```rust
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
```

**File:** evm/src/core/HostManager.sol (L134-150)
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
```

**File:** tesseract/messaging/messaging/src/fees.rs (L120-141)
```rust
					}

					let amount = hyperbridge.available_amount(client.clone(), &chain).await?;
					let fee_token_decimals = client.fee_token_decimals().await?;
					let min_amount: U256 = (config
						.minimum_withdrawal_amount
						.map(|val| std::cmp::max(val, 10))
						.unwrap_or(100) as u128 *
						10u128.pow(fee_token_decimals.into()))
					.into();
					if amount < min_amount {
						tracing::info!(
							target: crate::LOG_TARGET, unclaimed = %amount,
							min = %min_amount,
							"balance below threshold; skipping",
						);
						return Ok::<_, anyhow::Error>(());
					}

					let amount_usd = amount / U256::from(10u128.pow(fee_token_decimals.into()));
					tracing::info!(target: crate::LOG_TARGET, amount_usd = %amount_usd, "submitting withdrawal request");
					let results = hyperbridge.withdraw_funds(client.clone(), chain).await?;
```
