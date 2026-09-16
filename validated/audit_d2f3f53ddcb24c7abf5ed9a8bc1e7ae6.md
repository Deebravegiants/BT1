### Title
Permanent freezing of multi-token order escrow when a single input token becomes non-transferable (paused/blacklisted) - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw()` releases every token in a `WithdrawalRequest.tokens[]` array inside one loop using `safeTransfer`. If any single token in that array reverts on transfer (e.g., it is paused, or the beneficiary is blacklisted by a centralized stablecoin issuer), the entire function reverts, permanently blocking release of *all* other tokens in the same order — including tokens that would have transferred successfully and the accumulated relayer fee — since there is no per-token isolation or fallback path.

### Finding Description
`_withdraw` is the single settlement primitive used by both `RedeemEscrow` and `RefundEscrow` post-request handling (`onAccept`) and by the GET-response cancellation path (`onGetResponse`) in `ExtrinsicIntents.sol`. It iterates over `body.tokens` and unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)` for every entry: [1](#0-0) 

Because `SafeERC20.safeTransfer` reverts the whole call on failure, a single non-transferable token (paused ERC20, blacklisted recipient on tokens like USDC/USDT, or a token that later becomes non-transferable after order placement but before settlement) causes the entire `_withdraw` to revert — including the loop iterations for all *other*, perfectly healthy tokens in the same multi-asset order, plus the fee-token payout that follows in the same function: [2](#0-1) 

This is reached from the cross-chain settlement handler `onAccept`, which is invoked by the ISMP host once a relayer delivers a valid `RedeemEscrow`/`RefundEscrow` message: [3](#0-2) 

At the dispatch layer, `HandlerV2.handlePostRequests` only marks a request as processed via `host.requestReceipts` after `dispatchIncoming` succeeds — a reverting `onAccept`/`_withdraw` means the request receipt is never durably recorded as delivered, so the relayer can retry, but the retry hits the exact same revert forever if the offending token remains non-transferable (permanent pause, permanent blacklist): [4](#0-3) 

The same class of issue is present in the standalone (non-upgradeable) `IntentGatewayV2` variant, where `withdraw()` also loops over `body.tokens` and reverts the whole batch (`TransferFailed()`) if any single token transfer fails: [5](#0-4) 

Because orders can escrow and be redeemed with multiple `TokenInfo` entries (`order.inputs` / withdrawal `tokens[]`), and because the withdrawal token list and amounts are fixed at order-fill/cancel time and re-delivered verbatim by the cross-chain message, there is no way for the beneficiary, solver, or protocol to exclude or skip the poisoned token and unblock the rest of the escrow — the commitment and message body cannot be altered post-hoc.

### Impact Explanation
A user or solver escrow spanning multiple tokens becomes permanently unrecoverable if any one of the escrowed tokens is paused by its issuer or the beneficiary is blacklisted (a realistic and common occurrence for centralized stablecoins such as USDC/USDT, which is exactly the scenario the referenced report describes). This blocks:
- Release of the healthy tokens bundled in the same `WithdrawalRequest` (solver's other output assets or user's other refunded inputs),
- The accumulated relayer/transaction fee payout tied to the same commitment,
- Any future retry, since the relayed message content is immutable and will always hit the same reverting transfer.

This is a permanent freezing of funds for legitimate order participants triggered by a single third-party token action, satisfying the Medium severity bar for locked collateral.

### Likelihood Explanation
Likelihood is realistic but not attacker-controlled in the simplest case — it requires a token used as an order input/output to become non-transferable (pause, blacklist) between order placement and settlement, which is a known and recurring event for major stablecoins. It can also be deliberately engineered by a user/solver constructing an order with a token they know is likely to be paused/blacklisted, combined with other valuable tokens, to grief settlement or lock their own/counterparty's funds until the token issuer intervenes (if ever).

### Recommendation
Isolate per-token transfer failures in `_withdraw`/`withdraw` (e.g., wrap each `safeTransfer`/low-level transfer call so a failing token does not revert the loop; use a pull-based claim per token, or move failed-token amounts to a separate "stuck" ledger that can be retried or claimed independently once the token becomes transferable again), so that a single non-transferable token cannot block release of the other escrowed assets and fees within the same order.

### Proof of Concept
1. User places a same-chain or cross-chain `Order` with two input tokens: `USDC` and `MaliciousToken` (or a real stablecoin later blacklisted for the beneficiary address).
2. Order is filled/cancelled normally; the settlement path computes a `WithdrawalRequest` containing both tokens.
3. Before settlement is delivered, the issuer of `MaliciousToken`/USDC blacklists the beneficiary address or pauses transfers.
4. Relayer delivers the `RedeemEscrow`/`RefundEscrow` message; `onAccept` → `_withdraw` iterates the token list, reaches the blacklisted token's `safeTransfer`, and reverts.
5. The entire transaction reverts — the healthy `USDC` amount, the fee-token payout, and the finalize/emit logic never execute. Every retry by any relayer reproduces the same revert as long as the token remains non-transferable, permanently locking the escrowed funds.

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

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
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
