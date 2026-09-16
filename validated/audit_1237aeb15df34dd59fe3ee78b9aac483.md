### Title
Attacker-controlled beneficiary can permanently block escrow release/refund via reverting native-token transfer - (File: evm/src/apps/intentsv2/IntentsBase.sol / evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Intent Gateway's cross-chain escrow settlement path pays out native-token (ETH) escrow directly to a `beneficiary` address using a low-level `.call{value:}` that reverts the entire transaction if the transfer fails. Because the `beneficiary` is an arbitrary, attacker-supplied address embedded in the order (the `user`, the filling solver, or any address chosen at fill time), an attacker can make this call always fail by deploying a contract whose `receive()`/`fallback()` reverts, permanently blocking settlement of that order — analogous to the reported `fulfillQuery` refund-blocking bug.

### Finding Description
`IntentsBase._sendValue` performs a raw native transfer and reverts the whole call if it is not accepted: [1](#0-0) 

It is invoked from `_withdraw`, which releases escrowed native tokens to `beneficiary` (`address(uint160(uint256(body.beneficiary)))`, derived from attacker-controlled order/withdrawal data) with no fallback path if the transfer fails: [2](#0-1) 

`_withdraw` is reached from `onAccept` when Hyperbridge delivers a `RedeemEscrow` or `RefundEscrow` POST request relayed cross-chain: [3](#0-2) 

The parallel non-EVM-standard implementation (`evm/tron/contracts/apps/IntentGatewayV2.sol`) has the identical unconditional-revert pattern in its `withdraw()` function used for both fill settlement and GET-response-based refunds: [4](#0-3) [5](#0-4) 

Because `onAccept`/`onGetResponse` is called directly by the host as part of processing the relayed message (not wrapped in a try/catch that isolates failure to just the payout), a beneficiary contract that reverts on receiving ETH causes the entire request-handling transaction to revert. If the request has no timeout (many of the intents flows use `timeout: 0`, as seen in the cross-chain dispatch construction), the message can never be delivered/processed successfully, and the escrowed input tokens (and any accrued fees) are permanently stuck, since `_orders[commitment][token]` is never decremented and `_filled[commitment]` never gets set.

This mirrors the reported bug class exactly: an attacker pre-deploys a contract capable of toggling whether it accepts ETH, arranges to be the beneficiary of a native-token payout (either as the order's own `user` on a cancellation/refund, or as the `beneficiary` on the destination-chain output, whose fill later triggers a `RedeemEscrow` payout back to the filler/solver on the source chain), then flips the contract to reject ETH once the payout attempt is imminent, causing the relayer's delivery transaction to permanently fail.

### Impact Explanation
A malicious order creator or beneficiary can indefinitely block resolution of their own order's escrow, preventing solvers/relayers from ever completing settlement and preventing the honest counterparty (solver on `RedeemEscrow`, or user on `RefundEscrow`/cancellation) from ever recovering funds. Since Hyperbridge requests with `timeout: 0` never expire and there's no alternate payout mechanism (e.g. pull-based withdrawal), this results in permanent freezing of escrowed native-token funds and fees, and a route that cannot deliver its message payload (the relayed request keeps failing on `onAccept`). This satisfies the "permanent freezing of funds" / "route unable to deliver messages" acceptance criteria.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to control the `beneficiary` address of a native-token order leg (straightforward, since `beneficiary`/`user` fields are attacker-chosen input to `placeOrder`/`fillOrder`), and to have native-token (ETH) as one of the settled assets (input or output) rather than only ERC-20, which is a common configuration since the gateway explicitly supports native-token inputs/outputs. No special privileges or timing race beyond normal transaction ordering are needed — the same "toggle receive() to revert" trick from the reported analog applies directly.

### Recommendation
Do not let a failed native-token push permanently revert escrow settlement. Options:
- Wrap native token as WETH and transfer the ERC-20 representation when the raw ETH push fails (mirroring the pattern already used in `WrappedHyperFungibleToken.onAccept`/`onPostRequestTimeout`, which retries with `IWETH.deposit`+`safeTransfer` on failure): [6](#0-5) 
- Alternatively, implement a pull-payment pattern: on transfer failure, credit the beneficiary's balance in an internal ledger they can withdraw later instead of reverting the whole settlement.
- Apply the same fix to both `IntentsBase._sendValue`/`_withdraw` (evm/src/apps/intentsv2) and the Tron `IntentGatewayV2.withdraw`/`onGetResponse` paths.

### Proof of Concept
1. Attacker deploys `MaliciousBeneficiary` with a `receive()` function that reads a mutable `bool reject` flag: reverts if `true`, succeeds if `false` (mirrors the reentrancy-test malicious contract pattern already present in the repo's test suite, e.g. `ReentrantBeneficiary` in `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`).
2. Attacker sets `reject = false`, places a cross-chain order (`placeOrder`) with `order.output.assets` including a native-ETH output and `beneficiary = address(MaliciousBeneficiary)`, or as `order.user` for a self-cancel/refund flow.
3. A solver fills the order on the destination chain (`ExtrinsicIntents._fillCrossChain`), which dispatches a `RedeemEscrow` POST request back to source chain with `timeout: 0`.
4. Before the relayer submits the delivery proof on the source chain, attacker sets `reject = true`.
5. Relayer calls the host's request-handling entrypoint, which invokes `IntentGatewayV2.onAccept` → `_withdraw` → `_sendValue(beneficiary, amount)`; the low-level call reverts, `_sendValue` reverts with `InsufficientNativeToken`, and the whole delivery transaction reverts.
6. Since the request never times out (`timeout: 0`) and there's no alternate settlement path, the escrowed input funds on the source chain and the solver's already-delivered output on the destination chain remain permanently unreconciled — the solver can never redeem escrow, and if used for `RefundEscrow`, the user's own funds remain stuck.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
