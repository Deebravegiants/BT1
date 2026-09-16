I have enough to determine the analog. This confirms the vulnerability class: `_withdraw()` in `IntentsBase.sol` performs unconditional `IERC20.safeTransfer(beneficiary, amount)` calls reachable from `onAccept()` (RedeemEscrow/RefundEscrow) and `onGetResponse()` (source-chain cancellation) in `ExtrinsicIntents.sol`, without any fallback for a blocklisted beneficiary. Although `EvmHost.dispatchIncoming` (evm/src/core/EvmHost.sol:794-818) swallows a reverting `onAccept` call so the batch/receipt isn't bricked, the underlying condition (beneficiary blocklisted by the token) does not change on retry — so escrowed funds for that beneficiary remain permanently unwithdrawable, which is a valid freezing-of-funds analog.

### Title
Blocklisting in escrowed ERC20 permanently freezes IntentGateway escrow via reverting `safeTransfer` in `_withdraw()` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw()` transfers escrowed ERC20 tokens to a `beneficiary` using `IERC20(token).safeTransfer(beneficiary, amount)` with no failure isolation. This function is reachable from `ExtrinsicIntents.onAccept()` (for `RedeemEscrow` and `RefundEscrow` requests) and `ExtrinsicIntents.onGetResponse()` (source-chain cancellation after a Hyperbridge GET proof). If the `beneficiary` — the solver on a fill, or `order.user` on a refund/cancel — is blocklisted by the escrowed ERC20 (e.g. USDC/USDT), every call to `_withdraw()` for that commitment reverts, and the escrowed tokens can never be released to that address, permanently freezing the user's or solver's funds in the gateway.

### Finding Description
`_withdraw()` iterates over `body.tokens` and unconditionally calls:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
``` [1](#0-0) 

and, when `finalize` is true, also forwards accumulated transaction fees the same way:
```solidity
IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
``` [2](#0-1) 

This is called from two unprivileged, message-triggered entry points:
- `onAccept()` on `RedeemEscrow`/`RefundEscrow`, authenticated only against the counterpart `IntentGateway` instance, not against the beneficiary's blocklist status: [3](#0-2) 
- `onGetResponse()`, which finalizes a source-chain cancellation refund to `order.user` once the destination-chain "unfilled" storage proof is verified: [4](#0-3) 

Because `token.safeTransfer` bubbles up any revert from the ERC20 (e.g. a blocklist check), a single blocklisted token, in a multi-token withdrawal, reverts the entire `_withdraw()` call — freezing *all* tokens in that order's escrow for that beneficiary, not just the blocklisted asset.

At the host layer, `EvmHost.dispatchIncoming()` does isolate a reverting `onAccept()`/`onGetResponse()` call so the delivery batch itself doesn't revert and the receipt is deleted for retry: [5](#0-4) 
This differs from the reNFT root cause (which reverted the whole caller transaction), but it does not fix the underlying freeze: since the blocklist condition on the beneficiary address persists, every retry of the same `RedeemEscrow`/`RefundEscrow`/GET-response delivery fails identically, and there is no alternate recovery path (no admin sweep, no "claim to a different address" mechanism) for the affected beneficiary's escrow. Contrast this with `HyperbridgeLzEndpoint.onAccept()`, which explicitly wraps the analogous external call in `try/catch` and retains the payload for `retryPayload/clear/skip/nilify/burn` recovery: [6](#0-5) 
`IntentsBase`/`ExtrinsicIntents` has no equivalent recovery mechanism for a stuck beneficiary.

### Impact Explanation
- **Cross-chain fill (RedeemEscrow):** if the filling solver's address becomes blocklisted by the escrowed token before the settlement message lands, the solver's earned escrow (the user's original input tokens) is permanently stuck in the source-chain `IntentGateway`. The user's assets that were meant to pay the solver are locked with no recipient able to claim them.
- **Cross-chain refund/cancel (RefundEscrow / GET-response cancel):** if `order.user` becomes blocklisted by the escrowed input token (whether through legitimate compliance action or self-inflicted before placing the order to grief resolution), the user can never recover their escrowed input tokens through either cancellation path (`_cancelFromSource` or `_cancelFromDest`), permanently freezing their own principal in the gateway with no alternate exit.
- Any solver attempting to fill an order whose token later blocklists them, or any user relying on cancellation after a token-level compliance freeze, suffers permanent, unrecoverable loss of the escrowed asset — a direct funds-freezing condition per the accepted impact classes.

### Likelihood Explanation
Blocklisting is a real, actively used feature of centralized stablecoins (USDC, USDT) commonly used as intent-gateway settlement/input tokens. A user or solver interacting with the IntentGateway has no way to predict or prevent being blocklisted mid-flight, and unlike the reNFT case, there is no admin-recovery mechanism at all in `IntentsBase`/`ExtrinsicIntents` for stuck escrow. The condition requires no attacker action beyond normal usage — only an externally-imposed blocklist event — making this a credible Medium-likelihood, high-impact freezing bug reachable from a single relayed cross-chain message.

### Recommendation
- Wrap the `safeTransfer` calls in `_withdraw()` in a try/catch (or use a non-reverting low-level `call` + explicit success handling per token) so that a blocklisted beneficiary does not block the release of other tokens in the same withdrawal, and does not prevent order finalization.
- On transfer failure to `beneficiary`, credit the amount to a claimable/pull-based balance (or emit an event) so the funds can later be swept to an alternate address the beneficiary controls, or recovered via governance, rather than being permanently unretrievable.
- Consider mirroring the `HyperbridgeLzEndpoint`'s `try/catch` + retained-payload pattern used for OApp delivery, so failed withdrawals remain retryable/recoverable instead of silently perpetually failing.

### Proof of Concept
1. Deploy `ExtrinsicIntents`/`IntentGatewayV2` on a source chain with a mock blocklist-capable ERC20 as the order's input token (mirroring the reNFT PoC's `MockERC20.setBlock`).
2. User places a cross-chain order, escrowing the blocklist-capable token as input; source and destination differ.
3. Before the destination fill completes, blocklist `order.user` in the input token contract (simulating regulatory/compliance freeze).
4. Have the order legitimately go unfilled past `order.deadline`; call `cancelOrder()` from the source chain, which dispatches the `DispatchGet` proof request and eventually triggers `onGetResponse()` → `_withdraw(body, true, true)`.
5. Observe `IERC20(token).safeTransfer(beneficiary, amount)` revert inside `_withdraw()` at `IntentsBase.sol:468`; `EvmHost.dispatchIncoming` swallows the revert and deletes the receipt, but the escrow remains locked under `_orders[commitment][token]` with no way for `order.user` (or anyone else) to ever claim it, since re-submitting the same GET response proof hits the identical revert every time.

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

**File:** evm/src/core/EvmHost.sol (L794-818)
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
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L383-390)
```text

        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
```
