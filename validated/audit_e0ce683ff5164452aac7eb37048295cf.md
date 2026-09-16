### Title
Unbounded `Order.inputs`/`output.assets` arrays permit out-of-gas denial-of-service that permanently freezes escrowed funds - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`placeOrder` accepts a user-supplied `Order` struct whose `inputs` and `output.assets` are arbitrary-length `TokenInfo[]` arrays with no cap enforced anywhere in the contract, unlike the `TOKEN_ADDRESS_LIMIT` pattern the external report flags (a limit variable exists conceptually but is never checked). Because these arrays are later iterated in `_withdraw`, `_execute`, and re-encoded/dispatched cross-chain in `_fillCrossChain`/`_cancelFromDest`, an attacker can size an order so large that the payout/refund loop cannot complete within a block's gas limit.

### Finding Description
`placeOrder` only validates `order.inputs.length == 0` and duplicate output tokens; it never bounds the number of elements in `order.inputs` or `order.output.assets`: [1](#0-0) 

These unbounded arrays are carried through the entire order lifecycle and looped over in gas-sensitive contexts:
- `_withdraw`, which releases/refunds escrow to a beneficiary, loops over `body.tokens.length` performing an SLOAD, SSTORE, and an external transfer (native send or `safeTransfer`) per element: [2](#0-1) 
- `_cancelFromSource` loops over all `order.inputs` to validate escrow before dispatching a cancellation: [3](#0-2) 
- `_fillCrossChain` re-forwards the full, unbounded `order.inputs` array as the `RedeemEscrow` withdrawal-request body to the source chain: [4](#0-3) 
- On delivery, `onAccept` decodes this `WithdrawalRequest` and calls `_withdraw`, which must iterate the entire attacker-chosen array in a single relayer-submitted transaction: [5](#0-4) 

Because `placeOrder` is reachable by any unprivileged user and there is no limit on the number of `TokenInfo` entries (analogous to the missing `TOKEN_ADDRESS_LIMIT` enforcement in the audit report), a user can escrow funds under an order with hundreds or thousands of input/output legs. The corresponding release/refund transaction (`_withdraw`, invoked from `onAccept`/`onGetResponse`, or the cross-chain redeem/refund dispatch) can then exceed the destination or source chain's per-block gas limit, making it impossible for any relayer to ever successfully deliver the message and complete the payout.

### Impact Explanation
If the withdrawal loop cannot fit in a block, the escrowed input tokens (and any attached relayer/transaction fees) become permanently stuck: `_withdraw` can never fully execute, `_filled[commitment]` is never (or only partially, depending on where it reverts) finalized, and neither the solver (fill path) nor the original user (cancel/refund path) can retrieve the escrowed assets. This is a concrete freezing-of-funds vulnerability reachable by a single `placeOrder` transaction from any unprivileged intent user, matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood is Medium-High: exploitation requires only calling `placeOrder` with a very large `inputs`/`output.assets` array and funding it (fees scale with amounts, but an attacker can use small per-token amounts to keep cost low while maximizing element count) — no special privileges, no cross-chain coordination beyond the intended flow, and no dependence on validator or governance misbehavior. The main uncertainty is the exact array length needed to blow past the target chain's gas limit, which depends on chain-specific block gas limits and calldata/storage costs of `_withdraw`'s inner loop (SLOAD/SSTORE + external transfer per element), but the unbounded nature of `TokenInfo[]` makes such a length achievable at low cost.

### Recommendation
Enforce a hard cap on `order.inputs.length` and `order.output.assets.length` (and `predispatch.assets.length`) in `placeOrder`, sized so that the worst-case `_withdraw`/`_execute` loop — including all downstream external calls — comfortably fits within the gas limit of every supported destination/source chain, mirroring the `TOKEN_ADDRESS_LIMIT` enforcement recommended in the referenced report (e.g., `require(order.inputs.length <= MAX_INTENT_TOKENS && order.output.assets.length <= MAX_INTENT_TOKENS, InvalidInput())`).

### Proof of Concept
1. Attacker calls `placeOrder` with `order.inputs` containing e.g. 2,000 distinct dust-amount `TokenInfo` entries (or repeated small-amount entries for a single token, since duplicates are only rejected for `output.assets`, not `inputs`) and a correspondingly large `output.assets` array with matching count, `deadline` set far in the future, `session = address(0)`.
2. A solver (or the attacker's own account) fills the order via `fillOrder`/`_fillCrossChain`, causing `_post` to dispatch a `RedeemEscrow` `WithdrawalRequest` containing the full 2,000-element `order.inputs` array to the source chain.
3. When Hyperbridge delivers this message via `onAccept` → `_withdraw` (or via `_cancelFromDest`/`onGetResponse` for the refund path), the relayer's transaction must iterate all 2,000 elements, performing a storage read/write and an external token transfer for each; this transaction fails to fit within the destination chain's block gas limit and can never be mined.
4. The escrow for the commitment remains permanently locked in `_orders[commitment][token]` for every one of the 2,000 tokens, with no way to reduce the array size after the fact (no partial-withdraw/enumeration limit exists elsewhere in the contract).

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-234)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L245-252)
```text
        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
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
