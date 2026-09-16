## Analog Found

### Title
Liquidation-style DoS: a single blocked/paused output token permanently freezes an entire Intent Gateway escrow release - (File: evm/src/apps/intentsv2/IntentsBase.sol, evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentsBase._withdraw` (EVM) and its Tron counterpart `IntentGatewayV2.withdraw` release an order's *entire* set of escrowed tokens in a single loop. If the transfer of any one token in that list reverts, the whole function reverts and none of the other (otherwise transferable) tokens in the same order are released — exactly the same bug class as the referenced Sherlock M-3 finding, where a single failing asset transfer in a loop blocked an entire liquidation.

### Finding Description
`_withdraw` iterates `body.tokens` and calls `IERC20(token).safeTransfer(beneficiary, amount)` (or `.call` + manual success check on Tron) for every token, reverting the whole transaction on the first failure: [1](#0-0) 

The Tron variant is functionally identical, using a raw `.call` and `revert TransferFailed()`: [2](#0-1) 

This function is reached from `onAccept` when a relayer delivers a `RedeemEscrow` (successful fill) or `RefundEscrow` (cancellation) message, and from `onGetResponse` for the cancel-from-source flow: [3](#0-2) 

Both delivery paths are permissionless — any relayer can submit the proof via `HandlerV2.handlePostRequests`/`handleGetResponses`, which calls `EvmHost.dispatchIncoming`. That function uses a low-level `.call` to `onAccept` and, on failure, deletes the request receipt "so it can be retried": [4](#0-3) 

Since these withdrawal messages are dispatched with `timeout: 0` (no timeout), they never expire and can be resubmitted indefinitely: [5](#0-4) 

If an order escrows multiple input tokens (e.g., USDC + DAI) and one of them becomes untransferable — the beneficiary/solver address gets blacklisted on USDC, the token is paused, or an upgradeable token changes behavior — every retry of `onAccept`/`onGetResponse` fails at the same token in the loop. This is a direct structural analog to the original report: `_liquidate`/`sweepTo` iterating over all assets and reverting on a single bad transfer, which the Sentiment team fixed by catching per-asset failures and skipping/retrying individually. `_withdraw` here has no such per-token isolation — a single frozen asset locks the release of *all* other assets in that same commitment forever, since retrying invokes the identical all-or-nothing loop.

### Impact Explanation
Because retries always fail identically (the blocking condition — blacklist, pause, upgraded implementation — does not resolve itself), the entire order's escrowed value becomes permanently frozen: the solver can never redeem the tokens they legitimately filled the order for, and the user can never get a refund on cancellation. This is a full loss of access to escrowed funds (unbacked freezing), not merely a gas/DoS nuisance, matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Reachable by any user/solver constructing an order (or any attacker choosing to place themselves on the USDC blacklist, as the original report notes) with multiple input/output tokens where one asset is a blacklistable/pausable/upgradeable ERC-20 (USDC, USDT, etc. are common in cross-chain intent flows). No privileged role is required — the condition can be triggered by ordinary token behavior (pause, blacklist) or deliberately by a malicious order creator wanting to avoid ever settling a losing trade.

### Recommendation
Do not let one token's transfer failure block the release of the others. Options, mirroring the Sentiment fix:
- Wrap each per-token transfer in a try/catch (or low-level `.call` with per-item success handling) inside the `_withdraw`/`withdraw` loop, skip failed transfers, and keep the un-released amount in `_orders[commitment][token]` so it can be retried later without blocking the other tokens.
- Alternatively, allow retrying the withdrawal per-token via a separate permissionless `sweep`/`retryToken` function once the underlying condition (unpause, unblacklist) is resolved, decoupling the escrow accounting per token instead of an all-or-nothing loop.

### Proof of Concept
1. User places a cross-chain order escrowing `[USDC, DAI]` as inputs.
2. Solver fills the order on the destination chain; `_fillCrossChain` dispatches a `RedeemEscrow` message back to the source chain with `tokens = [USDC, DAI]` and `beneficiary = solver`.
3. Before the message is relayed, the solver's address is added to USDC's blacklist (or USDC is paused, or the solver deploys a contract that reverts on receiving DAI first then USDC transfer fails, etc.) — any condition making `IERC20(USDC).safeTransfer(solver, amount)` revert.
4. A relayer submits the proof via `handlePostRequests` → `EvmHost.dispatchIncoming` → `IntentsBase.onAccept` → `_withdraw`.
5. The loop reaches the USDC transfer, which reverts; the whole `_withdraw` call reverts; `EvmHost.dispatchIncoming` catches this and deletes the request receipt, allowing indefinite retries.
6. Every subsequent retry hits the same revert at the same USDC transfer, so the DAI amount (which is perfectly transferable) is never released either — both assets are permanently stuck in the gateway's escrow for that commitment.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-470)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L126-142)
```text
    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-366)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }

    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
