### Title
Zero-value token transfer in `IntentGatewayV2.withdraw()` can permanently freeze escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.withdraw()` unconditionally calls `token.transfer(beneficiary, amount)` for every entry in `body.tokens`, with no check that `amount != 0` before making the external call, unlike the sibling implementation in `evm/src/apps/intentsv2/IntentsBase.sol`, which explicitly skips zero-amount legs (`if (amount == 0) continue;`).

### Finding Description
`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` iterates over `body.tokens` and, for every ERC20 entry, performs a raw low-level call to `transfer`: [1](#0-0) 

There is no `if (amount == 0) continue;` guard before this call — the guard exists in the parallel non-Tron implementation (`IntentsBase._withdraw`): [2](#0-1) 

`withdraw()` is reachable from multiple unprivileged, cross-chain-triggered entry points that this contract must process to release escrow: `onAccept()` for `RedeemEscrow`/`RefundEscrow` messages delivered by any relayer after a fill/cancel on the paired chain, `cancelOrder()` for same-chain refunds, and `onGetResponse()` for cross-chain cancellation from the source chain: [3](#0-2) [4](#0-3) 

If an order's `tokens` array (built from `order.inputs`) contains an entry whose amount is 0 for a token that reverts on zero-value transfers (the classic LEND-style ERC20 behavior cited in the source report), the `token.call(...)` succeeds at the call level but the callee reverts, `success` is `false`, and `withdraw()` reverts with `TransferFailed()`. Since `withdraw()` processes **all** tokens in the request in a single loop before emitting `EscrowReleased`/`EscrowRefunded`, one non-zero-value-transfer-hostile token with a zero amount blocks release of every other (non-zero) escrowed token in the same commitment as well, because the whole transaction reverts atomically.

### Impact Explanation
This is a fund-freezing bug: escrow that should be redeemable by a solver (fill) or refundable to the user (cancel/timeout) becomes permanently stuck because the message that would release it (`RedeemEscrow`/`RefundEscrow` via ISMP, or a same-chain `cancelOrder`) can never execute successfully — every relayer attempt to deliver the settlement message replays the same revert. Unlike a normal ISMP timeout/retry mechanism, there is no code path here that removes or reorders the offending zero-amount entry, so the freeze is permanent for that order's escrow. This matches the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Reaching a zero-amount input in `body.tokens` requires either: (a) the order legitimately declaring a `TokenInfo` with `amount == 0` for one of its inputs (the Tron `placeOrder` path enforces `order.inputs[i].amount == 0` reverts only in the non-predispatch direct-transfer branch, but the `withdraw`-consumed `tokens` array is reconstructed independently in `cancelOrder`/`onAccept` from `order.inputs`, which a solver/relayer/user fully controls when constructing the message body off-chain before it's authenticated) or (b) protocol-fee rounding driving the escrowed (reduced) amount for one input token to zero while still exceeding zero requirements elsewhere. Because `order.inputs` (and thus `WithdrawalRequest.tokens`) is attacker-influenced input passed into `onAccept`/`cancelOrder`, and the token itself only needs to be a widely-known zero-transfer-reverting ERC20 (e.g., old LEND) to be deployed as one of the order's input assets, this is reachable by a single unprivileged order placement plus a normal fill/cancel — no privileged actor required.

### Recommendation
Add a zero-amount skip inside the Tron `withdraw()` token loop, mirroring `IntentsBase._withdraw`:
```solidity
uint256 amount = body.tokens[i].amount;
if (amount == 0) {
    unchecked { ++i; }
    continue;
}
```
placed before the `_orders[...] == 0` check and the transfer call, so a zero-amount leg neither reverts nor blocks release of the other escrowed tokens.

### Proof of Concept
1. User calls `placeOrder()` on the Tron `IntentGatewayV2` with `order.inputs` containing two entries: `[USDC: 100, LEND-like-token: 0]` (or a `protocolFeeBps` configuration that rounds one reduced input to 0).
2. A solver fills the order (or the user cancels after expiry), causing a `WithdrawalRequest` to be constructed with `tokens = order.inputs`, including the `amount = 0` LEND-like entry, and dispatched/delivered via ISMP or invoked directly through `cancelOrder`/`onAccept`.
3. `withdraw()` iterates `body.tokens`; when it reaches the zero-amount LEND-like token, it calls `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, 0))`.
4. The LEND-like token's `transfer()` implementation reverts on `_value == 0`, so `success == false`, and `withdraw()` reverts with `TransferFailed()`.
5. Every subsequent relayer/user attempt to redeem or refund this commitment hits the same revert — the 100 USDC (and any other legitimately escrowed assets under the same commitment) can never be released, permanently freezing the funds.

Note: I could not fully trace where `WithdrawalRequest.tokens` for cross-chain fills (`fillOrder`) is populated in this Tron file within the available context (the `fillOrder`/`_fillCrossChain` equivalent text was not retrievable in the indexed portions I searched), so I based the input-controllability claim on the `cancelOrder`/`onAccept` code paths that were directly confirmed, plus the analogous `_fillCrossChain` in the non-Tron `ExtrinsicIntents.sol`, which builds the withdrawal body directly from `order.inputs`. If a Devin session has full file access, it should confirm the Tron `fillOrder` construction of `WithdrawalRequest.tokens` to close this gap.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L696-714)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-470)
```text
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
