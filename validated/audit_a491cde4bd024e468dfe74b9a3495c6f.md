Confirmed: `_withdraw` in `IntentsBase.sol` has no per-token failure isolation or claim-later fallback — a single reverting token transfer atomically blocks the entire withdrawal, and there is no reclaim mechanism anywhere in the codebase (`_withdraw` is the sole exit path for escrowed funds, and the search for `claim`/`reclaim`/`pendingWithdraw` finds nothing on the intents side).

### Title
Atomic multi-token escrow release lets one blacklisted/reverting token freeze all other escrowed tokens in an order - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` releases every token in a `WithdrawalRequest.tokens` array to a single `beneficiary` in one loop, using `IERC20.safeTransfer`/`_sendValue` with no per-token isolation. This function is the single exit path for escrow release across `RedeemEscrow`, `RefundEscrow` and cancel flows. If any one token in the array reverts on transfer to the beneficiary (e.g. a USDC-style blacklist, a paused/frozen token, or any other token with transfer restrictions), the entire `_withdraw` call reverts, which reverts the enclosing `onAccept`/`onGetResponse` call and therefore blocks release of every other, unrelated token escrowed for that same order — even tokens with no restriction at all.

### Finding Description
`_withdraw` is invoked from three places: `onAccept` for `RedeemEscrow`/`RefundEscrow` cross-chain messages [1](#0-0) , `onGetResponse` for source-side cancellation [2](#0-1) , and the same-chain fill/cancel paths in `IntrinsicIntents.sol`. Its implementation iterates `body.tokens` and unconditionally calls `safeTransfer` (or a native `_sendValue`) per token, with no try/catch or partial-success bookkeeping: [3](#0-2) 

Multi-token orders are a first-class feature (`Order.inputs` is a `TokenInfo[]`), so a single order can legitimately escrow several different ERC20s. If any one of those tokens becomes non-transferable to the beneficiary — most commonly a centrally-blacklistable stablecoin like USDC, but also any pausable/permissioned token — the `for` loop reverts atomically on that transfer, unwinding the whole `_withdraw`, including the release of the other, perfectly healthy tokens in the same order.

Because delivery of `RedeemEscrow`/`RefundEscrow` goes through `EvmHost.dispatchIncoming`, a revert inside `onAccept` is swallowed at the host level and the request receipt is deleted so the message "can be retried" [4](#0-3) . But retrying does not help: the same blacklisted beneficiary will cause the exact same revert on every future delivery attempt, since `WithdrawalRequest.beneficiary` is fixed by the original order (the source-chain `order.user` for refunds, or the filling solver for redemptions) and cannot be redirected by anyone. There is no alternate, per-token or beneficiary-substitution reclaim function anywhere in `IntentsBase`/`ExtrinsicIntents`/`IntrinsicIntents` — `_withdraw` is the only way escrowed funds ever leave the contract.

### Impact Explanation
Once the beneficiary is unable to receive even one of the escrowed tokens, the entire order's escrow (all tokens, not just the restricted one) becomes permanently unrecoverable:
- On refund (`_cancelFromDest`/`onGetResponse` → `_withdraw(..., isRefund=true, ...)`), the user's entire multi-asset escrow is stuck if just one input asset is a blacklist-style token and the user's own address (or address they designated) is later blacklisted.
- On redemption (`RedeemEscrow`), the solver's entire payout across all escrowed input tokens is blocked if the solver becomes restricted for any single one of them.

This is a permanent freezing of funds with no recovery path, matching a Medium/High-severity finding: legitimate escrowed assets become irrecoverably locked in the contract due to one token's transfer restriction, and the underlying message can never be successfully delivered because retries hit the identical revert condition every time.

### Likelihood Explanation
Likelihood is moderate: it requires (a) an order/redemption escrowing a token with blacklist/pause/permission semantics (USDC and similar are common in intent-style bridging), and (b) the beneficiary address becoming restricted for that token after the order is placed but before withdrawal completes — a realistic real-world event (regulatory blacklisting, compliance freeze) rather than an artificially engineered attack, making it a plausible and not merely theoretical scenario for any deployment that escrows regulated stablecoins alongside other assets.

### Recommendation
Do not process all tokens in a single atomic loop with no failure isolation. Options:
1. Wrap each per-token transfer in a low-level call/try-catch; on failure, record `(beneficiary, token, amount)` in a per-order "pending claim" mapping instead of reverting the whole `_withdraw`, and expose a public `claim(token, beneficiary)` function so the beneficiary (or a permissionless keeper acting on their behalf) can retry the transfer later or have it redirected to an alternate address they control.
2. Alternatively, allow `finalize`/event emission and escrow-accounting updates to succeed independently per token so a failure on one token does not roll back the successful release of the others (finalize the order and emit the completion event even if some legs are pending claim).

### Proof of Concept
1. Place a cross-chain order with `order.inputs = [USDC: 1000, DAI: 1000]`, `order.user = Alice`.
2. Alice's address gets added to USDC's blacklist (or any transfer-restriction token used as an input) after order placement, for any real-world compliance reason.
3. Alice (or a relayer after the deadline) calls `cancelOrder` from the destination, dispatching `RefundEscrow` with `WithdrawalRequest{tokens: [USDC, DAI], beneficiary: Alice}`.
4. On the source chain, `onAccept` → `_withdraw` iterates the token array: the USDC `safeTransfer` to Alice reverts due to the blacklist, unwinding the entire `_withdraw` call, so the DAI leg is never released either.
5. `EvmHost.dispatchIncoming` swallows the revert and deletes the receipt, marking the message "retryable" — but every future delivery attempt hits the identical USDC blacklist revert, so both the USDC and the otherwise-unaffected DAI escrow are permanently stuck with no alternate withdrawal path in `IntentsBase`/`ExtrinsicIntents`.

### Citations

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-360)
```text
    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
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

**File:** evm/src/core/EvmHost.sol (L809-817)
```text
        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```
