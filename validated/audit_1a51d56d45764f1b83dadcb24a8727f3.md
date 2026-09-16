Based on my investigation, the exact analog exists in the intents system's `_sendValue` helper, used by the escrow release/refund path (`_withdraw` / `withdraw`) that is triggered permissionlessly by relayed cross-chain messages.

### Title
Escrowed native-token withdrawal permanently reverts and locks funds if the beneficiary is a contract without `receive()`/`fallback()` - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._sendValue` performs a raw `.call{value: amount}("")` to push native ETH to a beneficiary and unconditionally reverts with `InsufficientNativeToken` if the call fails [1](#0-0) . This helper is the sole mechanism used by `_withdraw` to release escrowed native-token order inputs to `order.user` (refund) or the solver/beneficiary (fill settlement) [2](#0-1) . If the beneficiary address is a contract without a payable `receive()`/`fallback()`, the transfer permanently reverts, and there is no alternate/pull-based recovery path for that token, matching the report's bug class exactly.

### Finding Description
`_withdraw` is invoked from `onAccept` when a `RedeemEscrow` or `RefundEscrow` request is delivered by any relayer via Hyperbridge — this is an unprivileged, permissionless-relayer-reachable path (`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` lines 691-730 mirrors the same logic) [3](#0-2) . The `beneficiary` address is decoded directly from message/order data supplied by the order placer (`order.user`) at `placeOrder` time and is never validated to be able to receive ETH [4](#0-3) . If that address is (or later becomes) a contract without a receive/fallback, every attempt to deliver the `RedeemEscrow`/`RefundEscrow` message — whether cross-chain settlement or same-chain cancellation — reverts inside `_sendValue`, since the whole `_withdraw` loop (and the encompassing `onAccept`/`withdraw` transaction) is atomic and rolls back on failure. There is no `try/catch`, no WETH-wrapping fallback, and no alternative address parameter, unlike the pattern already used elsewhere in this codebase for the exact same problem (`WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout`, which explicitly re-wrap to WETH and deliver ERC-20 on failed native push) [5](#0-4) . `_sendValue` is also reused by `placeOrder`'s overpayment refund and `_sweepDust`, so the same class of failure can also block a `placeOrder` transaction outright or block governance dust sweeps [6](#0-5) [7](#0-6) .

### Impact Explanation
For the `RedeemEscrow`/`RefundEscrow` case specifically, the escrowed native-token input is permanently locked in the gateway contract: the relayed message cannot be delivered successfully (it always reverts), the commitment can never be finalized, and there is no other function that lets the beneficiary pull those specific escrowed funds by a different route. This is a permanent freezing of user/solver funds triggered entirely by a user-controlled parameter (`order.user`/beneficiary address) at order placement — no admin or attacker action is needed beyond placing/filling an order with a non-payable contract as beneficiary.

### Likelihood Explanation
Likelihood is moderate-to-high: any user or integrating contract that places an order and sets `order.user`/beneficiary to a smart-contract wallet, vault, or proxy lacking a payable fallback (a very common real-world configuration, e.g. multisigs or vaults not yet configured for ETH receipt) will trigger this on the settlement/refund leg for native-ETH orders. No special conditions beyond "beneficiary is a contract without receive/fallback" are required.

### Recommendation
Mirror the pattern already implemented in `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`: on failure of `_sendValue`'s low-level call, fall back to wrapping the ETH (e.g., via WETH) and delivering it as an ERC-20 transfer to the beneficiary instead of reverting the whole withdrawal. Alternatively, implement a pull-payment/escrow-credit fallback so that when the push fails, the amount is credited to an internal balance the beneficiary can later withdraw via a separate function, ensuring `onAccept`/`withdraw` can always finalize the order regardless of the beneficiary's ability to accept a direct native transfer.

### Proof of Concept
1. User calls `placeOrder` with `order.output.assets` including a native-token (`address(0)`) output and `order.output.beneficiary` set to `msg.sender`'s own contract address that has no `receive()`/`fallback()`, or a cross-chain order where `order.user` resolves to such a contract for refunds.
2. Escrow is created; later a solver fills the order cross-chain, or the order expires/is cancelled.
3. The relayer delivers `RedeemEscrow`/`RefundEscrow` via `onAccept`, which calls `withdraw`/`_withdraw`, which calls `_sendValue(beneficiary, amount)` for the native-token line item.
4. The low-level `.call{value: amount}("")` fails because the beneficiary contract rejects ETH; `_sendValue` reverts with `InsufficientNativeToken`, reverting the entire `onAccept` transaction.
5. Every subsequent relayer attempt to deliver the same message reverts identically — the escrowed ETH remains permanently locked in the gateway contract with no recovery path.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L418-422)
```text
    /// @dev Native transfer that reverts with `InsufficientNativeToken` if refused.
    function _sendValue(address to, uint256 amount) internal {
        (bool sent,) = to.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-656)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
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

**File:** evm/src/apps/IntentGatewayV2.sol (L224-224)
```text
        order.user = bytes32(uint256(uint160(msg.sender)));
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-324)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```
