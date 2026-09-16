### Title
Attacker can place an intent order with a malicious input token and permanently freeze escrow release, griefing solvers and locking funds - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2.placeOrder` lets any caller escrow an arbitrary set of ERC-20 tokens as `order.inputs` with no token whitelist or validity check beyond rejecting duplicates. [1](#0-0)  When the escrow is later released — on fill, cancellation, or cross-chain settlement — `_withdraw`/`withdraw` iterates over *all* of the order's tokens in a single loop and transfers each one to the beneficiary; if any single token reverts on transfer, the entire withdrawal (and therefore the entire fill/cancel/settlement transaction) reverts. [2](#0-1)  A user can therefore construct an order that mixes one legitimate, valuable input token with one custom ERC-20 that always reverts on `transfer`, permanently blocking release of the entire escrow bundle — including the legitimate portion a solver already paid for.

### Finding Description
`placeOrder` accepts any token address encoded in `order.inputs[i].token` and pulls it via `safeTransferFrom` with no permissioning or allow-list, exactly like the permissionless `DepositManagerV1.fundBountyToken` in the referenced report. [3](#0-2)  The only defensive check is rejection of duplicate token entries, not validation that the token behaves honestly. [1](#0-0) 

All release paths converge on the same "all tokens or nothing" loop:
- Same-chain fill and cancel both call `_withdraw` with the full array of escrowed input tokens for the order. [4](#0-3) [5](#0-4) 
- Cross-chain settlement (`onAccept` handling `RedeemEscrow`/`RefundEscrow`) also calls `_withdraw` with the order's full input list, dispatched from `ExtrinsicIntents.onAccept`. [6](#0-5) 
- `_withdraw` itself has no per-token isolation — a single `safeTransfer` failure on any array element reverts the whole call. [7](#0-6) 

The Tron variant is equally affected, using a low-level `.call` + explicit `revert TransferFailed()` in the same all-in-one-loop pattern. [8](#0-7) 

For cross-chain orders specifically, the attack is a direct theft/freeze against a solver: the solver already delivered output tokens to the beneficiary on the destination chain during `_fillCrossChain` before the `RedeemEscrow` message is dispatched back to the source chain. [9](#0-8)  When that message is later delivered via `onAccept` on the source chain, the malicious token in `order.inputs` causes `_withdraw` to revert deterministically every time, for every relayer that attempts to submit the proof — the message can never be successfully delivered, and the solver's earned escrow (which may include otherwise-legitimate co-escrowed tokens) is frozen permanently.

### Impact Explanation
This is a permanent freeze of funds reachable from a single unprivileged `placeOrder` call combined with a normal `fillOrder`/relayed settlement:
- A solver who fulfills a cross-chain order can permanently lose the escrowed input payment they are owed, because the settlement message becomes permanently undeliverable (a route unable to deliver messages).
- For same-chain orders, the user's own escrow becomes permanently stuck (unfillable and uncancelable), since both `_fillSameChain` and `_cancelSameChain` route through the same `_withdraw` all-or-nothing loop.
- There is no per-token isolation or retry/skip mechanism, so no relayer resubmission or governance action can un-stick the specific commitment once a malicious token is embedded in it.

### Likelihood Explanation
High likelihood: placing an order is fully permissionless and requires no special privileges, mirrors the original bounty-funding bug exactly, and any attacker can deploy a trivial ERC-20 that reverts on `transfer`/`transferFrom` to any address other than itself, then include it as one of several `order.inputs`.

### Recommendation
- Maintain a token allow-list (or at minimum a "can withdraw" probe) for tokens usable in `order.inputs`/`order.output.assets`, similar to `openQTokenWhitelist` in the referenced protocol.
- Make `_withdraw`/`withdraw` resilient to individual token transfer failures — e.g., use a try/catch around each token transfer and only revert the failed leg's escrow bookkeeping (or push failed transfers into a separately claimable "stuck" balance) instead of reverting the entire withdrawal.
- Consider requiring cross-chain `RedeemEscrow`/`RefundEscrow` delivery to at least partially succeed, isolating one malformed token from blocking legitimate ones in the same order.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC-20 whose `transfer` function unconditionally reverts (or reverts for any recipient other than the deployer).
2. Attacker calls `placeOrder` with `order.inputs = [ {token: USDC, amount: X}, {token: EvilToken, amount: Y} ]` and an attractive `order.output` (e.g., cross-chain, paying in DAI on chain B). [10](#0-9) 
3. An honest solver observes the order, calls `fillOrder` on chain B via `_fillCrossChain`, and transfers the DAI output directly to the beneficiary, then the contract dispatches a `RedeemEscrow` message back to chain A. [9](#0-8) 
4. A relayer submits the proof; `onAccept` on chain A decodes the `WithdrawalRequest` (containing both USDC and EvilToken) and calls `_withdraw`. [6](#0-5) 
5. `_withdraw`'s loop reaches the EvilToken leg, `IERC20(EvilToken).safeTransfer(...)` reverts, and the entire transaction — including the USDC transfer to the solver — reverts. [7](#0-6) 
6. Every subsequent relayer submission of the same proof fails identically; the solver's USDC payment is permanently frozen and the message can never be delivered.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L312-373)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }

        // Phase 2: Compute protocol fees and commitment from actual received amounts.
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            order.inputs = reducedInputs;
        } else {
            reducedInputs = order.inputs;
        }
        commitment = keccak256(abi.encode(order));

        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L126-129)
```text
        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
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
