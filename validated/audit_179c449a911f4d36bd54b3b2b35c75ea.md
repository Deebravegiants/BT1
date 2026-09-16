### Title
Blacklistable ERC-20 tokens (USDC/USDT) can permanently freeze escrowed funds in Intents `_withdraw`/`withdraw` - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
The Intents (`IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents`) escrow-release path transfers escrowed input tokens directly to a `beneficiary` address decoded from the settlement message, with no fallback if that transfer reverts. If the debt/input token is a blacklist-capable token (USDC, USDT, etc.) and the beneficiary (the filler/solver on `RedeemEscrow`, or the order's user on `RefundEscrow`/cancel) is blacklisted by the token issuer, the transfer permanently reverts, and since `EvmHost.dispatchIncoming` simply resets the receipt to allow "retry" on failure, the same call will keep failing forever — permanently freezing the escrowed funds with no recovery mechanism.

### Finding Description
`IntentsBase._withdraw` unconditionally pushes tokens to the decoded beneficiary: [1](#0-0) 

and the fee-token forward right after it uses the same unguarded pattern: [2](#0-1) 

The Tron-side `IntentGatewayV2` mirrors this with a low-level call that reverts with `TransferFailed()` on failure, which is equally fatal to the whole `onAccept`/`onGetResponse` invocation: [3](#0-2) 

This code is reached from two unprivileged, permissionless flows:
1. **`RedeemEscrow`** — after a solver fills a cross-chain order (`_fillCrossChain` in `ExtrinsicIntents.sol`), a settlement message is dispatched back to the source chain; on delivery, `onAccept` calls `_withdraw` to pay the solver (`beneficiary` = the filler) the escrowed input tokens.
2. **`RefundEscrow`/cancel** — a `GetResponse` path (`onGetResponse`) or `RefundEscrow` message calls `_withdraw` with `beneficiary` = the original order's `user`, to refund escrow after cancellation.

Both `beneficiary` values are attacker/user-controlled inputs baked into the order/fill at order-placement or fill time — any address can be named as filler or user, including one the token issuer later blacklists.

Crucially, the host's incoming-message dispatch treats a failed `onAccept`/`onGetResponse` call as "retryable" rather than reverting the whole transaction: [4](#0-3) [5](#0-4) 

This "retry" is not actually a self-healing feature here: because the transfer inside `_withdraw` will always revert for the same blacklisted address, resubmitting the exact same message will fail every single time. Unlike a state-machine bug, this failure is deterministic and permanent as long as the token issuer keeps that beneficiary blacklisted (in practice, indefinitely) — the escrowed tokens (and any accumulated fee-token rewards) become permanently locked in the gateway with no alternate withdrawal path.

### Impact Explanation
The escrowed input tokens are the user's or protocol's principal value locked in `IntentGatewayV2`/`ExtrinsicIntents`. A single blacklisted `beneficiary` — reachable purely through normal order placement/filling by unprivileged users — makes the corresponding escrow entry undeliverable forever: the solver can never claim their `RedeemEscrow` payout, or the user can never claim their `RefundEscrow`. This is a permanent freezing of funds for at least the affected order(s), matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood is realistic wherever the escrowed input token is a centrally-blacklistable stablecoin (USDC, USDT are extremely common bridge assets). Any solver or user whose address later gets blacklisted (for unrelated reasons, e.g. sanctions/compliance actions) with an in-flight or historical order immediately loses access to their legitimate escrow, and no privileged or governance action in the current code can rescue it — `_withdraw`/`withdraw` have no beneficiary-override or pull-payment fallback.

### Recommendation
Do not let a single failed transfer to an attacker/user-controlled address block escrow release. Wrap the `IERC20.transfer`/`safeTransfer` calls in `_withdraw` (`IntentsBase.sol`) and `withdraw` (`IntentGatewayV2.sol`) in a try/catch (or low-level call check without reverting), and on failure credit the amount to an internal per-beneficiary claimable balance that can be pulled later (optionally to an alternate address supplied by the beneficiary), instead of reverting the entire settlement/refund call.

### Proof of Concept
1. A user places a cross-chain order with USDC as the input token via `placeOrder`, escrowing USDC in `IntentGatewayV2`/`ExtrinsicIntents`.
2. A solver fills the order on the destination chain (`_fillCrossChain`), naming its own address (or any address) as `msg.sender`/filler; this becomes the `beneficiary` in the resulting `RedeemEscrow` `WithdrawalRequest`.
3. Before the settlement message is delivered back to the source chain, Circle blacklists the filler's address in USDC (e.g., due to unrelated sanctions/compliance action).
4. When the relayer delivers the `RedeemEscrow` message, `EvmHost.dispatchIncoming` calls `onAccept` → `_withdraw`, which calls `IERC20(USDC).safeTransfer(beneficiary, amount)`; this reverts because the recipient is blacklisted.
5. Per `dispatchIncoming`'s failure handling [6](#0-5) , the receipt is deleted so the message "can be retried" — but every future relay attempt reverts identically, so the escrowed USDC remains locked in the gateway indefinitely, with no other function able to release it to the solver or anyone else.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-477)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
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

**File:** evm/src/core/EvmHost.sol (L820-839)
```text
    /**
     * @dev Dispatch an incoming GET response to source module
     * @param response - get response
     */
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }
```
