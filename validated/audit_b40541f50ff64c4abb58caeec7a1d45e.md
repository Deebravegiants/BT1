### Title
Escrow withdrawal reverts entirely if any single input token transfer fails, permanently freezing all other escrowed tokens in the order - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` (and its duplicate, `IntentGatewayV2.withdraw` in the Tron variant) iterates over every token in a `WithdrawalRequest.tokens` array and transfers each one to the beneficiary in a single call. If any one of those `IERC20.safeTransfer` (or low-level `.call`) invocations reverts, the entire withdrawal reverts — blocking the release of *all* the other, otherwise-transferable escrowed tokens in the same order, exactly as described in the referenced OpenQ report where dependent per-token transfers inside one loop can be griefed by a single malicious/reverting token.

### Finding Description
`placeOrder` lets a user (order creator) specify an arbitrary set of `order.inputs` tokens to escrow, with no allowlist enforced on token contracts: [1](#0-0) 

When the order is later settled — via `RedeemEscrow` (solver claim) or `RefundEscrow` (cancellation), delivered through `onAccept`, or via `onGetResponse` for source-initiated cancellation — `_withdraw` is invoked and loops over `body.tokens`, calling `IERC20.safeTransfer` for each token to the beneficiary: [2](#0-1) 

The same pattern exists in the Tron fork's `withdraw`, which uses a raw `.call` and explicitly reverts with `TransferFailed()` on any single-token transfer failure: [3](#0-2) 

`onAccept` calls `_withdraw`/`withdraw` directly for both `RedeemEscrow` and `RefundEscrow`: [4](#0-3) 

and `onGetResponse` (source-side cancellation path) calls the same function: [5](#0-4) 

Since a multi-input order's escrow is only released atomically as a whole (one token cannot be skipped), a user placing an order with two or more input tokens — one of them a token that unconditionally reverts on transfer to a specific address (e.g., a blacklist/pausable/fee-on-transfer-with-caps token, or one deliberately crafted to revert when the recipient is the solver or a particular address) — makes the entire `_withdraw` call permanently revert both for the `RedeemEscrow` (solver claim) path and for `RefundEscrow`/`onGetResponse` (cancellation/refund) path, since they hit the identical loop and identical malicious token.

### Impact Explanation
Because both the fill-settlement path and the cancellation/refund path route through the exact same `_withdraw` loop over the same `body.tokens`, once one token in a multi-input order is malicious/reverting:
- The solver who legitimately filled the order on the destination chain (already paid out real output tokens) can never redeem the escrowed inputs on the source chain.
- The user cannot cancel/refund the order either, since `RefundEscrow`/`onGetResponse` iterate over the same token list and hit the same revert.

This results in permanent freezing of all escrowed tokens for that order — including the well-behaved tokens bundled alongside the malicious one — with no opt-out or per-token skip mechanism, and no recovery path once the order is placed with such a token combination. This qualifies as a High-severity permanent freezing-of-funds condition matching the reachable Hyperbridge attack surface (a single `placeOrder` transaction from any unprivileged user).

### Likelihood Explanation
`placeOrder` places no restriction on the ERC-20 contracts used as `order.inputs`, so any user (attacker) can construct an order with a normal token plus a custom malicious token designed to always revert transfers to a specific counterparty (e.g., revert if `to == solver_address` or simply always revert after the order is placed and escrow accepted). Triggering the freeze requires only a single `placeOrder` call plus a subsequent `fillOrder`/cancel attempt by a victim solver or user — no privileged role, governance, or cross-chain race condition needed. `EvmHost.dispatchIncoming` swallowing the `onAccept` revert (deleting the receipt so "the message stays deliverable") does not help: because the failure is deterministic (the token always reverts), retries will always fail identically, so the freeze is permanent.

### Recommendation
Do not let a single failing transfer in `_withdraw`/`withdraw` block the release of the other tokens in the order:
- Wrap each per-token transfer in a try/catch (or low-level call already used in the Tron variant) and continue the loop on failure, tracking which tokens failed to be delivered.
- Allow a separate, permissionless "sweep" or "retry" function per (commitment, token) so undelivered tokens can be claimed later once conditions change, instead of gating the whole order's settlement and finalization (`_filled[...]`, event emission, fee release) on every token succeeding.
- Alternatively, validate/whitelist acceptable input tokens at `placeOrder` time, or cap the blast radius by settling each token in its own external call/transaction rather than one atomic loop.

### Proof of Concept
1. Deploy a malicious ERC-20 `EvilToken` whose `transfer`/`transferFrom` succeeds normally except it `revert()`s whenever `to` equals a specific address the attacker controls in advance (or simply reverts unconditionally after the order's escrow phase).
2. User calls `placeOrder` with `order.inputs = [ {token: USDC, amount: X}, {token: EvilToken, amount: Y} ]` and a valid output — see the escrow flow in `evm/src/apps/IntentGatewayV2.sol` (`placeOrder`, lines 194-256).
3. A solver fills the order via `fillOrder` on the destination chain (or, for same-chain, `_fillSameChain`/`_fillCrossChain`), and the settlement message (`RedeemEscrow`) is delivered to `onAccept` on the source chain, invoking `_withdraw(body, false, true)`.
4. Inside `_withdraw`'s loop (`evm/src/apps/intentsv2/IntentsBase.sol:456-470`), the `IERC20(EvilToken).safeTransfer(beneficiary, amount)` call reverts, causing the entire `_withdraw` call — and thus the entire `onAccept`/settlement — to revert, even though the USDC transfer would have succeeded.
5. The user's attempt to cancel and refund via `RefundEscrow`/`onGetResponse` hits the identical loop over the identical `EvilToken`, and also reverts.
6. Both the USDC and EvilToken escrow amounts, plus any escrowed transaction fees, remain permanently locked in the contract with no code path able to release them.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-256)
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
