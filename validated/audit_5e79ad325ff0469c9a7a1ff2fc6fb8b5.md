### Title
Escrow release permanently frozen by a single blacklisted-token transfer in an all-or-nothing withdrawal loop - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw()` releases escrowed order tokens to a beneficiary by iterating over the order's token list and calling `IERC20.safeTransfer()` for each entry. `safeTransfer` reverts hard if the underlying ERC-20 (e.g. USDC/USDT) has blacklisted the beneficiary. Because the loop has no per-token error handling or skip mechanism, and because the beneficiary for a given commitment is fixed once encoded in the `WithdrawalRequest`, a single blacklisted address (or blacklisted token) permanently blocks release of *every* token in that order's escrow — mirroring the root cause described in the referenced VUSD `processWithdrawals` finding (an unconditional `safeTransfer`/`transfer` in a loop with no way to skip or redirect a failing recipient).

### Finding Description
`IntentsBase._withdraw()` is the shared internal release routine used for both `RedeemEscrow` (fill payout to the filler) and `RefundEscrow` (refund to the original user) flows: [1](#0-0) 

For each token amount escrowed under the order's commitment, it directly calls `IERC20(token).safeTransfer(beneficiary, amount)` with no try/catch and no ability to substitute an alternate recipient. The equivalent low-level variant in `IntentGatewayV2.sol`'s `withdraw()` has the same shape — a `token.call(...transfer...)` whose failure causes the whole function to `revert TransferFailed()`: [2](#0-1) 

This function is reached from an unprivileged, permissionless path: a relayer submits a proof to `HandlerV2.handlePostRequests`, which calls `host.dispatchIncoming`, which low-level `.call()`s the app's `onAccept`, which for `RequestKind.RedeemEscrow`/`RefundEscrow` calls `withdraw(body, ...)` → `_withdraw(...)`: [3](#0-2) 

`EvmHost.dispatchIncoming` does *not* revert the whole batch on a failed `onAccept` call — it deletes the request receipt "so that it can be retried" and moves on: [4](#0-3) 

This retry-ability is precisely what makes the bug a *permanent* freeze rather than a transient failure: since the beneficiary encoded in the `WithdrawalRequest` (the filler address for `RedeemEscrow`, or `order.user` for `RefundEscrow`) cannot be changed once committed, every retry of the same commitment will fail identically forever if that address is blacklisted on any one of the escrowed tokens. The order's escrow entry in `_orders[commitment][token]` is never decremented (the `safeTransfer`/`transfer` revert unwinds the whole call), so the funds sit permanently locked with no alternate withdrawal path — there is no analogue of a "claimable balance" pull mechanism that the user/filler could use to redeem with a different address.

### Impact Explanation
Funds escrowed for a specific order commitment become permanently frozen if:
- the filler selected to redeem the escrow (`RedeemEscrow` beneficiary) is later blacklisted by the escrowed stablecoin issuer (e.g. Circle/Tether), or
- the original order placer (`RefundEscrow` beneficiary) is blacklisted (griefing/self-lock, or a legitimate user gets blacklisted after placing an order).

Because `_withdraw`/`withdraw` transfers *every* token in `body.tokens` in one atomic loop, even non-blacklisted tokens escrowed in the same order become unreachable, since the whole call reverts on the first failing transfer. There is no mechanism to skip the blacklisted leg or to redirect funds to a different address — this is a direct, permanent freezing of user/filler funds, matching the accepted-impact bar (permanent freezing of funds) even though the blast radius is scoped to the individual order commitment rather than a shared global withdrawal queue.

### Likelihood Explanation
Likelihood is moderate: it requires a participant's address (filler or order-placer) to be on a centralized stablecoin blacklist, which is outside the protocol's control but a realistic, externally-triggered event for any protocol handling USDC/USDT-class assets. Once that occurs, the freeze is deterministic and unavoidable through this code path — no relayer resubmission, no governance action documented in this code, can unstick the specific commitment's escrow.

### Recommendation
Adopt the same mitigations identified in the original report:
1. Switch to a pull-based, per-token withdrawal model: instead of pushing all tokens to the beneficiary in one atomic loop, credit an internal claimable balance per `(commitment, token)` and let the beneficiary claim each token individually (or specify an alternate recipient), so one blacklisted leg cannot block the rest.
2. Alternatively, wrap each `safeTransfer`/`transfer` in a try/catch (or low-level call check) inside the loop and, on failure, route the amount to an escrow/claim mapping keyed by `(token, originalBeneficiary)` rather than reverting the entire `_withdraw`, with a separate `claim(token, altRecipient)` function gated by a signature/authorization from the original beneficiary.
3. Ensure the escrow debit (`_orders[commitment][token] -= amount`) happens for each token independent of the success of other tokens' transfers in the same call.

### Proof of Concept
1. A filler agrees to fill a cross-chain order whose input tokens (escrowed on the source chain) include USDC.
2. The filler successfully fills the order on the destination chain; Hyperbridge dispatches a `RedeemEscrow` POST request back to the source-chain `IntentGatewayV2`/`ExtrinsicIntents` naming the filler as `beneficiary`.
3. Before (or after) the relayer delivers this message, the filler's address is added to USDC's blacklist (via Circle's centralized freeze capability) — e.g. due to a sanctions event or a scam report.
4. A relayer submits the proof; `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `onAccept` → `withdraw`/`_withdraw` executes `IERC20(USDC).safeTransfer(filler, amount)`, which reverts because the recipient is blacklisted.
5. `EvmHost.dispatchIncoming` catches the failure, deletes the receipt, and the message remains "retryable" — but every future retry hits the exact same blacklisted-recipient revert.
6. The escrowed USDC (and any other token bundled in the same order) is now permanently unrecoverable through the exposed contract interface, since `beneficiary` cannot be altered for an already-committed `WithdrawalRequest`. [1](#0-0)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/src/core/EvmHost.sol (L808-817)
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
