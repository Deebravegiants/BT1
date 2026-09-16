## Title
Permissionless `CallDispatcher.dispatch` lets anyone drain any dust it holds during Intent Gateway predispatch/postdispatch execution - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is a shared, stateless-looking utility contract used by `IntentGatewayV2`/`IntentsBase` (and other apps) to execute arbitrary attacker/solver-supplied calldata on behalf of orders (`predispatch` and `output.call`). Its `dispatch(bytes)` entrypoint has **no access control whatsoever** — any address can call it directly at any time to make `CallDispatcher` issue arbitrary calls (with arbitrary `value`) to arbitrary contracts, as `msg.sender = CallDispatcher`. [1](#0-0) 

The Intent Gateway routinely leaves tokens sitting on the `CallDispatcher` between the point where inputs/predispatch assets are transferred to it and the point where they are pulled back into escrow, and it only sweeps back the exact tokens it anticipates (`order.inputs` for predispatch, `order.output.assets` for postdispatch). [2](#0-1) [3](#0-2)  Any residual balance not covered by that fixed token list — dust from fee-on-transfer tokens, DEX-swap slippage, reward/incentive tokens returned by a router, or an order/solver simply crafting `predispatch.call`/`output.call` to leave a token behind — remains parked on `CallDispatcher` rather than the gateway. Because `dispatch()` is unauthenticated, this parked balance can be stolen by any unrelated third party in a separate transaction before the intended sweep or governance `SweepDust` action ever runs.

### Finding Description
This mirrors the CVE-2018-20167 bug class: an "unhandled/leftover" condition (Terminology's unrecognized media type) is deferred to an overly-powerful, generically-invokable executor (`xdg-open`) that will happily act on attacker-supplied content for *anyone* who triggers it. Here, `CallDispatcher.dispatch` is the analogous "generic executor" — it will run any `Call[]` for any caller, and the Intent Gateway's own design routes real user/protocol funds through it as a matter of course:

- `placeOrder` moves `predispatch.assets` (native or ERC20) to `dispatcher`, invokes `dispatch(order.predispatch.call)`, then only pulls back the exact `order.inputs` amounts, computing `dust = balance - requiredAmount` and only sweeping the difference back for tokens that are in the `inputs` list. [4](#0-3) 
- `_execute` (postdispatch, on fill) sends order output tokens through the same `dispatcher`, then sweeps only the tokens enumerated in `order.output.assets` (`outputsLen`) back to the gateway as "dust". [3](#0-2) 
- Both flows depend on `CallDispatcher` momentarily holding token/ETH balances that are *not* atomically fully accounted for in every case — any token returned by the executed calls that is not one of the pre-declared `inputs`/`output.assets` tokens is left behind on `dispatcher` with no automatic recovery in that same transaction.
- Because `ICallDispatcher.dispatch(bytes)` has no `onlyOwner`/`onlyGateway`/`msg.sender` check at all, any external, unprivileged account (an "unprivileged relayer/solver" per the scope) can call `CallDispatcher.dispatch()` directly with a `Call` such as `IERC20(token).transfer(attacker, IERC20(token).balanceOf(dispatcher))` to sweep out any leftover balance before the protocol's own dust-collection mechanism (`_execute`'s sweep, or governance's `SweepDust`) gets to it. [5](#0-4) 

This is a real, reachable "unknown token type mishandling → executed by a permissive generic dispatcher" pattern: the gateway's sweep logic only knows how to recover the specific tokens declared in the order (the "known types"), while any other token/ETH left on the shared dispatcher (the "unknown type") is deferred to `CallDispatcher.dispatch`, a component that — just like `xdg-open` in the CVE — will execute anything for anyone with zero authorization checks.

### Impact Explanation
Any dust left on the shared `CallDispatcher` (fee-on-transfer remainders, DEX slippage/rewards, or dust intentionally crafted by a malicious order/solver whose `predispatch.call`/`output.call` returns an off-list token) is a bounty for any unprivileged third party who front-runs the protocol's sweep by calling `CallDispatcher.dispatch()` directly. This is a concrete, permanent loss of protocol-owned funds (dust that should accrue to governance via `SweepDust`, or occasionally user/solver funds if timing/ordering allows interception before the same-transaction sweep completes for a subset of tokens). Given `CallDispatcher` is shared across the whole Intent Gateway (and potentially other apps configured with the same dispatcher address), the attack surface accumulates across every order that leaves any non-enumerated balance behind.

### Likelihood Explanation
High reachability, requires no special privilege: the attacker only needs to watch for any `DustCollected`/leftover-balance event or directly poll `CallDispatcher`'s token balances and race a plain call to `dispatch()`. No proof, consensus verification, or governance action is required — a single unprivileged transaction suffices whenever the shared dispatcher holds an uncollected residual balance.

### Recommendation
- Restrict `CallDispatcher.dispatch` to an allow-listed caller (e.g., the specific `IntentGatewayV2`/app contract(s) configured to use it), or deploy a dedicated, non-shared, single-use dispatcher per operation (e.g., ephemeral CREATE2 clone per order) so it cannot be invoked by arbitrary third parties.
- Alternatively, make the sweep in `placeOrder`/`_execute` exhaustive rather than allow-list-based — sweep *all* tokens/ETH the dispatcher ends up holding after executing calldata, not only those in `order.inputs`/`order.output.assets`.
- Add a reentrancy/ownership guard to `CallDispatcher` so it only executes calls at the behest of its configured caller, closing the confused-deputy window entirely.

### Proof of Concept
1. A user places an order via `IntentGatewayV2.placeOrder` with `predispatch.call` that swaps ETH for DAI through a router that also returns a small amount of a reward/bonus token (or simply is a fee-on-transfer token scenario) not declared in `order.inputs`.
2. `placeOrder` transfers predispatch assets to `_params.dispatcher`, calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, then sweeps back only the tokens listed in `order.inputs` — the bonus/reward token balance remains on `dispatcher`. [4](#0-3) 
3. Before the gateway's own logic or a subsequent order happens to sweep that token, an unrelated attacker directly calls: `CallDispatcher.dispatch(abi.encode([Call({to: rewardToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(rewardToken).balanceOf(dispatcher))})]))`. [1](#0-0) 
4. The call succeeds because `dispatch` has no caller restriction — the attacker receives the reward token balance that should have accrued as protocol dust for the Intent Gateway.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L234-270)
```text
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
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

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
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
