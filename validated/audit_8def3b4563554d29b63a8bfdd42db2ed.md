### Title
Unchecked ERC20 return value in Tron `IntentGatewayV2.withdraw()`/`SweepDust` allows escrow accounting to finalize without actual token transfer - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` uses a raw low-level `.call` with the `IERC20.transfer.selector` to move escrowed tokens out of the contract, and only checks that the *call itself* did not revert (`success`), never decoding/verifying the returned `bool`. This is the exact bug class described in the external report: non-compliant or edge-case ERC20 tokens that return `false` instead of reverting will cause the contract to believe a transfer succeeded even though no tokens moved, finalizing escrow state on a phantom transfer.

### Finding Description
In `withdraw()`, both the per-token escrow release and the fee-token release use: [1](#0-0) [2](#0-1) 

and the `SweepDust` handler does the same: [3](#0-2) 

In all three spots, the code does `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount)); if (!success) revert TransferFailed();`. `success` here only reflects whether the external call reverted — it does **not** verify the ABI-decoded boolean return value of `transfer()`. Per EIP-20, callers "MUST handle false from returns (bool success)" and "MUST NOT assume false is never returned." A token that returns `false` (rather than reverting) on a failed transfer — e.g., due to an internal check, blacklist, pause, or other application-level restriction — will make `token.call(...)` return `success = true` at the call level while zero tokens actually move.

Crucially, before this transfer happens, `withdraw()` has already decremented the escrow bookkeeping and (on finalize) marked the order filled/refunded: [4](#0-3) 

So if the transfer silently fails, `_orders[commitment][token]` is already zeroed and `_filled[commitment]` is already set, but the beneficiary never received the tokens — they remain permanently stuck in the `IntentGatewayV2` contract with no accounting path left to reclaim them.

By contrast, the canonical EVM `IntentsBase._withdraw()` (used by the non-Tron `IntentGatewayV2.sol`) correctly uses OpenZeppelin's `SafeERC20.safeTransfer`, which reverts on a `false` return: [5](#0-4) 

The Tron contract deliberately avoids `safeTransfer`/`safeTransferFrom` for outgoing transfers (it does use `safeTransferFrom` for incoming escrow deposits) and instead reimplements the check incorrectly for outgoing releases.

### Impact Explanation
`withdraw()` is the function that finalizes cross-chain intent settlement: it is invoked from `onAccept()` (processing a `RedeemEscrow`/`RefundEscrow` message delivered by any relayer via Hyperbridge) and from `onGetResponse()` (processing a source-chain cancellation). Because these are triggered by cross-chain messages relayed by an unprivileged relayer following normal solver/cancel flows, a solver or user filling/cancelling an intent order routed to a Tron deployment against a token with this behavior would have their escrowed funds permanently frozen in the gateway contract — the accounting state says "released" while the funds never left the contract, and there is no retry mechanism since `_orders[...]` is already zeroed. This is a permanent loss/freezing of user/solver funds.

### Likelihood Explanation
Likelihood depends entirely on whether a token listed for intents on the Tron deployment can return `false` from `transfer` without reverting (e.g., paused/blacklisted transfer scenarios, or any token implementing soft-fail semantics). Given Tron's ecosystem includes several TRC20 tokens with non-standard/soft-fail transfer semantics (mirroring the USDT-style behavior called out in the original report), and the flow is reachable by any relayer delivering a normal settlement message (no privileged action required), this is a realistic, medium-likelihood condition once such a token is used in an order.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` (lines ~706, ~720) and the `SweepDust` handler (line ~674) of `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with how `IntentsBase._withdraw()` already does it on the main EVM contract, and consistent with how the Tron contract already uses `safeTransferFrom` for incoming transfers. This ensures both call-level failures and `false`-return failures cause a revert rather than a silently accepted phantom transfer.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a token `T` whose `transfer()` returns `false` (does not revert) when the recipient is disallowed/paused, instead of reverting.
2. A user places an order escrowing `T` on the source chain; a solver fills it on the destination chain, and the source `IntentGatewayV2` dispatches a `RedeemEscrow` message.
3. A relayer delivers the message; `onAccept()` calls `withdraw()`, which decrements `_orders[commitment][T]` and calls `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`.
4. If `T.transfer()` internally returns `false` (e.g., beneficiary is blacklisted at this moment) rather than reverting, `success` is still `true` at the call-level, so `TransferFailed()` is not raised.
5. `_filled[commitment]` is set and `EscrowReleased` is emitted, but `T.balanceOf(beneficiary)` never increased — the tokens remain locked in `IntentGatewayV2` with no remaining escrow record to claim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-470)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```
