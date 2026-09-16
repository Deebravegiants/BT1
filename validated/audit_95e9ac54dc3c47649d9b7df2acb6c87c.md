## Title
IntentGateway order beneficiaries permanently lose escrowed refunds/fills if blacklisted by the escrowed ERC20 token - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw`, the single choke-point used by every escrow-release path in the Intent Gateway (fills, cross-chain refunds, cross-chain redemptions, and cancellations), pushes tokens to a hardcoded `beneficiary` address taken from the order/`WithdrawalRequest` with a strict, revert-on-failure `safeTransfer`/native `call`. There is no mechanism for the beneficiary to redirect funds to a different address if the escrowed token has since blacklisted them, so a blacklisted user's or solver's escrow becomes permanently stuck, exactly the bug class described in the referenced Footium `FootiumPrizeDistributor.claimERC20Prize` report.

### Finding Description
`_withdraw` resolves the recipient directly from the request body and transfers every escrowed token to it in a loop, with no way to specify an alternate destination: [1](#0-0) 

The `beneficiary` value is fixed long before withdrawal happens and can never be updated by the affected party:
- For refunds (`_cancelSameChain`/cross-chain `RefundEscrow`/`onGetResponse` after expiry), `beneficiary = order.user`, set once at `placeOrder` time: [2](#0-1) , and via the GET-response cancel path [3](#0-2) .
- For cross-chain fills (`RedeemEscrow`), `beneficiary = msg.sender` (the filling solver) at fill time: [4](#0-3) .

Both paths route through the same `_withdraw`, whether triggered directly (same-chain) or via `onAccept` after a cross-chain settlement message: [5](#0-4) . Because `IERC20.safeTransfer` reverts if the token contract refuses the recipient (e.g. USDC/USDT-style `isBlacklisted` checks), a single blacklisted beneficiary makes the entire `onAccept`/`_withdraw` call for that order revert unconditionally — there is no fallback recipient, no partial-skip-and-continue, and no user-facing function to re-target the beneficiary. The `RedeemEscrow`/`RefundEscrow` message is one-shot: once delivered (or the GET-response cancel path resolves), the only code path that can move the escrow reverts every time it's retried, since the beneficiary address baked into the commitment never changes.

The equivalent low-level variant on the Tron gateway has the identical pattern: [6](#0-5) .

### Impact Explanation
If a user's address (order creator) or a solver's address is blacklisted by any of the escrowed ERC20 tokens between order placement/fill and settlement — a realistic scenario given USDC/USDT-style blacklisting and the fact that cross-chain settlement, expiry-based cancellation, and GET-response proof windows can span arbitrary time — the escrowed principal for that order (and any accrued relayer fees in the fee token) is permanently locked in the `IntentGateway` contract with no recovery mechanism. This is a concrete, permanent freezing of user/solver funds reachable from a single unprivileged `placeOrder`/`fillOrder`/`cancelOrder` transaction sequence, matching the Medium-severity impact criteria (permanent freezing of funds) from the original report.

### Likelihood Explanation
Blacklisting is a low-probability event per user, as acknowledged in the original report, which is why it is rated Medium rather than High. However, the Intent Gateway is designed specifically to move arbitrary ERC20 assets (including blacklist-capable stablecoins) across chains for any user or solver, so the exposure is systemic across every order rather than a one-off configuration mistake, and the fund-freezing outcome is deterministic and unrecoverable once triggered.

### Recommendation
Decouple beneficiary determination from token delivery: allow the affected party to pull funds to a self-chosen address (e.g. a `claim(commitment, token, to)` function gated by proof that `msg.sender`/a signature matches the original beneficiary), or wrap each token transfer in `_withdraw` in a try/catch that credits an internal, separately claimable balance instead of reverting the whole withdrawal when a transfer to the hardcoded beneficiary fails.

### Proof of Concept
1. User places a cross-chain order via `placeOrder`, escrowing USDC as `order.inputs`, with `order.user` set to their own address.
2. Before the order is filled, the escrowed-token issuer blacklists the user's address (e.g., regulatory action against `order.user`).
3. The order goes unfilled past `order.deadline`; the user (or anyone, post-deadline) calls `cancelOrder`, which dispatches the cross-chain cancel/GET flow (`_cancelFromSource`/destination cancel) that ultimately calls `_withdraw` with `beneficiary = order.user`.
4. `IERC20(usdc).safeTransfer(beneficiary, amount)` in `IntentsBase._withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol:468`) reverts because USDC's `transfer` reverts for a blacklisted recipient.
5. Every retry of the settlement/cancellation message hits the same revert since `beneficiary` is immutably tied to `order.user`; the escrowed USDC remains locked in the gateway indefinitely, with no way for the user to specify a different receiving address.

### Citations

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-179)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-219)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L331-337)
```text
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-366)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```
