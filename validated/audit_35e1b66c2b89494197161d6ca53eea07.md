## Finding

### Title
Unbounded `order.inputs`/`WithdrawalRequest.tokens` array causes `onAccept`/`_withdraw` to run out of gas, permanently freezing cross-chain escrow — (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentGatewayV2.placeOrder()` accepts an `Order.inputs` array of arbitrary length with no upper bound. That same array is later carried, unmodified, as `WithdrawalRequest.tokens` inside a cross-chain `RedeemEscrow`/`RefundEscrow` message dispatched via Hyperbridge, and is consumed by an unbounded `for` loop in `_withdraw()` that performs one external token transfer per entry — the same "many external calls in one unbounded, user-sized loop" pattern flagged in the external `commitToLiens()` report.

### Finding Description
`placeOrder()` never caps `order.inputs.length`: [1](#0-0) 
The array is escrowed per-token in a loop and stored in `_orders[commitment][token]`, again with no bound on the number of distinct tokens: [2](#0-1) 

When a solver fills the order cross-chain, `_fillCrossChain` marks the order filled on the destination and dispatches a `RedeemEscrow` message to the source chain that embeds the entire `order.inputs` array verbatim: [3](#0-2) 
The analogous `_cancelFromDest` path embeds the same `order.inputs` into a `RefundEscrow` message: [4](#0-3) 

On the receiving chain, the permissionless relayer delivers this as a normal ISMP POST request; `onAccept` (callable only by the local `IsmpHost`, but reachable by any relayer submitting a valid proof) decodes the body and calls `_withdraw`: [5](#0-4) 

`_withdraw` then iterates over `body.tokens` — i.e., the attacker-sized `order.inputs` — performing one `safeTransfer`/native transfer per token with no length cap: [6](#0-5) 

If the number of distinct token entries is large enough that the loop's cumulative gas exceeds what the destination EVM host allows a single `handlePostRequests`/`onAccept` execution to consume, the message can never execute successfully — it deterministically reverts on every relayer attempt, exactly like `commitToLiens()` failing "due to insufficient gas."

### Impact Explanation
Because `_filled[commitment]` is already set on the destination chain in `_fillCrossChain` before the `RedeemEscrow` dispatch, a solver who fills such a malicious order has already delivered the required output tokens to the beneficiary. If the `RedeemEscrow` message can never be executed on the source chain because `_withdraw`'s loop always exceeds the available gas, the solver's corresponding input-token escrow on the source chain is permanently unreachable — no retry can ever succeed since the array length (and thus the gas requirement) never changes. This is a permanent freezing of escrowed funds and a griefing vector against solvers who fill oversized orders, reachable by any unprivileged user simply by calling `placeOrder()` with an inflated `inputs` array. The symmetric `RefundEscrow` path can likewise permanently trap a user's own escrow if the same order shape is used for cancellation.

### Likelihood Explanation
`placeOrder` is fully permissionless and imposes no bound on `order.inputs.length`, and nothing downstream (dispatch, `onAccept`, `_withdraw`) enforces a maximum token count either. Any user (or an attacker posing as a normal order placer) can construct such an order at negligible cost; a solver only needs to be induced to fill it (e.g., by an attractive output offer) for the freeze to occur once the redeem message is relayed.

### Recommendation
Enforce a maximum length on `Order.inputs` (and `Order.output.assets`) at `placeOrder`/`fillOrder` time, sized so that the worst-case `_withdraw` loop plus proof verification overhead comfortably fits within the destination chain's per-message gas budget. Alternatively, chunk `WithdrawalRequest.tokens` processing so a single oversized array cannot brick delivery of the whole withdrawal.

### Proof of Concept
1. Attacker calls `placeOrder` with `order.inputs` containing, e.g., 200+ distinct low-value ERC-20 tokens (or self-deployed cheap tokens), escrowing them via the existing per-token loop in `placeOrder`.
2. A solver, seeing a favorable output offer, calls `fillOrder`/cross-chain fill, transferring output tokens to the beneficiary; `_fillCrossChain` marks the order filled and dispatches `RedeemEscrow` with the 200+-entry `order.inputs`.
3. When the relayer delivers this POST request to the source chain, `onAccept` → `_withdraw` iterates 200+ times performing external transfers; the cumulative gas exceeds the chain's message-execution gas limit, so the transaction always reverts regardless of gas supplied by the relayer.
4. The solver's due escrow is now permanently unretrievable — repeated relay attempts all fail identically, since the array size never shrinks.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-196)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

```

**File:** evm/src/apps/IntentGatewayV2.sol (L228-256)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
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
