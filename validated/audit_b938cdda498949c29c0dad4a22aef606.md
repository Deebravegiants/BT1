## Title
Single Failing Token Transfer in `_withdraw` Blocks Escrow Release/Refund for All Tokens in an Order - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
The `_withdraw` function in `IntentsBase.sol`, which is the sole path for releasing escrowed order inputs to a solver (`RedeemEscrow`) or refunding them to a user (`RefundEscrow`/cancellation), loops over every token in `body.tokens` and calls `safeTransfer` for each one in sequence. Because the transfers are inside a single loop with no isolation, a transfer failure for any one token (e.g. a blacklisting stablecoin, a paused token, or a token contract that reverts for a specific recipient) reverts the entire function, permanently blocking release of every other, otherwise-transferable token escrowed for that same order commitment. This mirrors the reported `claimRemovedTokens` bug class: an "all-or-nothing" loop over independent token payouts where one bad token DOSes the rest.

### Finding Description
`_withdraw` is called from `onAccept()` (cross-chain settlement/refund) and `onGetResponse()` (source-chain cancellation), as well as from same-chain partial/full fills: [1](#0-0) 

```solidity
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
    ...
```

`_withdraw` is invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` kinds: [2](#0-1) 

and from `onGetResponse` for source-chain cancellation. The equivalent Tron contract has the identical pattern in `withdraw()`: [3](#0-2) 

If a single token in `body.tokens` cannot be transferred (e.g. the beneficiary is blacklisted on that specific ERC-20, the token is paused, or otherwise reverts), the `safeTransfer` call reverts, unwinding the whole `_withdraw` transaction — including the state updates for all other tokens in the same withdrawal, and the `_filled[commitment] = beneficiary` finalize marker. Since `EvmHost.dispatchIncoming` catches the `onAccept` revert and deletes the request receipt so the message "can be retried" (see `evm/src/core/EvmHost.sol:809-816`), the same delivery will simply be retried and fail again for the same reason — the transaction is not partially processed and cannot make progress past the bad token, indefinitely freezing all inputs of that order (not just the offending token).

### Impact Explanation
Multi-token orders escrow several distinct input tokens under a single commitment. If any one of them cannot be transferred to the beneficiary — a realistic scenario for compliance-gated stablecoins (USDC/USDT blacklisting a beneficiary address), a token that becomes paused, or a token with transfer hooks that revert under certain conditions — the entire order's escrow (all input tokens, plus accumulated transaction fees) becomes permanently stuck. Both the solver (on a legitimate fill via `RedeemEscrow`) and the user (on a cancellation/refund via `RefundEscrow`) lose access to funds that are otherwise fully redeemable. This is a concrete, permanent freezing-of-funds condition reachable by any relayer delivering a normal settlement/refund message, or by any user placing a multi-token order where one input becomes non-transferable to the counterparty.

### Likelihood Explanation
Likelihood is Medium: it requires one of the escrowed/output tokens in a multi-token order to become non-transferable to the specific beneficiary (blacklist, pause, or hook-based revert) at settlement time — a realistic but not universal condition for popular tokens like USDC/USDT. It does not require any privileged actor; a single order with an affected token and any relayer delivering the corresponding ISMP message is sufficient to trigger it, and once triggered, retries do not resolve it.

### Recommendation
Decouple per-token transfer success from the overall withdrawal bookkeeping in `_withdraw` (and the mirrored `withdraw` in `evm/tron/contracts/apps/IntentGatewayV2.sol`):
- Wrap each token transfer in a try/catch (or low-level call check) so a failing transfer for one token does not revert the loop.
- For tokens that fail to transfer, keep their escrow balance intact (do not decrement `_orders`) and expose a separate recovery/claim function that lets the beneficiary retry that specific token later, rather than gating all tokens in the order on the least reliable one.
- Ensure `_filled`/finalize state updates and fee release still occur for the successfully transferred tokens so the rest of the order settles.

### Proof of Concept
1. User creates a cross-chain order escrowing `tokenA` (a normal ERC-20) and `tokenB` (e.g. a USDC-like token) as inputs.
2. Solver fills the order on the destination chain; the source chain later receives a `RedeemEscrow` message via `onAccept`.
3. Between order creation and settlement, the solver's beneficiary address becomes blacklisted on `tokenB` (or `tokenB` is paused).
4. `onAccept` → `_withdraw` iterates: `tokenA.safeTransfer` may succeed, but `tokenB.safeTransfer` reverts due to the blacklist, reverting the whole `_withdraw` call and thus the whole `onAccept` execution.
5. `EvmHost.dispatchIncoming` catches the failure and deletes the receipt "so it can be retried" — but every retry hits the same revert on `tokenB`, so `tokenA` (and any accrued fees) also remain stuck in escrow indefinitely, even though `tokenA`'s transfer alone would have succeeded.

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
