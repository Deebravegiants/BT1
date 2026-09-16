### Title
Blacklisted token in a multi-token order permanently freezes ALL escrowed input funds during cancel/refund - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2` orders escrow an arbitrary array of input tokens (`order.inputs`) under a single order `commitment`. When an order is cancelled or refunded, `_withdraw()` iterates over every escrowed token and pushes it out with `IERC20(token).safeTransfer(beneficiary, amount)` in a single loop, with no isolation between tokens. If any one token in that array reverts the transfer (e.g. a USDC-style blacklist on the beneficiary), the whole loop — and therefore the whole refund/cancel transaction — reverts, permanently blocking withdrawal of every other (otherwise-transferable) token escrowed for that order.

### Finding Description
`_withdraw()` is the single chokepoint used by every refund/redeem path in the intents system: [1](#0-0) 

It loops through `body.tokens` and calls `safeTransfer` per token with no try/catch, so a single reverting token aborts the entire withdrawal for all tokens in the order.

This function is reached from three places, all satisfying the "unprivileged submitter" criterion:

1. **Same-chain cancel**, callable directly by the order's own user: [2](#0-1) 

2. **Cross-chain refund/redeem delivered by a relayer** via `onAccept`, which is the terminal handler for a Hyperbridge `PostRequest` — reachable by any relayer submitting a valid proof, not a privileged actor: [3](#0-2) 

3. **Cross-chain cancel-from-source GET response**, also delivered by an unprivileged relayer, which likewise calls `_withdraw`: [4](#0-3) 

A user can place a single order whose `inputs` array mixes a blacklist-capable token (USDC) with other tokens (ETH, DAI, etc.) — nothing in `placeOrder` restricts input token composition: [5](#0-4) 

If that user is later blacklisted by USDC (or the order commitment's beneficiary is blacklisted) and the order becomes cancellable/refundable, the resulting `_withdraw` call reverts on the USDC leg. Because there is no per-token withdrawal function and no partial/best-effort transfer logic, none of the other escrowed tokens for that commitment can ever be recovered either.

Unlike a simple "call it again later" situation, this is materially worse for the cross-chain paths: `RefundEscrow`/`RedeemEscrow` are single-delivery ISMP messages consumed via `onAccept`. If the module call reverts, the request delivery transaction reverts, and every retry by a relayer will hit the identical blacklist revert, since blacklist status does not change. There is no separate mechanism to skip the blacklisted token and still release the rest — the entire commitment's escrow (potentially including ETH and other freely-transferable assets) is permanently stuck.

The identical pattern exists in the Tron variant of the contract: [6](#0-5) 

### Impact Explanation
This causes concrete, permanent freezing of escrowed user funds: a single blacklisted token within a multi-token order locks all other tokens escrowed under that same order commitment, with no on-chain recovery path (no per-token withdrawal, no bypass, and cross-chain refund messages cannot be redelivered successfully). This satisfies "permanent freezing of funds" for an unprivileged, ordinary flow (a normal user placing and later cancelling/being refunded an order), qualifying as Medium severity.

### Likelihood Explanation
Likelihood is realistic: intent orders routinely bundle multiple input tokens (e.g., stablecoin + native ETH) since nothing restricts input composition, USDC/USDT-style blacklisting is common in production, and cancellation/refund is a standard, expected user/relayer-triggered flow (not requiring any special conditions beyond the order being cancellable and the user being blacklisted by one of the input tokens).

### Recommendation
- Make `_withdraw()` resilient per-token: wrap each token transfer in a try/catch (or use a pull-based "claimable" balance model) so a single failing/blacklisted token does not block release of the other tokens.
- Alternatively, provide a dedicated recovery function that allows withdrawing on a per-token basis for a given commitment, so a blacklisted token can be skipped or later swept to an alternate address while unaffected tokens are released immediately.

### Proof of Concept
1. User places an order with `inputs = [USDC: 100, ETH: 1, DAI: 100]` via `placeOrder` (`evm/src/apps/IntentGatewayV2.sol`), escrowing all three under one `commitment`.
2. User gets blacklisted by USDC's issuer (or their beneficiary address is blacklisted) at any point before cancellation.
3. Order becomes eligible for cancellation/refund (e.g., same-chain: user calls `cancelOrder` → `_cancelSameChain`; or cross-chain: relayer delivers `RefundEscrow` via `onAccept`).
4. `_withdraw()` iterates `body.tokens`: the USDC `safeTransfer(beneficiary, amount)` call reverts due to the blacklist.
5. The entire transaction reverts — ETH and DAI, which were fully transferable, remain permanently locked in escrow for that commitment, with no function available to withdraw them individually.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-367)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
}
```

**File:** evm/src/apps/IntentGatewayV2.sol (L228-256)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
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
