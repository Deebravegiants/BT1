### Title
Blacklisted-token transfer in `_withdraw` permanently freezes all other escrowed assets in the same order - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw()` releases every escrowed token for an order in a single loop of unconditional `IERC20.safeTransfer` calls to one `beneficiary`. If the beneficiary (the order's `user`, on a refund/cancel path, or the `solver`, on a fill path) is blacklisted by any *one* of the escrowed input tokens (e.g. USDC/USDT-style compliance lists), that single `safeTransfer` reverts and rolls back the entire withdrawal — including the release of every other, non-blacklisted token bundled in the same order. This mirrors the Aloe `Borrower.liquidate()` DOS pattern cited in the report: a single asset transfer that can be made to revert blocks an entire multi-asset settlement operation.

### Finding Description
`_withdraw` iterates over `body.tokens` and transfers each escrowed token to `beneficiary` without isolating individual transfer failures: [1](#0-0) 

```solidity
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
    ...
}
```

`_withdraw` is reached from:
- `ExtrinsicIntents._cancelFromSource` → Hyperbridge GET response → `onGetResponse` → `_withdraw(..., isRefund=true, finalize=true)` — refunds *all* of `order.inputs` to `order.user` in one call.
- `onAccept` handling `RedeemEscrow`/`RefundEscrow` POST requests (fill settlement and destination-initiated cancel) — same all-tokens-in-one-call pattern, releasing to `msg.sender`/solver or `order.user`.
- The same-chain analogue, `IntrinsicIntents._cancelSameChain`, also collects *all* remaining escrowed input tokens for the order into a single `_withdraw` call.

Because a user can freely construct a multi-input order (`order.inputs` contains several `TokenInfo` entries, potentially different ERC20s), and because ordinary compliant tokens like USDC/USDT can later blacklist an address, one blacklisted token in the bundle is enough to make the entire settlement/refund transaction revert forever, regardless of how many other tokens are in the same order.

Delivery through the ISMP host is failure-isolated at the message level (`EvmHost.dispatchIncoming` uses a low-level `.call()` and deletes the receipt on failure so the *message* can be retried): [2](#0-1) 

This isolation only prevents one failing message from blocking *other* messages/orders — it does not help the affected order itself: retrying the exact same `WithdrawalRequest` re-executes the identical loop and reverts on the same blacklisted token every time, since the compliance block cannot be lifted by the protocol.

### Impact Explanation
Any order whose `inputs` include a blacklistable stablecoin, where the refund/settlement beneficiary later becomes blacklisted on just that one token, permanently locks:
- All other escrowed input tokens in that same order (which may be entirely unrelated, non-blacklisted assets), and
- Any accrued transaction fees (`TRANSACTION_FEES`) tied to the same commitment, which are only released inside the same `finalize` branch after the token loop succeeds.

This is a permanent freezing of funds for the affected order — not merely a temporary retry-able delay — because the root cause (an external token issuer's blacklist on the beneficiary) is outside the protocol's control and the code has no per-token isolation or beneficiary-override/rescue path. The severity is amplified relative to a single-token bridge (e.g. `WrappedHyperFungibleToken`, which locks only that one asset) because here N-1 unrelated, non-blacklisted assets are frozen collaterally with the blacklisted one.

### Likelihood Explanation
Reachability requires only ordinary, permissionless usage: any user can place a multi-input order via `IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents` mixing a blacklistable token (USDC, USDT, or any compliance-gated ERC20) with other assets. The blacklisting event itself is triggered by the token issuer, not the protocol, but it is a well-known and realistic condition for widely-used stablecoins, and no attacker action beyond normal order placement is needed to set up the freeze. Likelihood is medium: it depends on an external compliance event, but affects a broad, generic code path (`_withdraw`) used by every cancel/refund/fill-settlement flow in the intents system.

### Recommendation
Isolate each token transfer in `_withdraw` so that a revert on one token does not block release of the others — e.g. wrap each `safeTransfer`/native send in a try/catch (or low-level call with success check) and, on failure, keep that specific token's escrow balance intact (or move it to a per-user/per-token pull-based rescue mapping) while still finalizing and releasing all other tokens and fees. This decouples the fate of unrelated escrowed assets from the compliance status of any single token/beneficiary pair.

### Proof of Concept
1. `order.user` places a cross-chain order with `order.inputs = [TokenA(1000), USDC(1000)]`, escrowing both tokens in `IntentGatewayV2`/`IntentsBase` on the source chain.
2. Before the order is filled or cancelled, USDC's issuer blacklists `order.user`'s address (a realistic, externally-triggered event).
3. `order.user` (or a relayer, post-deadline) calls `cancelOrder` → `_cancelFromSource` → GET request → `onGetResponse` → `_withdraw({tokens: [TokenA, USDC], beneficiary: order.user}, isRefund=true, finalize=true)`.
4. The loop first transfers `TokenA` successfully, decrementing its escrow; on the `USDC.safeTransfer(beneficiary, amount)` call it reverts because `beneficiary` is blacklisted.
5. The whole `_withdraw` call, and therefore the whole `onGetResponse`/`onAccept` delivery, reverts. Because the underlying `EvmHost.dispatchIncoming` catches this and deletes the receipt, the message becomes retryable — but every retry hits the same USDC blacklist revert.
6. Result: `TokenA`'s escrow amount (already decremented in the failed attempt's memory state, but reverted on-chain) and USDC's escrow remain stuck in the contract permanently; `order.user` can never recover `TokenA`, `USDC`, or the accrued fee, even though `TokenA` itself has no compliance issue.

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
