### Title
`onAccept`/`onGetResponse` escrow release permanently reverts and freezes all order funds when a single output token/beneficiary rejects the transfer - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw()` releases escrowed order funds by looping over `body.tokens` and making raw external calls (`_sendValue` for native ETH, `IERC20.safeTransfer` for ERC20s) to the `beneficiary` address embedded in the order/withdrawal request. Neither call has any fallback or per-token isolation: a single reverting transfer aborts the entire batch, and because this function is invoked from `onAccept`/`onGetResponse` (which are themselves invoked by the trusted host after ISMP message delivery), a permanently-reverting transfer makes the escrowed funds for the whole order unrecoverable.

### Finding Description
`_withdraw` in [1](#0-0)  iterates the token list of a `WithdrawalRequest` and unconditionally calls either:
- `_sendValue(beneficiary, amount)` which does `to.call{value: amount}("")` and reverts the whole transaction if `sent` is false [2](#0-1) , or
- `IERC20(token).safeTransfer(beneficiary, amount)` which reverts if the token itself reverts (e.g., blacklist-style tokens like USDC/USDT, paused tokens, or any ERC20 with a callback/hook that can be made to revert).

This function is the terminal step of both cross-chain escrow-release paths:
- `onAccept` for `RedeemEscrow`/`RefundEscrow` messages delivered by Hyperbridge [3](#0-2) 
- `onGetResponse` for the cancellation/refund path after a GET-request proof confirms the order was not filled on the destination [4](#0-3) 

Because `_withdraw` batches every input/output token of an order into one atomic loop with no try/catch or per-token skip logic, if *any single* token/beneficiary combination cannot accept the transfer (beneficiary is a contract with no `receive()`, is blacklisted on a stablecoin, or the ERC20 has a hook that reverts), the entire withdrawal reverts. Since the `beneficiary` is fixed at order-creation time (`order.user` for refunds, or the filler's address for redemptions) and cannot be changed after the fact, and since these callbacks are invoked by the host as part of message delivery (not something the user directly controls the retry semantics of the way a normal function call would allow), the escrowed tokens for that commitment become permanently stuck: the withdrawal message can be redelivered indefinitely and will always hit the same reverting call, and there is no admin/rescue path visible in this contract to force-release funds for a specific stuck order.

This differs from the analogous pattern in `EvmHost.dispatchIncoming`/`dispatchTimeOut`, which correctly wrap the external app callback in a low-level `.call(...)` and check `success`, deleting/restoring the receipt on failure so the message can be retried without losing funds [5](#0-4) . `IntentsBase._withdraw` has no equivalent isolation — a revert anywhere in the loop reverts the entire escrow release.

### Impact Explanation
This is a permanent freezing-of-funds bug matching the report's bug class ("external call failures preventing a settlement process from completing, causing users to lose access to funds/collateral"). Any order whose beneficiary (the user for refunds, or a solver for redemptions) cannot receive one of the escrowed tokens will have **all** of its escrowed tokens (not just the problematic one) locked in the `IntentsBase`/`IntentGatewayV2` contract forever, since there is no partial-success or rescue mechanism reachable through the analyzed dispatch paths.

### Likelihood Explanation
Reachable from a normal, permissionless flow: any user creates a cross-chain order (`Order.user`) or is filled by a solver (`msg.sender` becomes the redemption beneficiary); if that address is (or later becomes, e.g., via a stablecoin blacklist) unable to receive the transfer, the freeze is triggered automatically the next time the escrow-release message is delivered — no attacker action beyond normal usage is strictly required, though an adversarial order creator/solver could also deliberately supply a beneficiary/token pairing known to revert (e.g. a contract with no payable fallback, or an already-blacklisted USDC address) to grief co-mingled multi-token order escrow.

### Recommendation
Isolate each token transfer in `_withdraw` (e.g., wrap `_sendValue`/`safeTransfer` in a low-level call, check success independently per token, and if a transfer fails, credit the amount to an internal "claimable" balance for that beneficiary/token instead of reverting the entire batch), so a single problematic token/beneficiary cannot block release of the rest of the escrow, and provide a pull-based recovery mechanism so previously-failed transfers can be retried or reclaimed later.

### Proof of Concept
1. A user creates a cross-chain order whose `order.user` (source-chain refund beneficiary) is a smart-contract wallet without a `receive()`/payable fallback (or one that deliberately reverts), and includes a native-ETH input alongside an ERC20 input.
2. The order expires unfilled; `_cancelFromSource` is called, dispatching a Hyperbridge GET request to verify non-fill on destination [6](#0-5) .
3. Hyperbridge delivers the GET response; `onGetResponse` calls `_withdraw(body, true, true)` [4](#0-3) .
4. Inside `_withdraw`, the loop reaches the native-token entry and calls `_sendValue(beneficiary, amount)`, which reverts because `beneficiary` cannot accept ETH [2](#0-1) .
5. The entire `onGetResponse` call reverts, so the ERC20 portion of the same order (which would have succeeded) is also never released. Any resubmission of the same GET response/withdrawal message hits the identical revert — the escrowed funds for this order are permanently unrecoverable.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-275)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });

        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```

**File:** evm/src/core/EvmHost.sol (L811-818)
```text

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
