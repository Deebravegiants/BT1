### Title
Withdrawal of multi-token escrow reverts entirely on a single frozen/blacklisted token, permanently locking order cancellation and fill settlement - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw()` (and the equivalent `withdraw()` in the tron and V2 `IntentGatewayV2.sol` variants) iterates over the `WithdrawalRequest.tokens` array and calls `safeTransfer` (or a raw `.call` with `TransferFailed()` revert-on-failure in the Tron/legacy variant) for every escrowed token in a single loop. This mirrors the reported `Account.sweepTo` bug class: if any one of the multiple input tokens escrowed for an order becomes non-transferable (blacklist, pausable token, hacked/frozen contract), the entire withdrawal reverts, and there is no per-token fallback or skip logic.

### Finding Description
`_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` (lines 451-485) loops over `body.tokens`, decrementing escrow and calling `IERC20(token).safeTransfer(beneficiary, amount)` for each token: [1](#0-0) 

Because `Order.inputs` is a `TokenInfo[]`, a single order can escrow multiple distinct tokens (multi-input orders). This function is the single settlement primitive for:
- Same-chain cancellation, called directly by the user via `cancelOrder` → `_cancelSameChain` → `_withdraw`: [2](#0-1) 
- Cross-chain refund/redeem, dispatched by an unprivileged relayer delivering a Hyperbridge `RedeemEscrow`/`RefundEscrow` post request via `onAccept`: [3](#0-2) 
- GET-response driven cancellation from source, via `onGetResponse`: [4](#0-3) 

The identical pattern exists in the legacy/Tron `IntentGatewayV2.sol` `withdraw()` function, which uses low-level `.call` with an explicit `revert TransferFailed()` on failure for each token in the loop, and also has no per-token isolation: [5](#0-4) 

If a user places a multi-input order whose inputs include, say, USDC and a second ERC-20 token, and that second token later becomes frozen for the escrow contract or the beneficiary address (blacklist event, token-level pause, token contract compromise, or even a token that reverts on transfers to specific addresses), then:
1. The user can never cancel the order (same-chain path reverts every call).
2. A solver can never redeem escrow after filling (cross-chain `RedeemEscrow` `onAccept` call reverts).
3. A relayer can never deliver the refund/redeem message successfully — Hyperbridge's message can be delivered, but `onAccept` will revert on every attempt, so the message can never be finalized/applied even though the proof itself is valid.

This is functionally identical to the Sherlock finding on Sentiment's `Account.sweepTo`/`AccountManager.closeAccount`: a single bad/frozen asset in a batch transfer permanently blocks the whole settlement operation for every other (unaffected) token in the same order, freezing all escrowed funds for that order indefinitely.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by a normal, unprivileged user action (placing/cancelling a multi-token order) combined with a token-level event outside the protocol's control (blacklist/freeze/pause on one input token). All tokens escrowed for that order — including the otherwise-healthy ones — become permanently unrecoverable, since `_withdraw`/`withdraw` has no ability to partially settle or skip a failing token. Given Hyperbridge's intents module supports arbitrary ERC-20 tokens as inputs (including tokens with centralized blacklist authorities like USDC/USDT), this is a realistic and Medium-severity liveness/fund-freezing risk, not a low-likelihood edge case.

### Likelihood Explanation
Likelihood is Medium: it requires (a) a multi-input order and (b) one of the input tokens becoming non-transferable after escrow (blacklist action, token pause, or compromised token contract) before the order is cancelled/filled/refunded. USDC/USDT-style blacklistable stablecoins are extremely common intents/bridge assets, making the freeze scenario plausible in production usage, though it depends on external token-issuer action rather than attacker-controlled logic within Hyperbridge itself.

### Recommendation
Make per-token transfers in `_withdraw`/`withdraw` fault-tolerant instead of atomic-or-nothing:
- Wrap each token transfer in a try/catch (or low-level call check) so a failure on one token does not revert the whole loop; still decrement/track escrow per-token and emit a per-token failure event.
- Provide a separate recovery/sweep path that lets the beneficiary or governance later retry the transfer for a specific failed token (e.g., leave failed amounts in an "unclaimed" mapping keyed by `(commitment, token)` claimable independently), similar to the recommended fix in the source report (bypass `safeTransfer`'s revert-on-failure guarantee for the batch, and expose an emergency, best-effort withdrawal path).

### Proof of Concept
1. User places a cross-chain order with `order.inputs = [TokenA (healthy), TokenB (blacklistable stablecoin)]`, escrowing both tokens in the source `IntentsBase`/`IntentGatewayV2` contract.
2. Before the order is filled or cancelled, TokenB's issuer blacklists the escrow contract or the `beneficiary` address (a routine centralized-stablecoin compliance action).
3. User calls `cancelOrder` for a same-chain order (or a relayer delivers the cross-chain `RefundEscrow`/`RedeemEscrow` message to `onAccept`).
4. `_withdraw`/`withdraw` iterates `body.tokens`; the `safeTransfer`/`call` for TokenB reverts (blacklist check inside the token's `transfer`).
5. The entire transaction reverts — TokenA, which is perfectly transferable, is never released either, and escrow for both tokens remains locked in the contract with no available retry path, since every future call to cancel/redeem hits the same TokenB transfer failure.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-470)
```text
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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
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
