### Title
Blacklistable-token beneficiary permanently blocks escrow withdrawal on `RedeemEscrow`/`RefundEscrow` delivery - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` (used by `IntentGatewayV2.onAccept` for both `RedeemEscrow` and `RefundEscrow` message kinds) performs a forced `IERC20.safeTransfer` to the order's `beneficiary` while finalizing state (`_filled[commitment] = beneficiary`, `_orders[...] -= amount`). If the beneficiary's token (e.g. USDC) blacklists that address, the transfer reverts, the whole `onAccept` call reverts, and — per ISMP's handler semantics — no request receipt is persisted, so the message can be replayed but never delivered while the recipient stays blacklisted, permanently freezing the escrowed input tokens for that specific order.

### Finding Description
`IntentGatewayV2.onAccept` decodes `RedeemEscrow`/`RefundEscrow` requests and calls `_withdraw(body, isRefund, true)`: [1](#0-0) 

`_withdraw` finalizes the order and force-transfers escrow to the beneficiary in the same atomic state transition: [2](#0-1) 

The beneficiary is either the solver (on `RedeemEscrow`, chosen by whichever solver filled the order) or the original user (on `RefundEscrow`, after cancellation). Neither is validated against a token-transfer-ability check before this point — `placeOrder`/`fillOrder` never simulate a transfer to the beneficiary. If the input token is a blacklist-capable token (USDC, USDT, and other centrally-administered stablecoins) and the relevant beneficiary address is later or already blacklisted, `IERC20(token).safeTransfer(beneficiary, amount)` reverts unconditionally.

Per the documented ISMP handler contract, a failing `on_accept`/`onAccept` means the request receipt is not persisted, so the message is "replayable" rather than delivered: [3](#0-2) 

That means the message is stuck in permanent limbo: every relayer submission for this specific commitment reverts identically (the beneficiary is still blacklisted), so the escrowed input tokens for that order can never be released — not to the solver via `RedeemEscrow`, and not back to the user via `RefundEscrow`, since `_filled[commitment]` is only set on a successful `_withdraw` and the same forced transfer blocks both paths. This mirrors the OrderBook bug's root cause: a forced token transfer embedded in the finalization/state-mutation step of a claim/withdraw path, with no fallback for undeliverable beneficiaries.

Unlike the OrderBook bug, this does **not** cascade to block *other* orders' processing (Hyperbridge's request handling processes each commitment/message independently, and `HandlerV2.handlePostRequests` dispatches per-leaf with per-request receipts) — see the per-request dispatch loop: [4](#0-3) 
So the blast radius is scoped to the specific order/commitment whose beneficiary is blacklisted, not the whole gateway. This is a materially narrower impact than the OrderBook analog (which froze an entire price-point queue for all future participants via the cyclic-buffer coupling), but it is still a permanent freeze of that user's or solver's escrowed funds with no on-chain recovery path (no alternate beneficiary/redirect mechanism, no partial-skip, no sweep-to-treasury fallback for this case).

### Impact Explanation
An adversarial user or solver — or one whose own address is later added to a blacklist for unrelated reasons — can permanently trap the escrowed input assets of a specific `IntentGatewayV2` order:
- A solver that fills an order and is subsequently blacklisted (or self-selects a blacklisted address as `beneficiary`/fill destination) makes `RedeemEscrow` unexecutable — escrow (user's original tokens) is frozen forever.
- A user whose account gets blacklisted after placing an order but before cancellation/refund similarly makes `RefundEscrow` unexecutable.
This is a permanent freezing-of-funds condition for the affected order, satisfying the "critical" bar for individual-order fund loss, though it does not compromise protocol-wide availability like the original OrderBook bug.

### Likelihood Explanation
Moderate-to-low likelihood organically (requires an already- or soon-to-be blacklisted address to be a legitimate beneficiary), but trivially triggerable by a malicious actor: a solver can simply route `fillOrder`'s beneficiary through/self-select an address it knows will be sanctioned, or a griefer can front-run knowledge of an impending blacklisting action. No privileged access is required — any solver or user interacting with `IntentGatewayV2` on a USDC/USDT pair can create this condition for their own order.

### Recommendation
Decouple state finalization from the token transfer in `_withdraw`: mark `_filled[commitment]` and decrement `_orders[...][token]` unconditionally, but route the actual asset delivery through a pull-based/escrow-credit mechanism (e.g., credit an internal claimable balance for `beneficiary` that can be withdrawn later, or wrap the transfer in a try/catch and, on failure, credit a "stuck funds" balance redeemable by a designated alternate address) rather than a hard `safeTransfer` inside the same atomic finalize path. This is directly analogous to the Clober fix (PR #363): finalize the order/claim state independent of asset delivery success, so a single frozen beneficiary cannot make an order's escrow undeliverable via any path.

### Proof of Concept
1. Deploy `IntentGatewayV2` and a blacklist-capable mock USDC token (as used in existing tests, e.g. `evm/tests/foundry/IntentGatewayV2Test.sol`).
2. User places a cross-chain order with USDC as `inputs[0]`, source chain A, destination chain B.
3. A solver fills the order on chain B with `output.beneficiary` set to an address that USDC will blacklist (or is already blacklisted) — this becomes the `RedeemEscrow` beneficiary on chain A.
4. Relayer delivers the `RedeemEscrow` `PostRequest` to chain A's `IntentGatewayV2.onAccept`.
5. `_withdraw` calls `IERC20(usdc).safeTransfer(blacklistedBeneficiary, amount)`, which reverts (mirroring the `MockSimpleBlockableToken::transfer` "blocked" revert in the original report).
6. `onAccept` reverts; per ISMP semantics no receipt is stored, so the request can be resubmitted indefinitely but will always fail identically. `_filled[commitment]` is never set, and the escrowed USDC in `_orders[commitment][usdc]` remains permanently locked with no code path (redeem, cancel, or refund) able to release it.

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

**File:** docs/content/protocol/ismp/requests.mdx (L104-115)
```text
The request `handle` is used to notify onchain `IsmpModule`s of new requests to be processed. A relayer will construct the `RequestMessage` which holds a batch of new `PostRequest`s, as well as a _multi-proof_<sup>[1]</sup> of their existence on the source chain. The handler will perform the following operations

- Assert that the state machine's consensus client is not frozen
- Assert that the configured `challenge_period` for the `StateCommitment` has elapsed
- Assert that the requests have not been previously processed
- Assert that the requests have not timed out
- Assert that the membership proof for the requests verify
- Finally dispatch the requests to the relevant `IsmpModule::on_accept` and store a receipt for each request to prevent requests from being replayed.

<Callout title={'Danger'} type={"warn"}>
It's important to note that if the `IsmpModule::on_accept` does not return `Ok`, the receipt of this request will not be persisted, allowing the request to be **replayed**. Consequently, the `IsmpModule` is responsible for maintaining all invariants before modifying it's internal state to prevent partial state changes that could result in critical vulnerabilities in their request handler. This model ensures that if a request cannot be executed successfully on a destination state machine, it can time out gracefully on the source.
</Callout>
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```
