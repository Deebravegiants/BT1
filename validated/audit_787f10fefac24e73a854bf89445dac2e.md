This confirms the analog. `onAccept` at `IntentGatewayV2.sol` line 629-635 directly calls `withdraw(body, ...)` with no try/catch isolation, so both the `RedeemEscrow` (fill payout) and `RefundEscrow` (cancellation refund) paths are DoS'd by a single reverting token transfer inside `withdraw()`.### Title
`withdraw()` in `IntentGatewayV2` reverts entirely on a single non-standard/blocking output token, permanently freezing escrowed funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`ConvexSpell`'s DoS analog exists in `IntentGatewayV2.sol`'s `withdraw()` function, which is invoked by `onAccept()` for both `RedeemEscrow` (fill payout) and `RefundEscrow` (cancellation refund) message kinds without any failure isolation. A single reverting token transfer inside the loop reverts the whole ISMP `onAccept` call, exactly like `remove_liquidity_one_coin()` reverting kills `closePositionFarm()`.

### Finding Description
`onAccept` dispatches directly into `withdraw(body, isRefund)` for both escrow-release and refund message kinds: [1](#0-0) 

Inside `withdraw()`, each escrowed token is paid out to the beneficiary using a raw low-level `.call` to `IERC20.transfer`, and if that single call fails the entire function (and thus the enclosing `onAccept`) reverts with `TransferFailed`: [2](#0-1) 

The transaction-fee payout at the end of `withdraw()` has the identical unguarded pattern: [3](#0-2) 

Unlike the `HyperFungibleToken`/`WrappedHyperFungibleToken` apps, which isolate inbound delivery so a reverting recipient cannot brick the channel, and `HyperbridgeLzEndpoint.onAccept`, which explicitly wraps the external delivery call in `try/catch` specifically to prevent "a deterministic revert... does not revert `onAccept`" and stores the payload for later retry [4](#0-3) , `IntentGatewayV2.withdraw()` has no such isolation, no partial-success handling, and no retry/skip mechanism for a stuck order commitment.

If any one of the multiple `body.tokens[i]` in a `WithdrawalRequest` (e.g. an order with several output/input tokens) is a token that can permanently or temporarily block transfers to a given address — paused ERC20, blocklisted/frozen recipient (e.g. USDC/USDT-style compliance controls), a token that self-destructs its transfer path, or any ERC20 whose `transfer()` reverts under some external state — every future `onAccept` call carrying that `commitment` will revert. Because `_orders[commitment][token]` is never zeroed out on failure (the storage decrement only happens after a successful transfer), the escrowed funds for that commitment remain locked, and the RedeemEscrow/RefundEscrow message can never be successfully applied by any relayer, permanently freezing the escrowed assets for that intent, both the filler payout and the user's inputs.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable from a single submitted cross-chain intent order: any solver/filler or user picking (or being forced into) an order whose escrowed token list includes a token capable of reverting a transfer to the beneficiary address causes that order's `commitment` to be permanently un-redeemable and un-refundable. Both the filler's reward and the user's refund path are blocked simultaneously since both `RedeemEscrow` and `RefundEscrow` funnel through the same `withdraw()` function.

### Likelihood Explanation
Likelihood is Medium-High: `IntentGatewayV2` is generic infrastructure supporting arbitrary ERC20 tokens as `TokenInfo` inputs/outputs supplied by unprivileged order-placers/fillers, so it does not control which tokens are used. Any token with pausability, address freezing/blocklisting (common in stablecoins), or fee-on-transfer edge cases reverting on zero-value transfers to a blocked address is sufficient to trigger this; no attacker cooperation or privileged role is required beyond placing/filling an order that references such a token.

### Recommendation
Isolate each token transfer with try/catch (or a low-level call whose failure only skips that leg) so a single blocked token cannot revert the whole `withdraw()`/`onAccept()` call, similar to the pattern already used in `HyperbridgeLzEndpoint.onAccept` [4](#0-3) . On failure, retain the un-delivered leg's state (e.g. keep `_orders[commitment][token]` intact) and expose a permissionless retry/sweep path (mirroring `retryPayload`) so relayers or the beneficiary can re-attempt delivery once the blocking condition clears, rather than bricking the whole commitment.

### Proof of Concept
1. A user places a cross-chain order whose `inputs` (escrow) include a normal ERC20 `A` and a compliance-controlled stablecoin `B` capable of blocklisting addresses.
2. The order is filled by a solver, then Hyperbridge relays a `RedeemEscrow` message to the source chain calling `onAccept` → `withdraw(body, false)` [1](#0-0) .
3. Before delivery, the beneficiary/filler address is blocklisted on token `B` (or `B` is paused). `withdraw()`'s loop reaches `B`'s `token.call(...IERC20.transfer...)`, which returns `success == false`; the function reverts with `TransferFailed` [5](#0-4) .
4. Because the whole `onAccept` reverts, `_orders[commitment][A]` and `_orders[commitment][B]` are never decremented — token `A`, which was otherwise fully transferable, is now stuck alongside `B`.
5. No relayer can ever successfully deliver `RedeemEscrow` (or a later `RefundEscrow`) for this `commitment` since the same `withdraw()` path and the same blocked token are always hit, permanently freezing both `A` and `B` escrowed for this order.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L384-395)
```text
        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
        } catch {
            bytes32 payloadHash = keccak256(abi.encode(guid, message));
            _inboundPayloadHashes[receiverAddr][srcEid][sender][nonce] = payloadHash;
            emit InboundPayloadStored(receiverAddr, srcEid, sender, nonce, payloadHash);
        }
```
