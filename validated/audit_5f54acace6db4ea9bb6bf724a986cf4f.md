This confirms the analog. The Tron `IntentGatewayV2.withdraw` function releases escrow using a low-level `.call()` with the transfer selector but only checks the `success` boolean (that the call didn't revert), never inspecting the returned ABI-encoded boolean payload. Combined with placing/filling flows that use `SafeERC20.safeTransferFrom` correctly elsewhere in the same repo, this is an inconsistent, unmitigated instance of the exact bug class from the report.

### Title
Unchecked ERC20/TRC20 return-data in escrow withdrawal permanently freezes bridged funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw` (Tron variant) releases escrowed order funds and protocol fees to a beneficiary using a raw low-level `.call()` to the token's `transfer` selector, checking only that the call itself did not revert (`success`). It never decodes/validates the returned `bool` payload, so any ERC20/TRC20 token that signals failure by returning `false` (rather than reverting) is treated as a successful transfer.

### Finding Description
`withdraw` is invoked from `onAccept` (for `RedeemEscrow`/`RefundEscrow` requests delivered by a relayer via Hyperbridge) and from `onGetResponse` (for cross-chain cancellation refunds) — both are single-relayed-message-driven, unprivileged-reachable entry points once a proof/message is delivered: [1](#0-0) 

Inside `withdraw`, escrow accounting is decremented and the order is marked filled *before/regardless of* whether the token transfer actually succeeded, based purely on `success` from the raw call: [2](#0-1) 

The same unchecked pattern repeats for transaction fee payout and for the `SweepDust` handler: [3](#0-2) [4](#0-3) 

By contrast, the rest of the codebase (including the canonical EVM `IntentGatewayV2.sol`, `IntentsBase.sol`, `HyperFungibleToken.sol`, etc.) consistently uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, which decodes the return data and reverts on `false`: [5](#0-4) 

A low-level `.call()` only returns `success = false` if the callee reverts or the call fails at the EVM/TVM level; if a non-standard token (a class of tokens fairly common on TRON) executes without reverting but returns `abi.encode(false)` to signal a failed transfer (e.g., due to a blacklist, paused state, or insufficient allowance/balance edge case in a non-reverting implementation), `success` remains `true` here. The function then proceeds to decrement `_orders[...]`, mark `_filled[commitment] = beneficiary`, and emit `EscrowReleased`/`EscrowRefunded` as if the beneficiary was paid, when in fact no tokens moved.

### Impact Explanation
Once `withdraw` finalizes (`_filled` set, `_orders` decremented, event emitted), the order can never be redeemed or refunded again — the escrow accounting believes the funds were paid out. If the underlying token silently returns `false` instead of reverting, the beneficiary receives nothing while the escrowed collateral remains locked in the contract with no code path to reclaim it. This is a permanent freeze/loss of user or solver funds through the intents escrow settlement path, matching the report's core claim that failing to check a transfer's return value can cause collateral to be "lost forever" while positions are marked settled.

### Likelihood Explanation
This path is reached on every `RedeemEscrow`/`RefundEscrow` delivery and every `SweepDust`/fee payout on the Tron deployment of `IntentGatewayV2` — a normal, expected part of intent fulfillment that requires no attacker privilege, only that a listed order token behave as a non-reverting, boolean-returning ERC20/TRC20 on failure (a known, common pattern for TRC20/legacy ERC20 tokens). No malicious relayer or governance action is needed; the relayer is simply delivering a legitimately proven cross-chain message.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw` (escrow release, fee release) and in the `SweepDust` handler with OpenZeppelin's `SafeERC20.safeTransfer`, as is already done consistently elsewhere in the codebase (`IntentsBase._withdraw`, `HyperFungibleToken`, etc.), so a `false` return or non-standard token behavior reverts the whole delivery instead of silently finalizing escrow state.

### Proof of Concept
1. A user places a cross-chain order on the source chain, escrowing `token X` (a TRC20/ERC20 whose `transfer` returns `false` on failure instead of reverting — e.g. when the recipient is blacklisted, or under some internal capacity condition) in `IntentGatewayV2` on Tron.
2. The order is filled on the destination chain; the destination gateway dispatches a `RedeemEscrow` message via Hyperbridge.
3. A relayer delivers this message with a valid proof; `onAccept` decodes it and calls `withdraw(body, false)`.
4. In `withdraw`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` executes without reverting but the token contract returns `false` in its return data (transfer did not occur).
5. `success` is `true`, so the code does **not** revert with `TransferFailed`; it proceeds to decrement `_orders[commitment][token]` to zero and set `_filled[commitment] = beneficiary`, emitting `EscrowReleased`.
6. The beneficiary's token balance never increased — the escrowed tokens are now permanently stuck in `IntentGatewayV2` with no remaining code path (order already marked filled) to retrieve them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
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
