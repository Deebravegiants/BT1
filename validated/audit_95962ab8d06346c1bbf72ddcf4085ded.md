### Title
Push-pattern escrow release lets a single bad token in a `RedeemEscrow`/`RefundEscrow` withdrawal permanently freeze all other escrowed assets in the same order - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
The original report's root cause — pushing tokens to a party in the same call/step that also finalizes irreversible on-chain state, instead of pulling — has a direct analog in the IntentGateway's escrow-release path (`_withdraw`). Unlike a DAO's `sponsorProposal` front-running, here the risk isn't front-running per se, but the same "push, don't pull" anti-pattern: `_withdraw` decrements escrow and pushes tokens to a beneficiary inside a loop, and a single reverting transfer aborts the whole cross-chain message handler, with no way to retry per-token.

### Finding Description
`_withdraw` in `IntentsBase.sol` iterates over `body.tokens` and pushes each token directly to `beneficiary` via `IERC20.safeTransfer` (or a native `_sendValue`), decrementing `_orders[commitment][token]` first: [1](#0-0) 

This function is the terminal step of both the `RedeemEscrow` message (paid to the solver who filled a cross-chain order) and the `RefundEscrow`/cancellation message, both of which arrive through `onAccept` on the HyperApp callback triggered by an ISMP-relayed, cross-chain message — i.e., reachable by any relayer delivering a `PostRequest` that was legitimately dispatched by `ExtrinsicIntents._fillCrossChain`/`_cancelFromSource`: [2](#0-1) 

Because the token transfer is a **push** (`safeTransfer` to `beneficiary`) rather than a **pull** (beneficiary calling a `claim`/`withdraw` function themselves), any single token in a multi-input order that reverts on transfer to the beneficiary — e.g. a blacklist-capable stablecoin such as USDC where the beneficiary address later becomes blacklisted, a token that reverts on transfers to certain addresses, or a paused token — reverts the entire `_withdraw` call. Since `_withdraw` is invoked from inside the ISMP `onAccept` handler for the incoming settlement message, the revert propagates up and causes the whole message delivery to fail. `pallet-ismp`/`EvmHost` mark such deliveries as failed/undelivered, and unlike a normal request there is no separate retry path per-token — the entire `WithdrawalRequest` (which can carry multiple `TokenInfo` entries for multi-input orders, per `body.tokens`) is blocked as a unit, permanently freezing every other (non-blacklisted) token still escrowed for that commitment along with the fees transfer at the end of `_withdraw`: [3](#0-2) 

This mirrors the report's core complaint precisely: the recommendation there was "Pull pattern for token transfers will solve the issue" — the same fix (a `claim`-style pull, or per-token isolated try/catch with an internal credit ledger) is what is missing here.

### Impact Explanation
A single blacklistable or misbehaving token among an order's `inputs` (attacker- or solver-chosen, since `Order.inputs` and `order.output.beneficiary` are attacker/solver controlled at `placeOrder`/`fillOrder` time) can cause **permanent freezing of funds**: the whole `WithdrawalRequest` batch for that commitment can never be delivered, so the escrowed amounts for all other (non-problematic) tokens plus the accumulated transaction fees for that order are stuck forever with no recovery mechanism in this contract. This satisfies the "permanent freezing of funds" bar from the validation rules.

### Likelihood Explanation
Reachable from a normal user flow with no privileged role: any user places an order with multiple input tokens (one of which is a blacklist-capable asset like USDC/USDT), a solver fills it normally, and the settlement message is relayed normally. If the beneficiary (solver or user, depending on RedeemEscrow/RefundEscrow) is later blacklisted on the problematic token — which can happen for reasons unrelated to Hyperbridge (e.g. Tether/Circle compliance action) — the freeze triggers on the very next delivery attempt of that message, and stays frozen since ISMP relayers will keep re-attempting delivery of the same underlying accepted message and it will keep reverting.

### Recommendation
Convert `_withdraw` (and any other escrow-release path) from a push to a pull pattern: instead of transferring tokens directly in the ISMP callback, credit an internal `claimable[beneficiary][token] += amount` ledger, and expose a separate `claim(token)` function the beneficiary calls themselves. This isolates a single bad/blacklisted token from blocking the finalize/fee-release logic and from blocking delivery of the other tokens in the same withdrawal, and is exactly the fix already applied by the referenced report for the analogous `sponsorProposal` bug.

### Proof of Concept
1. User A places a cross-chain order via `placeOrder` with two inputs: `USDC` and `DAI` (`evm/src/apps/IntentGatewayV2.sol` / `ExtrinsicIntents._fillCrossChain` flow).
2. Solver B fills the order on the destination chain via `fillOrder`, which internally calls `_fillCrossChain`, dispatching a `RedeemEscrow` message back to the source chain naming Solver B as beneficiary (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:164-220`).
3. Before the message is relayed and delivered, Solver B's address gets added to USDC's blacklist by Circle (independent of Hyperbridge).
4. A relayer delivers the `RedeemEscrow` post request; `onAccept` decodes it and calls `_withdraw`, which processes `USDC` first (or in whatever order `body.tokens` are laid out) — `IERC20(USDC).safeTransfer(beneficiary, amount)` reverts because Solver B is blacklisted (`evm/src/apps/intentsv2/IntentsBase.sol:451-470`).
5. The entire `onAccept` call reverts, so DAI (which would have succeeded) and the accumulated transaction fees are never released — the escrow entry for this commitment is permanently stuck, since every retried delivery of the same message hits the same blacklist revert.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-484)
```text
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
