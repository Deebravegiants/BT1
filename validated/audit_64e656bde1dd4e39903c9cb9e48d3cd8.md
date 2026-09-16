### Title
Single Failing Token Transfer in Batched Post-Request Delivery Can Permanently Block Withdrawal/Escrow Release for All Other Requests in the Same Batch - ([File: evm/src/core/HandlerV2.sol])

### Summary
`HandlerV2.handlePostRequests()` iterates over a batch of proven `PostRequestLeaf`s and calls `host.dispatchIncoming(leaf.request, _msgSender())` for each one with no isolation (no try/catch). `EvmHost.dispatchIncoming` invokes the destination application's `onAccept` directly. Applications that release escrowed funds on `onAccept` — such as `IntentGatewayV2.withdraw()` / `IntentsBase._withdraw()` (token redemption for intents) and `HostManager`'s withdrawal handling for relayer-fee payouts — perform raw ERC20 transfers to a beneficiary inside this call path. If any single transfer in the batch reverts (blacklisted beneficiary, fee-on-transfer/hook token, or any other reason a transfer can fail), the revert propagates all the way up through `dispatchIncoming` and reverts the entire `handlePostRequests` transaction, so **no request in that batch is delivered** — not just the poisoned one.

### Finding Description
`HandlerV2.handlePostRequests` (lines 181–210) verifies the merkle multiproof for `requestsLen` requests and then dispatches every one of them in a plain loop: [1](#0-0) 

`dispatchIncoming` is `external restrict(_hostParams.handler)` on `EvmHost` and forwards the call to the destination app's `onAccept`: [2](#0-1) 

Downstream, apps that redeem escrow directly transfer tokens to attacker/user-controlled beneficiaries during `onAccept`/`onGetResponse` without isolating failures: [3](#0-2) [4](#0-3) 

The relayer-fee withdrawal path is structurally identical: `pallet-ismp-relayer` dispatches a `WithdrawalParams` POST with `timeout: 0` (never times out) to the destination `HostManager`, which performs an ERC20 transfer to the beneficiary on `onAccept`: [5](#0-4) [6](#0-5) 

Because none of these dispatch-to-module calls are wrapped in `try/catch`, any of the standard failure modes described in the report — a blacklisted beneficiary address (e.g., USDT), a token with `_beforeTokenTransfer`/`_afterTokenTransfer` hooks that revert or grief gas, or any other transfer-time revert — causes `dispatchIncoming` to revert, which propagates out of the `for` loop in `handlePostRequests` and reverts the *entire batched delivery transaction*. Relayers commonly batch multiple unrelated requests (from different users/orders/withdrawals) into a single `handlePostRequests`/`batchCall` invocation to amortize proof-verification and gas costs, so one adversarial/broken request can block delivery of every other legitimate request bundled alongside it, and since the poisoned request itself carries no timeout in the relayer-fee case, that specific request (and any escrow it references) can never be delivered at all — permanently freezing the associated funds.

### Impact Explanation
This is a concrete freezing-of-funds and route-availability issue reachable from unprivileged actions:
- A user/attacker can cause their own request to become permanently undeliverable by using (or having become, e.g. via blacklisting) an incompatible beneficiary/token, since there is no way to skip or discard a single poisoned request from a proven merkle batch of `PostRequestLeaf`s once it is included.
- Relayers who batch multiple independent withdrawal/order-fill requests into one `handlePostRequests` call have their entire batch DoS'd by the single bad request, delaying/blocking delivery (and thus payout) for unrelated legitimate users until relayers learn to permanently exclude the poisoned leaf.
- For the relayer-fee withdrawal flow specifically, `Fees::<T>` is zeroed on the source (Hyperbridge) chain as soon as the withdrawal request is dispatched, before the destination-chain transfer is known to succeed; since the request has `timeout: 0` (never times out) there is no retry/refund mechanism if the destination transfer permanently reverts, resulting in permanent loss of the relayer's fee.

This satisfies the "permanent freezing of funds" / "route unable to deliver messages" criteria for a Medium/High severity finding.

### Likelihood Explanation
Reaching this requires only a normal, permissionless action: submitting a POST request whose eventual beneficiary is (or becomes) blacklisted by its token, or using a token with reverting/gas-griefing transfer hooks, then having any relayer batch its proof together with other pending requests via `handlePostRequests`/`batchCall` — a standard cost-saving relayer behavior explicitly supported by `IHandlerV2.batchCall`. No admin, governance, or validator compromise is required.

### Recommendation
- Wrap each per-leaf dispatch in `HandlerV2.handlePostRequests`/`handleGetResponses` (and the corresponding `dispatchTimeOut` calls) in a low-level call with try/catch (or use `call` instead of a direct external call) so that a failing destination module does not revert delivery of sibling requests in the same batch; record the failure (e.g., emit an event) and allow the request to be retried/discarded independently.
- In `IntentsBase._withdraw`/`IntentGatewayV2.withdraw`/`HostManager` payout paths, use `safeTransfer`-style patterns with per-token isolation, and consider allowing a privileged/permissionless "skip and refund to a claimable balance" mechanism when a transfer to a beneficiary is not currently possible, rather than reverting the whole delivery.
- For relayer-fee withdrawals, avoid zeroing `Fees::<T>` before the destination payout is confirmed successful, or provide a reconciliation path to restore/re-dispatch fees if the destination-side transfer can never succeed.

### Proof of Concept
1. A user submits (or is assigned, e.g. via an intent order) an escrow withdrawal/fill whose beneficiary address is on a blacklistable token's (e.g., USDT-like) blacklist, or whose fee token has a transfer hook that always reverts.
2. Hyperbridge processes and commits this request alongside other, unrelated, legitimate pending POST requests (withdrawals/order fills) destined for the same EVM chain.
3. A relayer batches the merkle proof for all these requests into one call to `HandlerV2.handlePostRequests` (directly, or via `batchCall`).
4. `handlePostRequests` loops through all leaves and calls `host.dispatchIncoming` for each; when it reaches the poisoned leaf, `IntentGatewayV2.withdraw`/`IntentsBase._withdraw`/`HostManager.onAccept`'s ERC20 transfer reverts. [7](#0-6) 
5. The revert propagates through `dispatchIncoming` and the entire `handlePostRequests` transaction reverts, so none of the batched requests are delivered — including the unrelated, legitimate withdrawals/fills bundled in the same transaction — and the poisoned request (with no timeout, in the relayer-fee case) can never be delivered on any subsequent attempt either.

### Citations

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
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

**File:** evm/src/core/EvmHost.sol (L794-800)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L149-167)
```rust
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
```
