### Title
Cross-chain escrow refund/release can be permanently frozen by a blacklisted beneficiary token transfer, because `dispatchIncoming` marks the message retryable but the transfer failure is not recoverable - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2`/`IntentsBase._withdraw` pushes escrowed ERC-20 tokens directly to `beneficiary` via `IERC20(token).safeTransfer(beneficiary, amount)` inside `onAccept`, which is invoked by `EvmHost.dispatchIncoming` through a low-level `.call`. If the transfer reverts deterministically (e.g., beneficiary is blacklisted by a compliant token such as USDC/USDT), `dispatchIncoming` treats this as a "retryable" failure by deleting the request receipt, but the same deterministic revert will happen on every future retry, permanently freezing the escrowed funds for that order commitment.

### Finding Description
`EvmHost.dispatchIncoming` calls the destination app via a raw `.call`, and on failure deletes `_requestReceipts[commitment]` "so that it can be retried": [1](#0-0) 

This pattern mirrors the exact bug class from the external report: the recovery mechanism assumes that any failure is transient and can succeed on a later resubmission of the same proof/message. However, `IntentsBase._withdraw` (used for `RedeemEscrow`, `RefundEscrow`, and cross-chain fill settlement) unconditionally pushes tokens to the beneficiary address extracted from the withdrawal request, with no fallback / pull-based recovery path: [2](#0-1) 

The `beneficiary` address is attacker-influenced at order-placement time (`order.user`) or solver-controlled at fill time (`msg.sender` on the destination chain, propagated into the `WithdrawalRequest.beneficiary` sent back via `RedeemEscrow`). If that beneficiary is later added to a token's blacklist (or is a token where `transfer` can be made to permanently revert for a specific address — USDC/USDT compliance denylists, `paused` accounts, etc.), then:
1. `onAccept` reverts inside `_withdraw`'s `safeTransfer`.
2. `EvmHost.dispatchIncoming` catches this via `success == false` and deletes the receipt, allowing the exact same commitment/proof to be resubmitted.
3. Every resubmission hits the same deterministic revert because the recipient's blacklist status does not change.
4. The escrowed tokens for that specific order commitment become permanently locked in `IntentGatewayV2`/`IntentsBase`, with no code path to redirect them to a different, unblocked address.

The Tron variant (`evm/tron/contracts/apps/IntentGatewayV2.sol`) has the identical pattern using a manual `.call` + `revert TransferFailed()` instead of `safeTransfer`, so the same freeze applies there too: [3](#0-2) 

This is precisely the first failure mode described in the external report ("if the code ... reverts" due to a blacklisted recipient, the refund/release becomes permanently stuck) — except here the "queue" is the single order's escrow rather than a keeper-processed FIFO index, and the retry mechanism (`dispatchIncoming`'s receipt-deletion) gives a false impression of recoverability since it can never actually succeed for a deterministic per-recipient revert.

### Impact Explanation
Any order whose destination beneficiary (fill destination) or refund beneficiary (`order.user`) becomes blacklisted by the underlying ERC-20 token between order placement and settlement results in permanent loss of the escrowed input tokens and any accumulated fees for that order — a genuine, unrecoverable freezing of user/solver funds within the Intents Gateway, which is a primary economic surface of Hyperbridge (intents escrow and settlement). Because compliant stablecoins (USDC, USDT) are the most likely fee/settlement tokens used with the gateway, and blacklisting decisions are made unilaterally by the token issuer (regulatory action, hack-related freeze, etc.), this is a realistic, non-adversarial trigger, not merely a theoretical griefing vector.

### Likelihood Explanation
Likelihood is moderate: it requires the specific beneficiary address used in an order's escrow release/refund to be blacklisted by the token issuer. This is outside the control of the protocol but is a well-known real-world occurrence for USDC/USDT recipients (sanctions, exploit-related freezes). Because `beneficiary` in the cross-chain settlement path is the solver's `msg.sender` (attacker/solver-chosen at fill time) or the user's own address at cancellation, there is no gate preventing a currently-blacklisted address from being used, nor a mechanism to substitute or later change the recipient once escrow funds are locked to that specific `WithdrawalRequest.beneficiary`.

### Recommendation
Do not push tokens directly to `beneficiary` inside the ISMP-delivered callback path. Instead, following the same remediation HMX applied and the report's own recommendation: credit an internal, per-user withdrawable balance (`_pendingWithdrawals[beneficiary][token] += amount`) inside `_withdraw`, and expose a separate `claim()`/`withdraw()` function that beneficiaries call themselves (pull-based, isolated from the ISMP delivery critical path). This decouples proof delivery for `onAccept` from any specific token's transfer semantics, so a blacklisted or reverting recipient can never block or brick the settlement of an order commitment, and — critically — never permanently loses fund custody, since governance/the affected party can still resolve access to the internal balance later (e.g., by changing the claim recipient through a separate, permissioned recovery path) without needing the token transfer itself to succeed at delivery time.

### Proof of Concept
1. User places a cross-chain order on the source chain via `IntentsBase`/`IntentGatewayV2.placeOrder`, escrowing USDC as input, with `order.user` set to `attackerAddress`.
2. `attackerAddress` is later added to USDC's blacklist by Circle (independent real-world event, or simulated in a fork test by calling USDC's `blacklist(attackerAddress)` as the USDC master minter/blacklister).
3. The order expires; anyone calls `cancelOrder` from the destination chain (post-deadline, permissionless), which dispatches a `RefundEscrow` message back to source with `beneficiary = order.user = attackerAddress`.
4. A relayer submits the proof to `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `IntentsBase.onAccept` → `_withdraw`, whose `IERC20(USDC).safeTransfer(attackerAddress, amount)` reverts due to the blacklist.
5. `dispatchIncoming` catches the failure, deletes `_requestReceipts[commitment]`, and returns normally (transaction itself does not revert).
6. Any subsequent resubmission of the same `RefundEscrow` message (same commitment, same proof) reproduces the identical revert indefinitely — the escrowed USDC for this commitment is now permanently stuck in the gateway contract with no code path capable of releasing it to a different address.

This can be reproduced in a Foundry fork test against `evm/tests/foundry/IntentGatewayV2Test.sol`-style scaffolding by using a mock ERC20 whose `transfer` reverts for a specific "blacklisted" address, exactly mirroring the real USDC/USDT blacklist behavior, and asserting that `_orders[commitment][token]` remains non-zero and unrecoverable after repeated `onAccept` calls.

### Citations

**File:** evm/src/core/EvmHost.sol (L805-817)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```
