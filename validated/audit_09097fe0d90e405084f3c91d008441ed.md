### Title
Malicious order creators can escrow a "poison" ERC-20 that permanently blocks `_withdraw`/`onAccept`, freezing all input escrow and denying solvers their cross-chain reward - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentsBase._withdraw` iterates over a `WithdrawalRequest.tokens` array and performs a `safeTransfer` for every escrowed token in a single atomic loop [1](#0-0) . An unprivileged user placing an order chooses the `order.inputs` token list, and can include a malicious ERC-20 that reverts transfers to any address other than the depositor (e.g. an allow-list/blacklist token). Because the loop is atomic, this single poisoned token blocks release of *every* token escrowed for that order, and since the message is delivered via `EvmHost.dispatchIncoming`, which silently swallows the revert and marks the message retryable, the failure is permanent and can never be worked around by relayers [2](#0-1) .

### Finding Description
For cross-chain fills, `_fillCrossChain` in `ExtrinsicIntents.sol` has the solver deliver output tokens to the beneficiary on the destination chain first, then dispatches a `RedeemEscrow` Hyperbridge post request back to the source chain naming `msg.sender` (the solver) as the beneficiary of *all* of `order.inputs`: [3](#0-2) 

On the source chain, `onAccept` authenticates the request and calls `_withdraw(body, ..., true)` with `body.tokens = order.inputs`, and finalization marks the order filled: [4](#0-3) 

`_withdraw` then loops over every escrowed token and does a `safeTransfer` to the solver: [1](#0-0) 

If the order creator included a malicious token among `order.inputs` that only allows transfers back to the depositor's own address (or to a fixed allow-list), the `IERC20(token).safeTransfer(beneficiary, amount)` call for that token reverts. Since Solidity loops/calls are atomic, the entire `_withdraw` call reverts — meaning the *other, legitimate* escrowed tokens in the same order (e.g. USDC/DAI amounts) are also blocked from release, not just the poisoned one.

Because `onAccept` is invoked through `EvmHost.dispatchIncoming`, a reverting callback does not revert the whole ISMP delivery transaction; instead the receipt is deleted "so it can be retried" and the function returns normally: [5](#0-4) 

Any relayer retry re-executes the same `onAccept` call with the same immutable order data, hitting the same malicious token behavior every time. The `RedeemEscrow` message can therefore never be successfully delivered, and the escrow for that commitment (all input tokens, including any legitimate ones bundled with the poison token) is permanently stuck in the `IntentGateway`/`ExtrinsicIntents` contract.

Critically, by the time this happens the solver has *already* transferred real value to the order's beneficiary on the destination chain (`_fillCrossChain` executes the output transfer and calldata *before* dispatching the `RedeemEscrow` message). The solver therefore suffers an unrecoverable, uncompensated loss, while the malicious order creator's poisoned escrow (and any co-escrowed legitimate tokens) become permanently frozen in the contract. The identical pattern exists in the Tron variant's `withdraw()` function [6](#0-5) .

The same-chain path (`IntrinsicIntents._cancelSameChain` / fill flow) is less impactful since the beneficiary of a self-cancel refund is the order creator themselves, so they cannot use this to steal from others directly — but the cross-chain fill path lets a malicious order creator weaponize the poisoned token against any solver who fills the order and against the protocol's escrow accounting integrity.

### Impact Explanation
This is a permanent freezing-of-funds and message-non-delivery bug reachable by any unprivileged user submitting a single `placeOrder` transaction with a crafted ERC-20 as one of the order inputs:
- The `RedeemEscrow` cross-chain message can never be delivered/finalized for that commitment — it is retried indefinitely but always reverts, matching the "route unable to deliver messages" class.
- Escrowed input tokens (potentially bundled legitimate tokens alongside the poison token) are permanently locked in the gateway contract with no recovery path, since `_withdraw` is the only code path that releases escrow and it always reverts for that commitment.
- Solvers who filled the order in good faith and already paid out real output value on the destination chain lose that value with no compensation, since their `RedeemEscrow` reward can never be claimed.

This satisfies the "permanent freezing of funds" / "route unable to deliver messages" criteria for Medium severity.

### Likelihood Explanation
Likelihood is high: placing a malicious order requires only a normal `placeOrder` call with attacker-chosen `order.inputs` (no privileged capability needed), and no validation of token behavior (whitelist) exists in `IntentsBase`/`ExtrinsicIntents`/`IntrinsicIntents`. A solver would need to inspect the token contract to detect the trap, but nothing in the protocol prevents fillers from being lured into filling such orders, and the resulting freeze/DoS is deterministic once triggered.

### Recommendation
- In `_withdraw` (`IntentsBase.sol`) and the Tron `withdraw()` equivalent, isolate per-token transfer failures (e.g., wrap each `safeTransfer` in a try/catch or use a pull-based claim per token) so a single malicious token cannot block release of the other escrowed tokens for the same commitment.
- Consider allowing partial/best-effort withdrawal accounting: on a failed transfer for one token, leave that token's escrow claimable later (or mark it forfeited/sweepable) instead of reverting the entire withdrawal.
- Optionally support a token allow-list or a `safeTransfer`-with-gas-limit pattern to bound the blast radius of adversarial token implementations, consistent with the original report's recommendation.

### Proof of Concept
1. Attacker deploys `PoisonToken`, an ERC-20 whose `transfer`/`transferFrom` reverts unless `to == attacker` (or `to` is on a hard-coded allow-list containing only the attacker's address).
2. Attacker calls `placeOrder` on the source chain with `order.inputs = [ {token: USDC, amount: X}, {token: PoisonToken, amount: Y} ]`, a valid `output` requesting some token on a destination chain, per `ExtrinsicIntents`/`IntentGatewayV2` semantics [7](#0-6) .
3. A solver fills the order cross-chain via `fillOrder` → `_fillCrossChain`, delivering the requested output tokens to `order.output.beneficiary` on the destination chain and dispatching the `RedeemEscrow` request naming itself as beneficiary [3](#0-2) .
4. A relayer delivers the `RedeemEscrow` message to the source chain; `onAccept` calls `_withdraw` with `body.tokens = [USDC, PoisonToken]` and `beneficiary = solver` [4](#0-3) .
5. `_withdraw`'s loop reaches the `PoisonToken` transfer to the solver, which reverts; the whole `_withdraw` call reverts, so even the USDC portion is never released [1](#0-0) .
6. `EvmHost.dispatchIncoming` catches the revert, deletes the request receipt so it "can be retried," and returns without delivering the message [5](#0-4) .
7. Every subsequent relayer retry hits the exact same revert deterministically. The solver never receives the escrowed USDC/PoisonToken reward despite having already paid out the output assets on the destination chain in step 3, and both tokens remain permanently locked in the source-chain contract for that commitment.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-212)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L211-300)
```text
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

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

```
