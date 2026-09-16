### Title
Native ETH escrow release via `_sendValue` can permanently freeze order funds when the beneficiary rejects ETH - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._sendValue` and its inline duplicates in `IntentGatewayV2.sol` / `ExtrinsicIntents.sol` / `IntrinsicIntents.sol` push native ETH with a low-level `.call{value: amount}("")` and hard-`revert` on failure, exactly like the `GenericToken.transferNativeTokenOut` pattern in the referenced report. Because these calls sit on critical settlement paths (escrow release/refund, cross-chain redemption, order fills) where the recipient address is attacker-influenceable, a beneficiary contract that reverts on receiving ETH can permanently block fund release.

### Finding Description
`_sendValue` reverts unconditionally if the ETH push fails: [1](#0-0) 

It is used inside `_withdraw`, the function that releases escrowed native-token inputs (or refunds them) to a `beneficiary` derived from message/order data: [2](#0-1) 

The `beneficiary` passed into `_withdraw` for the cross-chain redemption path is the `msg.sender` value that filled the order on the destination chain, propagated back to the source chain in the `RedeemEscrow` body constructed in `_fillCrossChain`: [3](#0-2) 

A solver (or anyone controlling the `msg.sender` used to fill the order) can be, or route through, a contract with no `receive()`/payable `fallback()`. When the `RedeemEscrow` POST request is delivered back on the source chain and `onAccept` calls `_withdraw` for that commitment/beneficiary, the `_sendValue` call to that contract will always revert, causing `onAccept` to revert deterministically for that message. The same failure mode also appears in the inline (non-`_sendValue`) native transfer used in `IntrinsicIntents.sol`'s partial-fill path, and in the escrow refund path (`_withdraw` is also called for order cancellation refunds to `order.user`): [4](#0-3) 

Since ISMP message delivery for POST requests only marks a request handled on a successful `onAccept` execution, a beneficiary that always reverts on ETH receipt makes the redemption/refund message permanently non-deliverable, mirroring the "Accounts can't be liquidated" bug class: a hardcoded low-level `.call`/`.transfer`-style native push with an unconditional revert-on-failure blocks a critical, non-optional settlement action rather than degrading gracefully (e.g. falling back to a wrapped-token transfer, as is done correctly elsewhere in the codebase for `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout`, which explicitly re-wrap to WETH on failed native push): [5](#0-4) 

The intents contracts (`IntentGatewayV2.sol`, `ExtrinsicIntents.sol`, `IntrinsicIntents.sol`, `IntentsBase.sol`) do not implement this fallback for the escrow release/redeem-and-refund paths; they only implement it for the "excess/overpayment refund to msg.sender" case, where the caller controls their own address and thus their own risk.

### Impact Explanation
If the escrow-release/redemption beneficiary is a contract that reverts on receiving native ETH:
- The user's originally escrowed native-token input on the source chain becomes permanently un-redeemable (`_withdraw` for `RedeemEscrow` always reverts), freezing those funds in the `IntentsBase`/`IntentGatewayV2` contract indefinitely, since the ISMP request can never be successfully processed.
- The same applies to `EscrowRefunded` flows on cancellation, where `order.user` (chosen by the order creator at placement time but potentially manipulated via calldata-executing orders or compromised addresses) is the recipient.
- This is a permanent freezing of user/protocol funds — meeting the High severity bar described in the rules (concrete permanent freezing of funds).

### Likelihood Explanation
Reaching this requires only a single order fill or cancellation with native ETH as the input/output asset and a beneficiary/solver address that is a contract without a payable fallback — a cheap, fully permissionless, single-transaction setup available to any unprivileged solver or order-canceller. No governance, admin, or off-chain trust is required, matching the “unprivileged intent solver” reachability criterion.

### Recommendation
Apply the same defensive pattern already used in `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable`: attempt the native `.call`, and on failure fall back to crediting a WETH-equivalent ERC20 balance (or a pull-based withdrawal pattern) instead of reverting the entire settlement. Concretely:
1. In `IntentsBase._sendValue` (and the inline duplicates in `IntentGatewayV2.sol`, `IntrinsicIntents.sol`), replace the unconditional revert with a fallback: wrap the ETH into the configured WETH token and `safeTransfer` it to the beneficiary if the native push fails.
2. Alternatively, move to a pull-payment/escrow-credit model for native-token beneficiaries so a hostile recipient can only griefs itself, not block settlement for others.

### Proof of Concept
1. Attacker deploys `MaliciousReceiver` with no `receive()`/payable `fallback()`.
2. Attacker (as solver) calls `fillOrder`/`ExtrinsicIntents` cross-chain fill using `MaliciousReceiver` as `msg.sender` (e.g. via a proxy contract) for an order whose input asset is native ETH.
3. Fill succeeds on the destination chain, dispatching `RedeemEscrow` with `beneficiary = MaliciousReceiver`.
4. When the `RedeemEscrow` POST request is relayed to the source chain and `onAccept` invokes `_withdraw`, the `_sendValue(beneficiary, amount)` call at [6](#0-5)  reverts because `MaliciousReceiver` cannot accept ETH.
5. The message can never be processed successfully; the original user's escrowed native ETH input remains locked in the source-chain contract permanently.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L201-219)
```text
        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L95-100)
```text
            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
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
