### Title
Multi-token orders can permanently strand escrow if the beneficiary is blacklisted by any single input/output token - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
### Finding Description
`Order.inputs` and `Order.output.assets` are arrays of `TokenInfo`, so a single order can escrow/pay out multiple distinct ERC-20 tokens under one commitment [1](#0-0) . Both the "redeem" (fill accepted) and "refund" (cancel) paths converge on `IntentsBase._withdraw`, which loops over `body.tokens` and unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)` for each token to a single, non-configurable `beneficiary` address: [2](#0-1) 

This is functionally identical to the reported Maia `BranchBridgeAgent.redeemDeposit` bug: many tokens are bundled under one commitment and sent atomically, in a loop, to one immutable address, with no ability for the caller to redirect a subset of the funds or specify an alternate recipient.

`beneficiary` for `RedeemEscrow`/`RefundEscrow` is derived from `WithdrawalRequest.beneficiary`, which for the cancel-from-destination and cancel-from-source flows is fixed to `order.user` at `placeOrder` time and cannot be altered later [3](#0-2) . For `RedeemEscrow` the beneficiary is the filler/solver address chosen at fill time, likewise fixed once the order is filled.

If `beneficiary` is on a token-level blacklist (USDC/USDT-style compliance blacklist, or any transfer-restricted token) for even one of the several tokens in `body.tokens`, the `safeTransfer` for that token reverts inside the `for` loop. Since Solidity reverts unwind the *entire* call, none of the other (perfectly fine) tokens in the same order are transferred either, and `_orders[body.commitment][token]` amounts are not decremented for any token — the whole multi-token escrow is left stuck.

Critically, this revert propagates up through `onAccept`, which is invoked via a raw low-level `.call` from `EvmHost.dispatchIncoming`. On failure, the host deletes the message receipt and returns without reverting the outer transaction, explicitly to make the message "retryable": [4](#0-3) 

This "retryable" design assumes failures are transient (e.g., temporary revert conditions). But a token-level blacklist against a fixed, un-substitutable `beneficiary` is not transient — every future relayer resubmission of the same message will hit the exact same revert, forever. There is no code path that lets the `beneficiary`/user split the withdrawal per-token, substitute a different recipient, or otherwise recover the non-blacklisted tokens bundled in the same order. The result is a permanent freeze of the full multi-token escrow (including the assets that have nothing to do with the blacklisted token) for that order commitment.

The same pattern also exists in the tron variant of the gateway, whose `withdraw` function loops over `body.tokens` calling `token.call(...transfer...)` and reverts the whole delivery on any single transfer failure [5](#0-4) .

### Impact Explanation
An order escrowing multiple input tokens (or paying out multiple output tokens) becomes permanently unrecoverable if the fixed beneficiary/user address is blacklisted by even one of the constituent tokens (e.g., a USDC/USDT compliance blacklist). This is a **permanent freezing of user/solver funds**: all tokens bundled into that order commitment — not just the blacklisted one — become stuck in the `IntentGatewayV2` contract with no governance, admin, or user-level recovery mechanism, since `_withdraw`'s beneficiary is derived from immutable order/fill data and there is no partial-withdrawal or beneficiary-override path. This matches the "concrete... permanent freezing of funds" acceptance bar. Severity is Medium/High depending on multi-token order usage, consistent with the original Maia finding's Medium rating.

### Likelihood Explanation
Likelihood is moderate: it requires (1) an order with multiple input or output tokens where at least one is a blacklist-capable token (common for USDC/USDT and many regulated stablecoins), and (2) the order's user or filler being blacklisted on just one of those tokens. Given regulated stablecoins are widely used as intent-gateway assets and blacklisting events do occur (sanctions, compliance actions, exploit-related freezes), this is a realistic, single-transaction/relayed-message trigger requiring no privileged access — any unprivileged relayer resubmitting the message reproduces the permanent revert.

### Recommendation
- In `IntentsBase._withdraw` (and the tron `withdraw` equivalent), do not let a single token's transfer failure block the others: wrap each per-token transfer in a try/catch (or use a low-level `call` and check success without reverting the loop) and credit any tokens that fail to transfer to a per-user, per-token "pending withdrawal" balance that the beneficiary (or a designated alternate address) can later pull via a separate `claim(token, to)` function.
- Alternatively, allow the beneficiary to specify (or later update) an alternate receiving address for withdrawal, similar to the Maia fix recommendation of adding a caller-supplied `_receiver` parameter, so a blacklisted address is not a permanent dead end.
- At minimum, decouple redemption per-token so that a revert on one token does not roll back the successful transfers of the other tokens in the same order/commitment.

### Proof of Concept
1. `placeOrder` an order with `inputs = [TokenA, TokenB]` where `TokenB` is a blacklist-capable stablecoin, source chain X.
2. Fill or cancel the order such that `RefundEscrow`/`RedeemEscrow` is dispatched to chain X with `beneficiary = order.user` (a fixed address).
3. Before the message is delivered, `TokenB` blacklists `order.user`.
4. A relayer calls `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `IntentGatewayV2.onAccept` → `IntentsBase._withdraw`. The loop transfers `TokenA` successfully, then reverts on `TokenB.safeTransfer(beneficiary, ...)`.
5. `EvmHost.dispatchIncoming` catches the failure, deletes the receipt, and returns without reverting the outer transaction — the request is marked as not-yet-delivered and can be resubmitted [6](#0-5) .
6. Every subsequent relayer resubmission of the same message hits the identical revert on `TokenB`, so `TokenA` (and any other well-behaved tokens in the same order) can never be withdrawn either — the entire multi-token escrow for that commitment is permanently stuck in `IntentGatewayV2`.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L228-234)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L301-307)
```text

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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
