### Title
Escrowed order funds can be permanently frozen if the input/output ERC20 token is pausable or supports blacklisting the beneficiary - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
The intent gateway's escrow release path (`_withdraw`) performs an unguarded `safeTransfer` to the beneficiary when redeeming or refunding escrowed order tokens. If the token used as an order input can be paused (e.g. temporarily halted) or the specific beneficiary address can be blacklisted (e.g. USDC/USDT-style tokens), the transfer permanently reverts, and there is no mechanism in the protocol to redirect the beneficiary or otherwise recover the escrowed funds — mirroring the "pausable NFT freezes bridge funds" bug class from the referenced report, but here applied to the intents escrow.

### Finding Description
`_withdraw()` in [1](#0-0)  releases escrowed tokens with a direct `IERC20(token).safeTransfer(beneficiary, amount)` and no failure handling — if the transfer reverts, the whole call reverts.

This function is invoked from two permissionless, cross-chain-triggered entry points:
- `onAccept()` for `RedeemEscrow`/`RefundEscrow` messages: [2](#0-1) 
- `onGetResponse()` for the source-chain cancel path: [3](#0-2) 

Both are dispatched by `EvmHost.dispatchIncoming`, which does handle low-level call failure by deleting the request receipt so delivery can be retried: [4](#0-3)  and [5](#0-4) . This is *better* than the reported OptimismPortal bug (which marks the withdrawal finalized regardless of call success), but it does not solve the underlying issue: if the `beneficiary` embedded in the `WithdrawalRequest` (always `order.user` for refunds, or the filler for redemptions) is permanently blacklisted on the escrowed token, or the token is paused indefinitely, every retry of `onAccept`/`onGetResponse` will keep reverting forever. The documentation for the cancel-from-destination path explicitly confirms the beneficiary cannot be changed by anyone, including relayers acting on the user's behalf: [6](#0-5) .

The same pattern (unguarded low-level `.call` with `revert TransferFailed()` on failure, with no beneficiary-redirection recovery) exists in the Tron variant's `withdraw()`: [7](#0-6) .

### Impact Explanation
Once a token used as an order input becomes untransferable to the specific stored beneficiary (temporary pause turning effectively permanent, or a blacklist entry that is never lifted), the escrowed tokens for that order are permanently stuck in the `ExtrinsicIntents`/`IntentGatewayV2` contract. There is no admin sweep, no alternate beneficiary path, and no timeout-based fallback for escrow withdrawal itself (timeouts in this protocol only apply to message delivery, not to the withdrawal logic once the message *is* delivered and reverts). This is a permanent freezing of user/solver funds, matching the Medium severity of the original report.

### Likelihood Explanation
This requires the order's input/output token to be a pausable or blacklist-capable ERC20 (common for stablecoins like USDC/USDT and various compliance-gated tokens) and the specific beneficiary address to become permanently restricted (compliance blacklist, sanctions, or an extended/indefinite pause). This is a realistic occurrence for real-world stablecoins integrated with the intent gateway, and requires no privileged or malicious actor within the protocol — it is triggered purely by the external token's own compliance logic while the escrow flow is fully permissionless.

### Recommendation
Wrap the `safeTransfer` calls in `_withdraw()` (and the Tron `withdraw()`) in failure-tolerant logic: on transfer failure, escrow the funds into a per-beneficiary claimable balance (pull-based) instead of reverting the entire withdrawal, so retries of `RedeemEscrow`/`RefundEscrow`/`onGetResponse` don't remain permanently blocked by one non-transferable token, and expose an alternate-recipient/rescue mechanism gated appropriately (e.g. allow the original beneficiary to designate a different receiving address once functionally unable to receive the original transfer).

### Proof of Concept
1. Alice places a cross-chain order using a pausable/blacklistable ERC20 (e.g. a USDC-like token) as an input, escrowed by `ExtrinsicIntents`/`IntentGatewayV2`.
2. Before the order is filled, Alice's address (or the eventual beneficiary) gets blacklisted on that token (compliance action, independent of Hyperbridge).
3. The order expires; anyone triggers `cancelOrder()` from the destination chain, which dispatches `RefundEscrow` back to source chain with `beneficiary = order.user` fixed in the message: [8](#0-7) .
4. When delivered, `onAccept()` calls `_withdraw()`, which calls `safeTransfer(beneficiary, amount)` — this reverts because the beneficiary is blacklisted: [9](#0-8) .
5. `EvmHost.dispatchIncoming` catches the revert and deletes the receipt so it can be retried, but every retry hits the same blacklist and reverts identically, forever: [4](#0-3) .
6. The escrowed tokens remain locked in the gateway contract permanently, with no way to redirect the beneficiary per the documented cancellation design: [6](#0-5) .

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** evm/src/core/EvmHost.sol (L809-818)
```text
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

**File:** evm/src/core/EvmHost.sol (L832-839)
```text
        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }
```

**File:** docs/content/developers/evm/intent-gateway/cancelling-orders.mdx (L279-282)
```text
Cancelling from the destination chain is simpler and does not require a storage proof. The destination gateway immediately marks the order as settled, blocking any future fill attempts, and sends a refund message to the source chain via Hyperbridge. When the message arrives, the source chain authenticates it as coming from the registered destination gateway and returns the escrowed tokens to the original user.

Before and **at** the order deadline only the order creator can trigger this path. From the first destination block after the deadline, anyone may call. This lets relayers act on behalf of users whose orders have expired without being filled, providing a recovery mechanism that does not require the user to be online. The caller pays the dispatch cost, but cannot change `WithdrawalRequest.beneficiary`: the refund always goes to `order.user`.

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
