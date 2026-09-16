## Title
Escrowed order funds are permanently frozen if the input token blacklists the order's beneficiary address - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase::_withdraw`, the internal function that releases escrowed order inputs to a beneficiary on `RedeemEscrow`/`RefundEscrow` delivery and on the `cancelFromSource` GET response, performs a direct push transfer (`IERC20(token).safeTransfer(beneficiary, amount)`) to an address baked into the order/commitment at placement or cancellation time. If the escrowed token implements a denylist (e.g., USDC), and that fixed beneficiary address is or becomes blacklisted, the transfer reverts every single time it is attempted, permanently freezing the escrowed principal with no pull-based recovery path — the same root-cause class as Teller's H-4 `_repayLoan`/lender-blacklist bug.

### Finding Description
`_withdraw` is the shared settlement primitive for the Intent Gateway escrow: [1](#0-0) 

It is reached from three unprivileged, single-transaction paths:
- `onAccept` handling `RefundEscrow` after `_cancelFromDest`, where the beneficiary is fixed to `order.user` at cancellation time: [2](#0-1) 
- `onGetResponse` after `_cancelFromSource`, again with beneficiary `order.user`: [3](#0-2) [4](#0-3) 
- `onAccept` handling `RedeemEscrow` after a cross-chain fill, beneficiary = the filling solver's own address: [5](#0-4) 

The `RefundEscrow`/GET-response paths are the concerning ones: `order.user` is set once when the order is placed and is committed into the order hash, so it cannot be changed later. If a legitimate user's address becomes denylisted by the escrowed token's issuer (e.g. sanctioned USDC address) at any point before their order is cancelled/refunded, `IERC20(token).safeTransfer(beneficiary, amount)` in `_withdraw` will revert unconditionally. Because the beneficiary is immutable for that commitment, every retry of the cancellation flow — whether a fresh `RefundEscrow` dispatch, a fresh GET-response delivery, or a relayer resubmission — hits the exact same revert. There is no alternate/pull-based mechanism (comparable to Teller's escrow-vault fix for H-4) to let the funds be recovered by any other means; the tokens remain locked in `_orders[commitment][token]` forever, and the on-chain state can never be advanced past that point.

The same fragility exists in the parity Tron implementation, which uses a raw low-level call instead of `SafeERC20` but produces the identical unconditional-revert-on-blacklist behavior: [6](#0-5) 

### Impact Explanation
Any escrowed input token amount tied to an order whose beneficiary (the order's own `user` field) is denylisted by the token contract becomes permanently unrecoverable. This is a guaranteed, permanent loss/freeze of user principal with no admin, governance, or protocol-level workaround built into the contract — matching the "permanent freezing of funds" impact bar. It requires no privileged or malicious actor: a routine token-issuer denylisting event (sanctions, fraud flags, regulatory action against the address) triggers it, and it is unrecoverable by the user, solver, or any relayer once triggered.

### Likelihood Explanation
Likelihood is driven entirely by the token's denylist policy, not by an attacker's actions: any USDC-escrowed intent order whose placing user's own address is later blacklisted (which does happen in practice with USDC) will hit this path when they attempt to cancel and reclaim their escrow. Given IntentGatewayV2 is designed to support arbitrary ERC-20 tokens including USDC (per the same-chain fee-on-transfer/USDC test fixtures in the repo's test suite), this is a realistic, non-contrived scenario rather than a purely theoretical one.

### Recommendation
Follow the same fix pattern Teller adopted for H-4: when the direct `safeTransfer`/native send to `beneficiary` in `_withdraw` (and the Tron `withdraw`) fails or is expected to fail for a denylist-capable token, fall back to depositing the funds into a per-beneficiary escrow/vault contract that the beneficiary (or an authorized delegate/alternate address) can later pull from, instead of reverting the whole settlement. Alternatively, wrap the transfer in a try/catch and route failed transfers into a claimable balance mapping keyed by `(beneficiary, token)`, exposing a separate `claim()` function that lets the affected party redirect the withdrawal to a non-blacklisted address.

### Proof of Concept
1. User places a cross-chain (or same-chain) order via `placeOrder`, escrowing `USDC` as `order.inputs[0]`, with `order.user` set to their own address `U`.
2. Before the order is filled, USDC's issuer blacklists address `U` (independent external event).
3. User calls `cancelOrder` (`_cancelFromDest`/`_cancelFromSource`), which dispatches `RefundEscrow`/`DispatchGet` with beneficiary fixed to `order.user = U`.
4. When the corresponding `onAccept`/`onGetResponse` is delivered and calls `_withdraw`, `IERC20(USDC).safeTransfer(U, amount)` reverts because `U` is blacklisted.
5. Any resubmission of the same message by any relayer reproduces the identical revert, since the beneficiary `U` is fixed in the order commitment — the escrowed USDC in `_orders[commitment][USDC]` can never be released, permanently freezing the user's funds.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```
