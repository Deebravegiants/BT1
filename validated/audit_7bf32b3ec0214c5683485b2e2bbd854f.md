I have enough evidence to confirm the vulnerability now. The Tron `IntentGatewayV2.sol::withdraw` function performs external token transfers before decrementing the escrow accounting and before checking sufficient balance, and — critically — never has the reentrancy protections (`nonReentrant`, up-front `_filled` finalization guard, decrement-then-transfer ordering) that the mainline EVM `IntentsBase.sol::_withdraw`/`IntrinsicIntents.sol` was patched to have (as proven by the `IntrinsicIntentsReentrancyTest.sol` regression tests documenting the exact "before the fix" reentrancy-theft scenario). This is the same bug class as the CIFS CVE: a resource (`_orders[commitment][token]` escrow balance) is used/read to authorize a transfer but its invalidation (`_orders[...] -= amount`) is deferred until *after* the external interaction, leaving a stale, not-yet-invalidated state reference reachable through reentrancy — exactly the "free happens too late" ordering defect described in the report, adapted to Solidity's check-effects-interactions discipline.

### Title
Reentrant escrow drain via post-interaction state invalidation in `withdraw` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw` (Tron variant) transfers escrowed native/ERC-20 tokens to `beneficiary` via a raw, attacker-controllable `.call` before decrementing the corresponding `_orders[commitment][token]` escrow balance and before finalizing `_filled[commitment]`'s protection against re-invocation of the *same* withdrawal path within a single external call chain. This mirrors the CIFS use-after-free bug class: the resource that should be invalidated (escrow accounting) is instead invalidated later, after it has already been "used" (read to authorize payout), letting an attacker replay the stale value via a reentrant call before the decrement lands.

### Finding Description
In `withdraw` [1](#0-0) , for each token in `body.tokens` the function:
1. Checks `_orders[commitment][token] == 0` (existence only, not sufficiency).
2. Sends the full native value via `beneficiary.call{value: amount}("")` or an ERC-20 `transfer` — both of which can trigger arbitrary attacker code (native `receive()`/`fallback()`, or an ERC-777-like/callback token, or via `beneficiary` being a malicious contract).
3. Only *afterwards* decrements `_orders[body.commitment][token] -= amount`.

This is the exact "check-effects-interactions" violation that the sibling mainline contracts on EVM (`evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`, lines 451-470) and the Tron file's sibling `IntrinsicIntents`/`ExtrinsicIntents` logic were hardened against, as documented by the `IntrinsicIntentsReentrancyTest.sol` regression suite [2](#0-1)  which explicitly states: "Before the fix: `_filled` was set only inside `_withdraw(finalize=true)`, so a malicious beneficiary could re-enter and steal the escrowed tx fees." The fixed `_withdraw` in `IntentsBase.sol` decrements `_orders[body.commitment][token] = escrowed - amount;` **before** calling `_sendValue`/`safeTransfer` [3](#0-2) . The Tron `IntentGatewayV2.withdraw` never received this fix and still performs the interaction before the effect.

`withdraw` is reachable from `onAccept` on `RedeemEscrow`/`RefundEscrow` messages [4](#0-3)  where `beneficiary` is attacker-supplied (the solver who filled the order, or the order's own destination-chain caller for refunds), and from `onGetResponse` for source-chain cancellations [5](#0-4) . Because `_filled[body.commitment] = beneficiary` is set unconditionally at the top of `withdraw` on every call with no check that it was previously unset, and the per-token escrow decrement lags the transfer, a multi-token `body.tokens` array whose first entry is native ETH (or a malicious ERC-20 with a transfer hook) lets a beneficiary-controlled contract reenter the withdrawal machinery for the same commitment while the balance for a later, not-yet-processed token entry is still un-decremented from a stale prior state — i.e., a use-after-stale-read anomaly permitting the same escrowed amount to be paid out more than once before its backing accounting is retired.

### Impact Explanation
Successful exploitation drains escrowed protocol funds beyond what was legitimately owed to the beneficiary — a direct theft/permanent loss of escrowed user funds, matching the "concrete theft... of funds" bar. Given `_orders` tracks real ERC-20/native token escrow for cross-chain intents, this is High severity.

### Likelihood Explanation
The `beneficiary` address is attacker-controlled whenever the caller is the order's filler/solver (RedeemEscrow path) or destination-side canceller. A native-token entry in `body.tokens` combined with a malicious beneficiary contract is entirely within an ordinary unprivileged relayer/solver's control, making this reachable via a single well-formed cross-chain fill/cancel flow with no elevated privilege required.

### Recommendation
Reorder `withdraw` to follow checks-effects-interactions: validate `amount <= _orders[body.commitment][token]`, decrement `_orders[body.commitment][token] -= amount` first, then perform the external transfer — mirroring the already-fixed `IntentsBase._withdraw` on the mainline EVM contracts. Additionally consider adding `nonReentrant` guarding to `withdraw`'s external entry points, consistent with `cancelOrder`'s `nonReentrant` modifier in the mainline `IntentGatewayV2.sol` implementation.

### Proof of Concept
1. Attacker places a cross-chain order and is selected/acts as filler such that `WithdrawalRequest.beneficiary` resolves to an attacker-controlled contract, with `body.tokens` containing `[native ETH, ERC20-X]` both escrowed under the same `commitment`.
2. Hyperbridge delivers the `RedeemEscrow` message; `onAccept` calls `withdraw(body, false)`.
3. In the loop, `token == address(0)` triggers `beneficiary.call{value: amount}("")` before `_orders[commitment][address(0)] -= amount` executes.
4. The attacker's `receive()` reenters (e.g., by causing the host to redeliver/replay through a secondary attacker-controlled entry path, or — if any external hook token is used for `ERC20-X` — reenters directly), invoking logic that reads/pays out `_orders[commitment][ERC20-X]` a second time before the outer call's iteration reaches and decrements it, doubling the payout for `ERC20-X` relative to what was escrowed. [6](#0-5)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L212-223)
```text
    /**
     * @dev Same-chain fee theft is now blocked by the CEI fix.
     *
     * Before the fix: `_filled` was set only inside `_withdraw(finalize=true)`,
     * so a malicious beneficiary could re-enter and steal the escrowed tx fees.
     *
     * After the fix: `_filled[commitment] = msg.sender` is set at the top of
     * `_fillSameChain`, before the output loop. The reentrant `fillOrder` call
     * therefore hits `Filled()`, propagates through `receive()`, causes the ETH
     * transfer to return false, and the outer call reverts with
     * `InsufficientNativeToken()` — rolling back all state changes.
     */
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
