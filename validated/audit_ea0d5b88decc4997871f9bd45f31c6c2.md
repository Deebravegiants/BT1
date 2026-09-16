### Title
Escrow release to blacklisted/non-receiving beneficiary permanently freezes user funds in `IntentsBase._withdraw` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw`, invoked from `ExtrinsicIntents.onAccept` when a cross-chain `RedeemEscrow` or `RefundEscrow` message is delivered, unconditionally `safeTransfer`s escrowed input tokens to a fixed `beneficiary` address that is baked into the cross-chain message body dispatched from the *other* chain. If that ERC20 (e.g. a USDC-style token with a blacklist) refuses the transfer to that beneficiary, the whole `_withdraw` call reverts, `EvmHost.dispatchIncoming` deletes the request receipt "so it can be retried," and the message is retried with the exact same immutable beneficiary — so it fails forever, permanently freezing the user's escrowed funds with no recovery path.

### Finding Description
`ExtrinsicIntents.onAccept` decodes `RequestKind.RedeemEscrow`/`RefundEscrow` and calls `_withdraw` with a `beneficiary` decoded straight from the incoming ISMP POST body: [1](#0-0) 

`_withdraw` then loops the escrowed tokens and does a direct, unconditional `safeTransfer(beneficiary, amount)` for each one, with no fallback, no pull-based claim, and no way to change the beneficiary: [2](#0-1) 

The `beneficiary` for `RedeemEscrow` is the filler/solver address that filled the order on the destination chain (embedded into the dispatched body at fill time), and for `RefundEscrow` it is `order.user` (embedded when the destination-side cancellation is dispatched). Once this cross-chain message is dispatched, its body — including the beneficiary — is immutable; it cannot be re-encoded with a different address.

Delivery goes through `EvmHost.dispatchIncoming`, which performs a low-level `call` into `onAccept` and, on failure, deletes the request receipt "so it can be retried": [3](#0-2) 

This retry mechanism only helps for *transient* failures (e.g. out-of-gas, temporary paused state). It does not help here because the underlying cause — the `beneficiary` address being blacklisted by the specific escrowed ERC20 — is permanent and baked into the message. Every relayer retry replays the identical `onAccept` call with the identical `beneficiary`, so `safeTransfer` reverts identically every time, forever.

This is the same bug class as the referenced Cooler report: a hardcoded, non-configurable recipient for an ERC20 transfer that can permanently revert (blacklist), with no alternate withdrawal or claim path, causing the underlying escrowed collateral to be locked forever. Here the reachable trigger is not a privileged/malicious lender changing state, but the natural, permissionless flow of order fulfillment across Hyperbridge: any user placing a cross-chain intent order whose input token is later filled/redeemed to (or refunded to) an address that gets blacklisted by that token.

### Impact Explanation
Because `_withdraw` reverts entirely (not partially) when any single token transfer in `body.tokens` fails, **all** escrowed input tokens for that commitment — not just the blacklisted asset — become permanently unreachable:
- `RedeemEscrow` case: the user's escrowed input tokens can never be released to the filler if the filler's (or their chosen receiving) address is/becomes blacklisted by that specific ERC20 (e.g. USDC), even though the filler legitimately delivered the output assets on the destination chain. The filler loses their fulfillment and the user's original escrow is stuck.
- `RefundEscrow` case: if `order.user`'s address is/becomes blacklisted by the escrowed token between order placement and cancellation, the user's own escrow can never be refunded.

Since there is no way to re-dispatch the withdrawal request with a substitute beneficiary, and no owner/governance override to force-release with an alternate recipient, the escrowed value is permanently frozen — a concrete, unbounded loss of user funds reachable from ordinary, permissionless intent-fill/cancel flows.

### Likelihood Explanation
Likelihood is realistic wherever intents are settled in tokens with blacklist/pause functionality (USDC, USDT, and similar centrally-controlled stablecoins are explicitly supported use cases for cross-chain intents). A filler's receiving address, or an order's own `user` address, can become blacklisted at any point between order placement and settlement for reasons entirely outside the protocol's control (regulatory action, compliance freeze, prior unrelated flags on that address). No attacker action is even required — though a malicious filler could also deliberately supply a beneficiary they know will later be blacklisted, or a beneficiary belonging to a contract designed to revert, achieving the same permanent freeze deterministically.

### Recommendation
Do not push funds to a hardcoded on-chain beneficiary that cannot be changed after the cross-chain message is dispatched. Instead:
- Credit an internal, pull-based balance (mapping from beneficiary → token → amount) in `_withdraw` instead of calling `safeTransfer` directly, and expose a separate `claim()` function the beneficiary (or anyone on their behalf, to any address they specify) can call later. This way a blacklisted address can still direct funds elsewhere, or use a proxy/multisig without needing to re-run the cross-chain flow.
- Alternatively, wrap each `safeTransfer` in a try/catch (or low-level call) per-token so a single failing transfer doesn't revert the whole withdrawal and lock the other escrowed assets, and fall back to crediting that specific token to a claimable balance on failure.

### Proof of Concept
1. User places a cross-chain intent order (`ExtrinsicIntents`/`IntentGatewayV2`) escrowing USDC as `order.inputs` on the source chain, destined for some `order.destination` chain.
2. A filler fills the order on the destination chain and dispatches a `RedeemEscrow` `WithdrawalRequest` back to the source chain with `beneficiary = filler` (see `evm/src/apps/intentsv2/ExtrinsicIntents.sol` fill logic that emits this body, e.g. lines 181-220).
3. Before the message is delivered on the source chain, Circle blacklists the filler's address on USDC (or the filler intentionally supplies an address it knows will be/become blacklisted).
4. A relayer delivers the message via `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `ExtrinsicIntents.onAccept` → `IntentsBase._withdraw`. `IERC20(usdc).safeTransfer(beneficiary, amount)` reverts because `beneficiary` is blacklisted.
5. `EvmHost.dispatchIncoming` catches the failed low-level call and deletes the request receipt "so it can be retried" (`evm/src/core/EvmHost.sol` lines 809-816).
6. Any subsequent relayer retry replays the exact same immutable message body (same `beneficiary`), and `safeTransfer` reverts identically every time — the user's escrowed USDC is permanently stuck in the contract with no way to redirect it to a non-blacklisted address.

### Citations

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
