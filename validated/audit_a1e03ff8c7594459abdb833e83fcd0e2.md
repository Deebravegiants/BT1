### Title
Persistent revert in `_withdraw`'s beneficiary transfer permanently freezes escrowed intent funds - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw`, invoked from the `IntentGatewayV2.onAccept` `RedeemEscrow`/`RefundEscrow` handling, transfers escrowed tokens directly to a fixed `beneficiary` via `IERC20.safeTransfer`/`_sendValue` with no `try/catch`. `EvmHost.dispatchIncoming` wraps the entire `onAccept` call in a low-level `.call` and, on failure, simply deletes the request receipt to make the message "retryable" — but if the transfer to `beneficiary` fails deterministically (e.g. a blacklisted/paused token, or a beneficiary contract that reverts on receipt), every retry fails identically, forever. This is the same bug class as the `2024-01-salty` `DAO._executeApproval` finding: an unhandled external-call revert inside a state-finalizing function leaves the underlying state (`_filled[commitment]`, escrow accounting) permanently stuck instead of failing gracefully.

### Finding Description
`_withdraw` is called for both `RedeemEscrow` (settlement releasing escrow to the solver) and `RefundEscrow` (cancellation refund to the user) messages processed in `onAccept`: [1](#0-0) 

The loop performs `_orders[body.commitment][token] = escrowed - amount;` (state mutation) immediately before the token transfer `IERC20(token).safeTransfer(beneficiary, amount);` in the same iteration, with no fallback if the transfer reverts. Because `finalize` also sets `_filled[body.commitment] = beneficiary` up front, the order is marked filled/refunded as soon as `_withdraw` is entered, but the whole call — and thus the entire `onAccept` transaction — reverts if any single token transfer fails.

At the host level, `EvmHost.dispatchIncoming` for `PostRequest` delivery uses a low-level `.call` and, on failure, deletes the request receipt so the same message can be resubmitted: [2](#0-1) 

This "retry" mechanism assumes the failure is transient. But `beneficiary` in `WithdrawalRequest` is a value baked into the cross-chain message itself (determined at fill time on the destination chain, or by the order's own `user` field for cancellations) and cannot be changed by any relayer or governance action. If `beneficiary` is a token-blacklisted address, a token that has been paused, or a contract whose `receive`/fallback permanently reverts, `safeTransfer`/`_sendValue` will fail identically on every retry — the message can never be delivered successfully.

### Impact Explanation
Once a `RedeemEscrow`/`RefundEscrow` message can never be delivered:
- The escrowed input tokens for that order remain locked in the `IntentGatewayV2`/`IntentsBase` contract forever — they can neither be released to the solver nor be refunded to the user, since the only code path that moves them (`_withdraw`) is the one that permanently reverts.
- Because the message never finalizes on the destination side (`_filled` mapping is never actually committed, since the transaction reverts), the order also cannot be re-cancelled through the normal cancellation flow (its state is ambiguous — not filled, not refunded, but the escrow-decrement side effects were rolled back with the revert, so the order is stuck in limbo relative to the source chain that already believes settlement is in flight).
- This is a concrete permanent freezing of user/solver funds with no on-chain recovery path, matching the "concrete... permanent freezing of funds" acceptance criteria.

### Likelihood Explanation
Reaching this state does not require any privileged actor: it can be triggered by an ordinary intent flow where a solver (for `RedeemEscrow`) or a user (for `RefundEscrow`) specifies (or later becomes, e.g. via `USDC`/`USDT` blacklisting) a `beneficiary` address for one of the escrowed tokens that permanently rejects transfers. Given that `IntentGatewayV2` explicitly supports common tokens like USDC/USDT (which have centralized blacklist functionality) as escrowable assets, and beneficiaries are arbitrary addresses supplied via the order/fill flow, this is a realistic, unprivileged, single-message scenario — directly analogous to the original report's "approved ballot that can never be finalized" root cause.

### Recommendation
Mirror the confirmed fix pattern from the referenced report: don't let a single beneficiary-side external call failure permanently block escrow finalization. Options:
- Wrap each token transfer in `_withdraw` in a `try/catch` (or low-level `call` with success check) and, on failure, credit the amount to a per-user pull-payment/rescue balance instead of reverting the whole withdrawal, so other tokens in the same request still settle and the order still finalizes.
- Alternatively, decouple `_filled` finalization from the transfer loop so that a transfer failure doesn't leave the commitment state stuck, and provide a permissionless "sweep to rescue mapping" function beneficiaries (or anyone) can call to retrieve stuck funds through an alternate mechanism (e.g. a different address).

### Proof of Concept
1. An intent `Order` escrows `USDT` as an input token on the source chain.
2. A solver fills the order on the destination chain; the settlement `WithdrawalRequest` (`RedeemEscrow`) sets `beneficiary` = the solver's address.
3. Before the `RedeemEscrow` message is relayed and delivered, the solver's address is added to `USDT`'s blacklist (a realistic centralized-stablecoin risk) — or the solver used a beneficiary contract without a payable/ERC777 hook rejecting the token.
4. The relayer submits the proof; `EvmHost.dispatchIncoming` → `IntentGatewayV2.onAccept` → `_withdraw` → `IERC20(USDT).safeTransfer(beneficiary, amount)` reverts (`transfer` returns false / reverts due to blacklist).
5. `EvmHost.dispatchIncoming` catches the failure, deletes the request receipt so the message is "retryable" — but every subsequent relay attempt fails identically because `beneficiary` never changes.
6. The escrowed `USDT` for this order is now permanently stuck in the `IntentGatewayV2` contract: it cannot be released (transfer always reverts) and the order cannot be cancelled through the normal flow since `_filled` was never durably committed.

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
