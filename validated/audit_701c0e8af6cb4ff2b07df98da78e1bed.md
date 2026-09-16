This confirms the mechanism: `EvmHost.dispatchIncoming` (for POST requests) does a low-level `.call` into the destination app's `onAccept`, and on failure just deletes the receipt "so that it can be retried" and returns — it does not revert the whole message, but it also never succeeds if the revert condition is permanent. [1](#0-0) 

This is the exact analog of M-6.

### Title
Blacklisted escrow beneficiary permanently blocks Intent order settlement/refund - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` (used by both `RedeemEscrow` and `RefundEscrow` handling in `ExtrinsicIntents.onAccept`) and its Tron equivalent `IntentGatewayV2.withdraw` send escrowed input tokens directly to a fixed `beneficiary` address via `safeTransfer`/low-level `transfer` inside the cross-chain message handler. If that token is a blacklist-capable stablecoin such as USDC and the beneficiary (the solver on `RedeemEscrow`, or the original `order.user` on `RefundEscrow`) is on the token's blacklist, the transfer reverts, which reverts the entire `onAccept` call and can never succeed, exactly like Nounsdao's `Stream.cancel()` sending directly to `recipient_`.

### Finding Description
`_withdraw` iterates the withdrawal request's tokens and unconditionally does `IERC20(token).safeTransfer(beneficiary, amount)`, decrementing escrow accounting *before* the external call, and only marks `_filled[body.commitment] = beneficiary` when `finalize` is true (which happens in the same call): [2](#0-1) 

This function is invoked from `onAccept` for both `RedeemEscrow` (releasing input tokens to the solver who filled the order) and `RefundEscrow` (refunding the user after cancellation) — the same beneficiary address for the entire commitment, hard-coded into the cross-chain `WithdrawalRequest` when the order was placed/filled: [3](#0-2) 

The Tron `IntentGatewayV2.withdraw` implementation has the identical pattern using a raw `.call` to `transfer` and reverting with `TransferFailed` on failure: [4](#0-3) 

Delivery of this `onAccept` call happens through `EvmHost.dispatchIncoming`, which does a low-level `.call` and, on failure, simply deletes the request receipt "so that it can be retried" — it never reverts the message permanently, but it also never succeeds if the revert condition (the recipient being blacklisted) is permanent: [1](#0-0) 

Because the beneficiary address is baked into the order/commitment (`order.user` for refunds, `msg.sender`-the-filling-solver for redemptions) and cannot be changed after the order is placed/filled, if USDC (or any other blacklist-capable ERC20) is used as an input token and the beneficiary is later added to that token's blacklist:
- `RedeemEscrow` can never deliver the escrowed input tokens to the solver — the solver already delivered the output assets to the user off-chain/on-chain but can never be paid, and the escrow is permanently stuck in the gateway contract.
- `RefundEscrow` can never refund the original user their escrowed input tokens if a cancellation occurs after the user (or an address they control) is blacklisted — the user's principal is permanently frozen in the gateway.

This is the exact bug class in M-6: a single fixed transfer to a potentially-blacklisted recipient, embedded inside a state-changing function with no alternate claim path, causes indefinite freezing of funds rather than just failing gracefully.

### Impact Explanation
Escrowed ERC20 input tokens (e.g., USDC) become permanently locked in the `IntentGatewayV2`/`ExtrinsicIntents` contract with no recovery path: neither the solver (on redemption) nor the user (on refund) can ever retrieve them once the beneficiary address is blacklisted on the token, because the beneficiary is immutably encoded in the commitment/`WithdrawalRequest` and `_withdraw` has no alternate destination or pull-based claim mechanism. This is a permanent freezing-of-funds condition reachable by any order flow that uses a blacklist-capable ERC20 as an input token.

### Likelihood Explanation
Any user or solver interacting with the intents system using USDC (or another blacklistable stablecoin) as an input asset is exposed. The condition requires the beneficiary address to become blacklisted by the token issuer at some point between order placement and settlement/refund — plausible for solver addresses (which are more likely targets of compliance action given they operate at scale) and for users whose addresses get flagged for unrelated reasons. No malicious actor needs to be involved on Hyperbridge's side; this is a standard "third-party centralized token control" griefing/DoS vector identical to the referenced Sherlock finding.

### Recommendation
Do not push tokens directly to the beneficiary inside `_withdraw`/`withdraw`. Instead, credit the beneficiary's balance in an internal ledger (e.g., `_claimable[beneficiary][token] += amount`) when releasing/refunding escrow, and expose a separate `claim()` function that the beneficiary (or anyone, paying out to the beneficiary) can call to pull funds later. This decouples the cross-chain message-processing critical path from any single token transfer succeeding, preventing one blacklisted address from freezing the entire commitment's escrow.

### Proof of Concept
1. User places a cross-chain order with `order.inputs = [USDC, amount]`, `order.user = attackerControlledAddress`.
2. A solver fills the order on the destination chain and dispatches `RedeemEscrow` naming the solver (`msg.sender`) as `beneficiary` in the `WithdrawalRequest` — see `_post(order, _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))), …)` in `ExtrinsicIntents.sol` around line 207-212.
3. Before the Hyperbridge relayer delivers this message back to the source chain, USDC's issuer blacklists the solver's address (e.g., due to unrelated compliance action).
4. The relayer submits the proof; `EvmHost.dispatchIncoming` calls `ExtrinsicIntents.onAccept`, which calls `_withdraw`, which calls `IERC20(USDC).safeTransfer(beneficiary, amount)` — this reverts because `beneficiary` is blacklisted.
5. `dispatchIncoming` catches the failure, deletes the request receipt, and returns without reverting the whole batch — the message is "retryable" but will fail identically on every future attempt since the blacklist status persists.
6. The escrowed USDC (`_orders[commitment][USDC]`) remains locked in the gateway contract forever; no other function allows redirecting or reclaiming it since `beneficiary` is fixed in the already-dispatched `WithdrawalRequest`.

### Citations

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
