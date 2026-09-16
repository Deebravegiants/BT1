### Title
Intents Gateway `SweepDust` transfers governance-specified amounts with no on-chain check against outstanding user/solver escrow, permanently freezing/stealing escrowed order funds - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._sweepDust()` (and its equivalents in `evm/src/apps/IntentGatewayV2.sol`, `evm/tron/contracts/apps/IntentGatewayV2.sol`) blindly transfers an arbitrary `amount` of any token out of the gateway's balance to a beneficiary, with no on-chain accounting that verifies the swept amount is actually "dust" (protocol fee surplus) rather than tokens that are still escrowed against open orders in `_orders[commitment][token]`. This is structurally the same root cause as the `MuteAmplifier.rescueTokens()` finding: a token-rescue/sweep function that fails to subtract funds still owed to other parties (there: stakers' `totalRewards`/`totalReclaimed`; here: solvers'/users' escrowed order balances) before allowing a withdrawal from the contract's raw token balance.

### Finding Description
`placeOrder()` computes a protocol fee and only emits a `DustCollected` event — it never increments any on-chain running total of collected dust: [1](#0-0) 

The reduced (post-fee) amount is the only value credited to escrow accounting: [2](#0-1) 

When governance later sweeps accumulated dust, `_sweepDust`/`sweepDust` simply transfers the caller-specified `amount` for each token straight out of the contract's balance, with zero on-chain validation that this amount does not exceed `balanceOf(gateway) - Σ(open order escrow for that token)`: [3](#0-2) [4](#0-3) 

Because "dust" is tracked purely off-chain (via emitted `DustCollected` events aggregated by an indexer), the amount passed into `SweepDust` is only as accurate as an off-chain snapshot. Any unprivileged actor's normal, permissionless action — placing a new order (`placeOrder`), which escrows tokens into the same contract balance the sweep draws from, or a solver filling/settling an order that changes escrow composition between the indexer's snapshot and the sweep's on-chain execution — can cause the swept amount to overlap with funds that are still legitimately escrowed for an open order. The `_orders[commitment][token]` accounting is never checked or decremented by `_sweepDust`, so nothing on-chain prevents this overlap.

When the affected order is later redeemed or refunded, `_withdraw()`/`withdraw()` will attempt to pay out from `_orders[commitment][token]` even though the physical tokens backing that escrow were already swept to the treasury: [5](#0-4) 

This reverts (insufficient token balance) or, worse, drains other users' escrow to cover the shortfall, exactly mirroring the two-fold impact described in the original report: rewards/escrow become undeliverable ("reward system broken") and/or funds get permanently locked/misappropriated inside the contract.

### Impact Explanation
- Permanent freezing of funds: an intent placer's/solver's escrowed tokens can become unavailable for legitimate redemption or refund once dust has been over-swept, since `_orders[...]` still shows a balance that the contract no longer physically holds.
- Route unable to deliver messages / settle: `withdraw()`/`_withdraw()` calls dispatched via `onAccept` (`RedeemEscrow`/`RefundEscrow`) can revert for lack of contract balance, breaking the intent-fill/cancel-refund flow for any user whose escrow overlapped with the swept "dust."
- This does not require a malicious governance actor — it is a straightforward accounting gap reachable in the normal flow of order placement (unprivileged) interleaved with a routine, correctly-intentioned governance sweep.

### Likelihood Explanation
Medium: it requires the swept `amount` (computed off-chain from indexed `DustCollected` events) to be stale relative to on-chain state at execution time — plausible any time new orders are placed, filled, or cancelled between the off-chain dust computation and the governance-dispatched `SweepDust` message being delivered (which itself takes multiple blocks/ISMP round-trips to land). No special privilege is needed by the party whose action (placing/filling an order) creates the overlap; only the eventual sweep is governance-triggered, and the vulnerability is purely a missing on-chain invariant rather than governance intent.

### Recommendation
Track collected protocol dust on-chain per token (e.g., a `mapping(address => uint256) private _dust` incremented wherever `DustCollected` is emitted), and have `_sweepDust` require `amount <= _dust[token]`, decrementing it on sweep — analogous to the recommended fix of checking `totalRewards`/`totalReclaimed` before allowing `rescueTokens()` to move `muteToken`. This guarantees the swept amount can never overlap with tokens still escrowed against `_orders[commitment][token]`.

### Proof of Concept
1. User A places an order for 1,000 USDC with a 1% protocol fee; 990 USDC is credited to `_orders[commitment][USDC]`, 10 USDC sits in the gateway as "dust" (`DustCollected(USDC, 10)` emitted, no on-chain tally).
2. Before the accumulated-dust total is refreshed off-chain, User B places another order for 5,000 USDC (990+4,950 escrowed, plus another 50 USDC of dust) in the same block/period.
3. Governance, using a slightly stale off-chain dust total, dispatches `SweepDust{token: USDC, amount: 60, beneficiary: treasury}` believing only 10 USDC of "old" dust remains uncounted — but due to a race/reorg/timing issue the on-chain function has no way to verify this against `_orders` and transfers 60 USDC unconditionally.
4. If any additional or unaccounted overlap occurs (e.g., a partial fill releasing escrow mid-flight, or a second sweep dispatched before the first's effects are reflected off-chain), the swept amount can exceed true protocol-owned dust, pulling from User A's or User B's escrowed 990/4,950 USDC.
5. When User A's order is later redeemed via `onAccept(RedeemEscrow)` → `_withdraw()`, `IERC20(token).safeTransfer(beneficiary, amount)` reverts (or partially succeeds at another user's expense) because the gateway's real USDC balance is now less than `_orders[commitment][USDC]` claims, permanently freezing that user's funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-373)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-656)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
            unchecked {
                ++i;
            }
            emit DustSwept(token, amount, req.beneficiary);
        }
    }
```
