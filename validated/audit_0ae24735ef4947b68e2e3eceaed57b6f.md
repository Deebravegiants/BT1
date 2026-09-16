### Title
Postdispatch calldata leftovers are swept as protocol dust instead of returned to the beneficiary - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, function `_execute`)

### Summary
`IntentGatewayV2`'s composable "postdispatch" fill pattern routes solver-delivered output tokens through an arbitrary external protocol call (via `CallDispatcher`) before crediting the beneficiary. Any tokens the external call leaves on the `CallDispatcher` afterward are unconditionally swept into the gateway and permanently classified as protocol dust — with no logic to recognize that a partial/failed external interaction (the exact edge case highlighted in the referenced Malt `Bonding.sol` report, where an external DEX call unexpectedly returns the input asset instead of performing the expected action) should instead be refunded to the order's beneficiary.

### Finding Description
The docs describe the postdispatch flow explicitly: "output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary" [1](#0-0) . This is implemented by `_execute`, called from both `_fillSameChain` (`IntrinsicIntents.sol`) and `_fillCrossChain` (`ExtrinsicIntents.sol`) after solver funds have already landed at the address specified as `order.output.beneficiary` (which, for this pattern, is the `CallDispatcher` or an intermediate contract that the arbitrary calldata is meant to act upon): [2](#0-1) 

After `ICallDispatcher(dispatcher).dispatch(order.output.call)` runs the arbitrary DeFi calldata, `_execute` measures *every* residual token/native balance left on the dispatcher and unconditionally treats it as protocol dust, emitting `DustCollected` and sweeping it back to the gateway contract — with zero distinction between:
1. Genuine leftover dust (e.g., rounding remainder after a successful swap/deposit), which is a reasonable protocol-fee case, and
2. A failed or partially-completed external interaction where the downstream protocol call could not complete as intended and instead returned the original (undeposited/unswapped) asset back to the dispatcher — mirroring precisely the `Bonding.sol`/`UniswapHandler.removeLiquidity` edge case in the reference report, where `amountMalt == 0 || amountReward == 0` caused the LP token itself to be sent back to the caller instead of the expected output, and the caller had no logic to recognize or forward it.

Just as `Bonding.sol`'s `_unbondAndBreak` had no code path to detect "the DEX handler didn't do what I expected, and returned something else instead," `_execute` has no code path to detect "the arbitrary postdispatch call didn't fully consume/forward the beneficiary's funds, and left them here instead." Both cases funnel the value into the intermediary's own generic catch-all handling instead of returning it to its rightful owner.

### Impact Explanation
Because swept "dust" is later distributed only via the governance-gated `SweepDust` request path to an address chosen by protocol parameters — not the order's beneficiary [3](#0-2)  — any tokens that a postdispatch DeFi call fails to fully route (due to slippage protection, insufficient liquidity, a reverted-but-caught inner leg, or any other external protocol condition that returns assets rather than completing the intended action) are permanently misappropriated from the intended beneficiary to the protocol. This is a concrete, permanent loss of user funds triggered entirely by ordinary solver/user activity (placing and filling an order with postdispatch calldata) — no privileged or malicious actor is required, satisfying the "permanent freezing/loss of funds" bar.

### Likelihood Explanation
Postdispatch calldata is an explicitly documented, user/solver-composable feature intended to route funds "through a DeFi protocol" [4](#0-3) , meaning arbitrary third-party protocols (DEXes, lending markets, etc.) are routinely invoked. Any of those downstream protocols experiencing a partial-fill, slippage-guard, or "return principal instead of proceeds" condition — the same general class of edge case already documented as real and exploitable in the reference Uniswap handler code — will trigger this loss. This requires no attacker; it can occur under normal, unprivileged solver-driven order fulfillment whenever the target external protocol behaves defensively.

### Recommendation
In `_execute`, do not treat all residual balances left on the `CallDispatcher` as protocol dust unconditionally. Instead, distinguish between expected surplus and undelivered principal: track the balances the postdispatch call was expected to consume/forward (mirroring the approach already used for predispatch and input-transfer accounting elsewhere in `IntentGatewayV2.sol`, which measures balances before/after and treats any deficit as `InvalidInput`/revert), and forward any tokens matching the beneficiary's expected output amount (or unconsumed principal) back to `order.output.beneficiary` rather than sweeping them into `DustCollected`. Only genuine excess beyond the expected/required amounts should be attributed to protocol dust.

### Proof of Concept
1. User places a cross-chain (or same-chain) order whose `output.beneficiary` is the shared `CallDispatcher` contract and whose `output.call` encodes a DeFi action (e.g., deposit into a lending market or swap via a router) intended to ultimately benefit the user.
2. A solver fills the order; `_fillCrossChain`/`_fillSameChain` transfers the full required output amount to the `CallDispatcher` address (the designated beneficiary for this pattern) [5](#0-4) .
3. `_execute` dispatches `order.output.call`. The target external protocol, under an edge condition (e.g. slippage/liquidity guard analogous to the Uniswap handler's `amountMalt == 0 || amountReward == 0` case), does not perform the intended action and instead leaves the original tokens on the `CallDispatcher`.
4. `_execute`'s sweep loop measures the dispatcher's balance, finds it non-zero, and unconditionally sweeps it into the gateway while emitting `DustCollected` [6](#0-5) .
5. The swept tokens are now only redeemable via a governance-authorized `SweepDust` request to the protocol's chosen beneficiary — the user who placed/expected to benefit from the order never recovers them.

### Citations

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L103-112)
```text
### Postdispatch

The `call` field in `PaymentInfo` contains calldata to execute *after* the order is filled. This enables fill-then-act patterns — for example, output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary.

Execution timing differs by mode:

- **Same-chain**: Calldata executes only after the order is **fully filled**. Partial fills do not trigger calldata — only the final fill that completes the order executes it. This ensures all output tokens are available when the calls run.
- **Cross-chain**: Calldata executes **immediately** after the solver delivers output tokens to the beneficiary, before the settlement message is dispatched back to the source chain.

After execution, any tokens remaining in the `CallDispatcher` are swept back to the gateway and collected as dust (emitting `DustCollected` for each token). When postdispatch calldata is present, 100% of any surplus (solver overpayment) goes to the protocol rather than being split with the beneficiary — this prevents manipulation of surplus distribution through calldata side effects.
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L186-196)
```text
            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L345-346)
```text
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
```
