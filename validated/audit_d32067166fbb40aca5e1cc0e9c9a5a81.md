Confirmed: `EvmHost.dispatchIncoming` (evm/src/core/EvmHost.sol:794-818) uses a low-level `.call` and on failure deletes `_requestReceipts[commitment]` so the request "can be retried" — the delivery is not abandoned, it stays retryable forever by any relayer. This is the mechanism that turns a per-token blacklist revert into a *permanent* freeze rather than a one-off failure.

### Title
Permanent freezing of entire multi-token escrow when a withdrawal beneficiary is blacklisted on any single token - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._withdraw` releases every escrowed token for an order to a single `beneficiary` in one loop using un-caught `IERC20.safeTransfer`. If the beneficiary is blacklisted (e.g. USDC/USDT) for just one of the tokens in the withdrawal, the whole call reverts, and because the ISMP delivery path treats callback failure as "retry later" rather than "fail permanently," the entire escrow — including tokens the beneficiary could otherwise receive — becomes permanently stuck.

### Finding Description
`_withdraw` iterates over `body.tokens` and calls `IERC20(token).safeTransfer(beneficiary, amount)` for each token without try/catch, decrementing `_orders[commitment][token]` before the transfer: [1](#0-0) 

This function is the settlement path for both cross-chain fills and refunds. It is invoked from `ExtrinsicIntents.onAccept` for `RedeemEscrow`/`RefundEscrow` requests, and from `onGetResponse` for source-side cancellations: [2](#0-1) [3](#0-2) 

`onAccept` is called by `EvmHost.dispatchIncoming` via a raw `.call`. On failure, the host does **not** revert the whole batch nor permanently drop the message — it deletes the request receipt "so that it can be retried": [4](#0-3) 

Because a token blacklist status does not change between retries, any relayer resubmitting the same proof will hit the exact same revert indefinitely. Solidity's atomic revert semantics mean a failure on token[i] rolls back the successful transfers of token[0..i-1] too, so tokens the beneficiary *could* legitimately receive are locked along with the blacklisted one, with no way to selectively re-deliver only the receivable tokens (`WithdrawalRequest.tokens` is fixed by the original dispatch and cannot be redispatched with a subset).

This is the direct analog of the referenced report: a single unprivileged actor (the order's designated beneficiary — either the order creator via `order.user`/`_cancelFromDest`/`_cancelSameChain`, or the filling solver via `_fillCrossChain`'s `RedeemEscrow` beneficiary) can get themselves blacklisted on one token in a multi-token order to force a forever-undeliverable settlement message, freezing the whole basket of escrowed assets rather than losing only the blacklisted token.

### Impact Explanation
Escrowed funds for the affected order commitment become permanently unrecoverable: no retry ever succeeds, there is no partial-release or force-refund-to-alternate-address fallback, and no governance/admin path in `IntentsBase`/`ExtrinsicIntents` allows re-targeting or splitting a stuck `WithdrawalRequest`. This satisfies "permanent freezing of funds" and, since the message can never be successfully delivered, also "a route unable to deliver messages" per the validation criteria. Multi-token orders (input escrow with several distinct tokens, or the fee-token top-up combined with token release in the `finalize` branch) are the most exposed, since a single blacklisted token blocks the whole set, including the protocol fee-token transfer: [5](#0-4) 

### Likelihood Explanation
Getting an address blacklisted on USDC/USDT is a known, low-cost, self-inflicted action (as demonstrated in the referenced report), and any order beneficiary/user is free to choose or later cause their own address to be sanctioned. Multi-token orders are a normal, expected usage pattern (the `TokenInfo[]` shape supports arbitrary numbers of input/output tokens), so no unusual configuration is required to hit this path — a single order with two input tokens where one is a blacklist-capable stablecoin is sufficient.

### Recommendation
In `_withdraw`, wrap each per-token transfer in a try/catch (or use a low-level `call` with success check) so that a failure on one token does not roll back transfers already made or block redelivery of the remaining tokens; track per-token delivery status (e.g., leave `_orders[commitment][token]` un-decremented only for the failed token) so a follow-up call can retry just the stuck token, or expose a permissionless "sweep to alternate address" recovery path for tokens that fail repeatedly, analogous to fixing `_liquidate` in the original report by isolating per-asset failures instead of an all-or-nothing loop.

### Proof of Concept
1. Attacker places a same-chain (or cross-chain) order with two input tokens: `USDC` and `DAI`, both escrowed via `placeOrder`.
2. A solver fills the order via `fillOrder` → `_fillSameChain`/`_fillCrossChain`; the resulting `WithdrawalRequest.beneficiary` is the solver's own address for `RedeemEscrow` (source-chain release), or the order's user address for `RefundEscrow`/cancellation.
3. Attacker (as the eventual beneficiary, e.g., orchestrating the fill through a controlled solver address or being the order's own `user`) gets that beneficiary address blacklisted on `USDC` by Circle.
4. When `_withdraw` executes (via `onAccept`/`onGetResponse`), the `DAI` transfer that should succeed is attempted after — or the `USDC` transfer reverts first — either way `IERC20(USDC).safeTransfer(beneficiary, amount)` reverts, unwinding the whole call.
5. `EvmHost.dispatchIncoming` catches the failure and deletes `_requestReceipts[commitment]`, marking the message retryable.
6. Every subsequent relayer retry replays the same revert since the blacklist persists — both the `USDC` and the otherwise-receivable `DAI` escrow are permanently stuck in the `IntentGateway` contract with no recovery path.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-477)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
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

**File:** evm/src/core/EvmHost.sol (L805-818)
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
    }
```
