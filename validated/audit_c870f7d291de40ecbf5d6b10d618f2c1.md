### Title
Permanent freezing of multi-token escrow if any single token transfer reverts during withdrawal - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.withdraw()` (Tron EVM app) releases every escrowed token for an order (plus fees) in a single loop inside one atomic call triggered by an incoming `RedeemEscrow`/`RefundEscrow` POST request. If any one token in that loop cannot be transferred to the beneficiary (e.g. the beneficiary is blacklisted for a stablecoin like USDC, or is a contract that reverts on receipt for one of the tokens), the whole `withdraw()` call reverts, blocking release of *all* the other escrowed tokens in that order as well.

### Finding Description
`withdraw()` iterates `body.tokens` and, for each token, does a low-level `.call` of `transfer`, reverting the entire function with `TransferFailed` if any single transfer fails: [1](#0-0) 

This function is invoked from `onAccept()`, reached only when Hyperbridge (via a relayer) delivers an authenticated `RedeemEscrow`/`RefundEscrow` POST request: [2](#0-1) 

Because `pallet-ismp`/`IsmpHost` does not persist receipts for failed `IsmpModule` callbacks, a reverting `onAccept` call can be retried indefinitely by relayers until the request times out — but if the failure condition (e.g. a USDC blacklist on the beneficiary) is permanent, the message can never succeed and the order's *entire* escrow (all tokens, not just the problematic one) remains stuck, exactly mirroring the underlying report's bug class: a single non-cooperative/blacklisted/reverting receiver blocking batch fund release that should otherwise be uncoupled per-asset.

The fee sweep at the end of `withdraw()` (transfer of `TRANSACTION_FEES` in `feeToken`) is similarly coupled into the same atomic call, so a stuck fee-token transfer also blocks release of the principal tokens, and vice versa: [3](#0-2) 

The same one-bad-receiver-blocks-all-outputs pattern also appears in the `SweepDust` handler, which loops over multiple token payouts to a single beneficiary and reverts the whole `onAccept` on the first failed transfer: [4](#0-3) 

### Impact Explanation
This is a High-severity availability/fund-freezing issue: a user's cross-chain intent order can escrow multiple distinct tokens (e.g. USDC + DAI + native). If the beneficiary address becomes blacklisted for just one of those tokens (or is a contract that reverts on one token's transfer), the relayer-delivered settlement message will perpetually revert on `onAccept`, permanently freezing *all* the escrowed assets for that order — not just the problematic token. Since `IsmpHost` allows unlimited retries of failed messages but the blacklist condition never resolves, the funds become permanently unrecoverable through the intended path once the timeout window (if any) also elapses without successful delivery.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: any order involving a common blacklistable stablecoin (USDC) as one of several escrowed inputs is exposed. No privileged access is required — a normal user simply needs to get blacklisted (or use/return to an address that later becomes blacklisted, e.g. via sanctions or fraud flags) between order placement and settlement, or an attacker could deliberately construct/target an order whose beneficiary is a maliciously reverting contract for one token to grief the settlement of the whole order.

### Recommendation
Decouple per-token transfers so a failure in one does not block the others:
- In `withdraw()`, don't revert the whole call on a single token transfer failure; instead, track failed transfers and let the beneficiary (or a permissionless sweep function) pull/retry them individually, or credit a per-beneficiary/per-token claimable balance on failure instead of reverting.
- Apply the same isolation to `SweepDust` — one bad token/beneficiary pair should not prevent sweeping the rest.
- Consider explicitly detecting non-fatal transfer failures (e.g., using `try/catch` around low-level calls, already partially done via `(bool success,)`) and instead of reverting, escrow the failed amount for later manual/permissionless withdrawal by the beneficiary via an alternate address.

### Proof of Concept
1. User places a cross-chain order via `IntentGatewayV2` with `order.inputs = [USDC, DAI]`, escrowing both tokens on the source chain.
2. Before settlement/refund is delivered, the user's designated beneficiary address gets blacklisted by USDC (Coinbase/Circle freeze).
3. A relayer delivers the `RedeemEscrow`/`RefundEscrow` POST request; `onAccept` → `withdraw()` iterates `body.tokens`, hits the USDC leg first, `token.call(transfer(...))` returns `success = false` due to the blacklist, and the function reverts with `TransferFailed`.
4. Because the transaction reverted, the DAI leg (and any fee-token payout) that would have succeeded is never processed either — the whole order remains permanently stuck since `IsmpHost` will keep allowing retries of the same failing message, which will keep reverting for as long as the blacklist persists.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-720)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
```
