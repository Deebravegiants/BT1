## Title
Intent settlement `_withdraw` reverts entirely on a single blacklist-enforcing/reverting token, permanently freezing escrow for the whole order — (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw` releases every escrowed token for an order commitment in a single loop using `SafeERC20.safeTransfer`, which reverts the entire function (and the whole settlement transaction) if *any one* token transfer fails. Because settlement is delivered exactly once per commitment via Hyperbridge's `onAccept`, a single misbehaving/blacklisting ERC-20 among an order's multiple input tokens permanently blocks release of *all* tokens in that order — the analog of the Derby `blacklistProtocol()` issue, where an action that must complete (fund release) is coupled to an external call on a component (a token contract) that can be made to always revert.

### Finding Description
`IntentsBase._withdraw` iterates over `body.tokens` and, for ERC-20s, calls `IERC20(token).safeTransfer(beneficiary, amount)`, which reverts on failure: [1](#0-0) 

This function is invoked directly (no try/catch, no per-token isolation) from `ExtrinsicIntents.onAccept` for both `RedeemEscrow` and `RefundEscrow` settlement kinds: [2](#0-1) 

and from `onGetResponse` for source-chain cancellation: [3](#0-2) 

Many real-world stablecoins (e.g. USDC/USDT) implement an issuer-controlled blacklist: `transfer`/`transferFrom` to a blacklisted address reverts unconditionally. If a solver-filled or cancelled order escrows such a token alongside other, unrelated tokens (a common pattern — `TokenInfo[] tokens` supports arbitrary multi-token orders), and the `beneficiary` (`order.user` for refunds, or the filling solver for redemption) is or later becomes blacklisted by that token's issuer, `safeTransfer` for that one token reverts, unwinding the *entire* `_withdraw` call — including the release of the other, perfectly healthy escrowed tokens and fees in the same order.

Crucially, this is not a one-off; every retry of the same settlement message hits the exact same revert, so the freeze is permanent for that commitment. Contrast this with how the core host already handles the equivalent problem for module delivery: `EvmHost.dispatchIncoming`/`dispatchTimeOut` isolate the external app call behind a low-level `.call` with an explicit success check specifically so a reverting callee cannot brick host-level state: [4](#0-3) 

`_withdraw`/`onAccept` in the intents module does not apply this same isolation pattern at the per-token level, so the blacklist-style revert propagates and blocks the whole multi-token settlement rather than being caught and left retryable/partial.

### Impact Explanation
Once a beneficiary is blacklisted by any single ERC-20 held in a multi-token order's escrow, every subsequent delivery attempt of that order's `RedeemEscrow`/`RefundEscrow`/cancel-GET-response reverts identically. This is a **permanent freeze of funds**: the unrelated, healthy tokens and the accrued relayer/tx fees escrowed in the same order can never be released, because `_withdraw` has no mechanism to skip or isolate a single failing token transfer. This is directly reachable by any unprivileged intent user/solver simply by placing or filling a cross-chain order whose input/output token set includes a blacklist-capable stablecoin — no privileged action or malicious admin is required, satisfying the "unprivileged intent solver" reachability requirement.

### Likelihood Explanation
Likelihood is realistic: USDC/USDT and other centrally-blacklistable stablecoins are common in intent-based bridging flows, and blacklisting of an arbitrary address by an issuer (due to sanctions, exploit-related freezes, etc.) is outside the protocol's control but fully foreseeable. Any multi-token order that happens to include such a token becomes permanently stuck the moment its beneficiary is blacklisted — no attacker action against Hyperbridge itself is even needed, only a downstream token-issuer action against the beneficiary address.

### Recommendation
Isolate per-token transfer failures in `_withdraw` (e.g., wrap each `safeTransfer`/native send in a low-level call, check success individually, and either skip failed transfers while completing the rest and recording a residual claim, or introduce a per-token retry/recovery path) so that one uncooperative token cannot block the release of the remaining escrowed assets and fees for the same order commitment.

### Proof of Concept
1. A user places a cross-chain `Order` with two input tokens: `USDC` (blacklist-capable) and `DAI`, escrowed via `IntentGatewayV2.placeOrder`.
2. A solver fills the order on the destination chain; Hyperbridge relays a `RedeemEscrow` settlement back to the source chain.
3. Before delivery, the solver's address is added to USDC's blacklist by the issuer (or the order is a refund case and `order.user` gets blacklisted).
4. `ExtrinsicIntents.onAccept` calls `_withdraw`, which loops over `[USDC, DAI]`; `IERC20(USDC).safeTransfer(beneficiary, amount)` reverts because the beneficiary is blacklisted.
5. The whole `_withdraw` call reverts, so the `DAI` transfer, the tx-fee transfer, and the `_filled` finalization never happen — even though `DAI` alone was fully redeemable.
6. Every future delivery of this exact settlement message reproduces the same revert, since neither `_orders[commitment][USDC]` nor `_orders[commitment][DAI]` nor `_filled[commitment]` is ever updated — the escrow for this order commitment is permanently frozen.

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

**File:** evm/src/core/EvmHost.sol (L794-817)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

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
