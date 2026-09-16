## Title
Escrowed input tokens can be permanently locked when a cross-chain `RedeemEscrow` message from `fillOrder` is never relayed - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
Cross-chain order settlement in the Intent Gateway mirrors the `NukeFund` pattern described in the external report: release of escrowed funds depends entirely on a single follow-up action (delivery of a Hyperbridge message) that only a relayer can perform, with no timeout, retry path, or admin/emergency escape hatch if that delivery never happens.

### Finding Description
When a solver fills a cross-chain order, `_fillCrossChain` immediately marks the order filled on the destination chain and dispatches a `RedeemEscrow` `DispatchPost` back to the source chain with `timeout: 0` (no expiry): [1](#0-0) 

The `_post` helper explicitly sets `timeout: 0` for this dispatch: [2](#0-1) 

The escrowed input tokens on the source chain are only released via `_withdraw`, which is only reachable through `onAccept` when the `RedeemEscrow` (or `RefundEscrow`) message actually arrives: [3](#0-2) 

There is no other path back to the escrow. Cancellation from the destination is blocked because `_filled[commitment]` was already set there when the order was filled: [4](#0-3) 

Cancellation from the source is likewise blocked once the destination reports the order as filled — `onGetResponse` reverts with `Filled()` in that case (per the documented flow), and the source-side `_filled` mapping only becomes non-empty once the (never-delivered) `RedeemEscrow`/`RefundEscrow` message lands. If no relayer ever delivers the `RedeemEscrow` message — e.g., because the solver set `options.relayerFee` too low to be economically worth relaying, the relayer set is offline, or delivery is otherwise griefed — the escrowed input tokens sit in the source `IntentGatewayV2`/gateway contract indefinitely: [5](#0-4) 

No owner, governance, or admin function exists to force settlement, retry the message, or sweep stuck escrow back to the user or solver in this situation; `SweepDust`/`UpdateParams` governance actions only touch protocol dust, not per-order escrow.

### Impact Explanation
This is a permanent freezing-of-funds bug: once a cross-chain order is filled, the user has already lost the ability to cancel (destination side is locked), the solver has already paid out the output assets to the user's beneficiary, and the only route to release the corresponding escrowed input tokens is a relayer-dependent, un-timed-out message. If that message is never delivered, both the user's escrow and the solver's expected payout remain stuck in the source contract with no recovery mechanism — directly analogous to NukeFund's reliance on a single user-triggered action with no emergency withdrawal.

### Likelihood Explanation
Reachable via a single `fillOrder` transaction on the destination chain — no privileged role required. The relayer fee for this dispatch is solver-controlled (`options.relayerFee`); an underpriced fee, a relayer outage, or targeted griefing by withholding delivery of a specific message are all realistic ways this message never gets relayed, especially since `timeout: 0` means the request can never expire and be recovered via a timeout path either.

### Recommendation
Add a bounded timeout (instead of `timeout: 0`) on the `RedeemEscrow`/`RefundEscrow` dispatch so a timed-out request can fall back to an on-chain recovery path (e.g., permitting the user or solver to reclaim/re-trigger settlement after expiry), and/or add a governance-gated emergency withdrawal for orders whose settlement message has been outstanding beyond a safety window.

### Proof of Concept
1. User places a cross-chain order on chain A (source), escrowing input tokens; `order.source = A`, `order.destination = B`.
2. Solver calls `fillOrder` on chain B, delivering output tokens to the user's beneficiary; `_filled[commitment]` is set on B, and `_fillCrossChain` dispatches a `RedeemEscrow` `DispatchPost` back to A with `options.relayerFee` set low (or a relayer simply never picks it up) and `timeout: 0`.
3. No relayer ever submits the proof/delivers this message to chain A.
4. On chain A, `_filled[commitment]` remains empty, so the escrowed input tokens sit untouched in the gateway contract; a source-side `cancelOrder` (GET-based) would return `Filled()` once the destination is queried past the deadline, since B's `_filled` is already set — cancellation is blocked, and no other function releases the escrow.
5. Neither the user (already paid out on B) nor the solver (never receives the promised escrow from A) can recover the funds; there is no admin/governance withdrawal for this per-order escrow.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L505-510)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-485)
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

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```
