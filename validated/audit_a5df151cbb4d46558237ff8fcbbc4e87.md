## Analog Found

### Title
Malicious ERC20 order-input token permanently freezes solver funds and co-escrowed assets in Intent Gateway `_withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` (used by both same-chain fills and cross-chain `RedeemEscrow`/`RefundEscrow` settlement) iterates over an order's escrowed input tokens and calls `IERC20(token).safeTransfer(...)` on each one in a single atomic loop. Any user can place an order whose `inputs` array contains an attacker-controlled ERC20 with no whitelist or validation. If that rogue token reverts on transfer, the entire withdrawal transaction reverts — including the release of every other, legitimate token escrowed in the same order — permanently freezing funds and, in the cross-chain case, stranding a solver who already paid out real value on the destination chain.

### Finding Description
`placeOrder`/order construction places no restriction on which ERC20 addresses may appear in `order.inputs` — [1](#0-0)  simply pulls whatever token address is specified via `safeTransferFrom`. There is no token whitelist check anywhere in `IntentsBase`/`ExtrinsicIntents`/`IntrinsicIntents`.

Settlement of escrowed inputs — for both fill-redemption and cancellation-refund — goes through `IntentsBase._withdraw`, which loops over `body.tokens` and calls `safeTransfer` for every token in one atomic transaction: [2](#0-1) 

For a cross-chain order, the solver fills on the destination chain (`_fillCrossChain`), delivering the real output tokens to the order's beneficiary immediately, then dispatches a `RedeemEscrow` message back to the source chain listing *all* of `order.inputs` to be released to the solver: [3](#0-2) 

That message is sent with `timeout: 0` via `_post`, meaning it can never time out and be refunded/cancelled — it must eventually succeed: [4](#0-3) 

On the source chain, `onAccept` decodes the `RedeemEscrow`/`RefundEscrow` body and calls `_withdraw`: [5](#0-4) 

`EvmHost.dispatchIncoming` swallows a reverting `onAccept` by deleting the request receipt so the delivery "can be retried" — but it does not change the outcome: `_withdraw`'s loop deterministically reverts every single time it is invoked with the same commitment/token set, because the rogue token itself is the one that reverts: [6](#0-5) 

Since the underlying request has `timeout: 0` and can never be marked delivered, the escrow for that commitment — including any legitimate token co-escrowed in the same order — is permanently locked in the gateway contract with no recovery path.

### Impact Explanation
An attacker (as the order's `user`) places a cross-chain order whose inputs are `[LEGIT_TOKEN, ROGUE_TOKEN]`, where `ROGUE_TOKEN.transfer` is coded to always revert (or to revert only when `to == solver`, keeping the attack invisible during simulation). A solver, unaware of the malicious token's behavior, fills the order and immediately delivers real output value to the attacker's beneficiary on the destination chain. When the solver's `RedeemEscrow` message reaches the source chain, `_withdraw`'s loop hits `ROGUE_TOKEN.safeTransfer` and reverts — which reverts the *entire* withdrawal, including the legitimate token that would otherwise have gone to the solver. Because the request never times out (`timeout: 0`) and delivery can be retried indefinitely with the identical, deterministic revert, the solver can never claim any of the escrowed inputs. The solver's real, already-delivered output tokens are lost, and both the legitimate and rogue tokens remain frozen in the gateway forever. The same mechanism applies to refund (`RefundEscrow`) and same-chain (`IntentsBase._withdraw` shared by `IntrinsicIntents`) paths, freezing the user's own multi-token escrow if they later try to cancel.

### Likelihood Explanation
The attack requires no privileged access — only the ability to deploy an arbitrary ERC20 and place an order through the public, unrestricted `placeOrder` entrypoint. There is no token whitelist, no per-token isolation of escrow settlement, and no partial-success handling in `_withdraw`. Any solver competing for orders (which is by design an open, permissionless market) can be targeted.

### Recommendation
- Do not let a single failing token transfer revert the release of unrelated tokens in the same withdrawal: process each token transfer independently (e.g. wrap each `safeTransfer` in a try/catch, or perform a low-level call and only revert on failure for the last-attempted state, allowing per-token retry/withdrawal).
- Alternatively, require input tokens to belong to a whitelist/registry maintained by governance before they may be used in orders, closing off arbitrary attacker-supplied ERC20s as order inputs.
- Consider giving cross-chain `RedeemEscrow`/`RefundEscrow` messages a non-zero timeout or an explicit escape hatch (e.g. a dust-sweep/administrative unlock) so escrow for a poisoned commitment is not permanently unrecoverable.

### Proof of Concept
1. Attacker deploys `RogueToken`, an ERC20 whose `transfer`/`transferFrom` succeeds normally but is coded to `revert()` once a flag is flipped (or whenever `to` equals a specific target such as the eventual solver address).
2. Attacker calls `placeOrder` on the source chain with `order.inputs = [ {USDC, 1000}, {RogueToken, 1} ]` and an attractive `order.output` on a destination chain, escrowing both tokens via `IntentsBase`/`IntentGatewayV2` (no whitelist check blocks the rogue token: [7](#0-6) ).
3. A solver calls `fillOrder` on the destination chain, delivering the required output tokens directly to the attacker's beneficiary (`_fillCrossChain`), then dispatches `RedeemEscrow` back to source with `order.inputs` and `beneficiary = solver` [8](#0-7) .
4. Attacker flips `RogueToken`'s revert flag (or it was always configured to revert for `to == solver`).
5. When the relayer delivers `RedeemEscrow` and `onAccept` calls `_withdraw`, the loop's `IERC20(RogueToken).safeTransfer(solver, 1)` reverts, reverting the whole `_withdraw` call and therefore the USDC transfer too: [9](#0-8) .
6. `EvmHost.dispatchIncoming` deletes the receipt so it "can be retried" [10](#0-9) , but every retry produces the same deterministic revert. Because the message's `timeout` is `0`, it can never expire and be refunded either. The solver's already-delivered output tokens are gone, and the escrowed USDC + rogue token remain frozen in the gateway indefinitely.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-468)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-220)
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
