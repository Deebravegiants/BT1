## Analysis

The Votium `applyRewards()` pattern — a party executes attacker/user‑supplied `(target, calldata)` tuples against arbitrary contracts, including unrestricted `approve()` calls, from a stateful shared contract that also handles other parties' funds — has a direct analog in Hyperbridge's `IntentGatewayV2` / `CallDispatcher` design.

`CallDispatcher.dispatch()` executes an arbitrary, caller-supplied `Call[]` array against any contract with code, with **no allowlist of targets or selectors**: [1](#0-0) 

This dispatcher is a **single, shared, permanently deployed contract instance** — its address is fixed at `IntentGatewayV2` deployment (`Params.dispatcher` / `CALL_DISPATCHER`) and reused by *every* order from *every* user on that chain, not scoped per order: [2](#0-1) 

Any unprivileged user, at `placeOrder()`, fully controls the calldata routed through this shared dispatcher via `order.predispatch.call` (executed *before* escrow) and `order.output.call` (postdispatch, executed *after* a solver delivers tokens): [3](#0-2) [4](#0-3) 

Just like Votium's `applyRewards()`, the gateway grants the calldata author (any order-placing user — no privileged role even required here) the ability to issue arbitrary ERC-20 `approve()` calls *from the dispatcher's own balance* to any spender, with no validation that the calldata is a legitimate swap, and no automatic revocation of approvals afterward. Because the dispatcher is shared and long-lived, an approval granted by one user's order calldata persists on-chain indefinitely and applies to whatever balance the dispatcher holds in later, unrelated transactions.

The sweep-back logic that is supposed to return dispatcher balances to the gateway is scoped only to the tokens explicitly declared in that specific order (`order.inputs` for predispatch, `order.output.assets` for postdispatch): [5](#0-4) [6](#0-5) 

Any token/ETH balance left in the dispatcher that is *not* one of those declared tokens (e.g., swap leftovers, refunds, or unrelated tokens produced by an attacker-crafted swap path) is never swept and remains stranded in the shared contract — exactly the kind of residual value an attacker who previously planted a `max` approval to themselves (via their own cheap order's predispatch/postdispatch calldata) can later drain with a plain `transferFrom`, since that approval was never scoped, expired, or reset.

### Title
Unrestricted arbitrary-call surface in the shared `CallDispatcher` lets any order-placer plant persistent token approvals and drain dispatcher-held dust from unrelated orders - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`IntentGatewayV2` routes fully user-controlled calldata (`order.predispatch.call`, `order.output.call`) through a single, permanently shared `CallDispatcher` contract for every order on a chain. `CallDispatcher.dispatch()` places no restriction on call targets, selectors, or the ability to grant unlimited ERC-20 approvals from its own balance. Because the sweep-back logic only recovers tokens explicitly declared by the current order, any dispatcher-held balance outside that declared set (dust, swap leftovers, or tokens from a differently-shaped malicious call) persists across transactions in a contract shared by every user, and can be captured by anyone who previously used their own order's calldata to grant themselves an approval.

### Finding Description
`CallDispatcher.dispatch()` executes each `Call{to, value, data}` unconditionally as long as `to` has code, exactly mirroring the pattern the reference report flags — arbitrary target, arbitrary calldata, no semantic validation of what the call does (e.g., no restriction to a known DEX router, no check that output is a specific token). [1](#0-0) 

Unlike a typical "solver executes calldata against their own funds" pattern, the dispatcher here is a single deployed instance reused across *all* orders and *all* users (`Params.dispatcher` set once at gateway deployment). Both the predispatch path (attacker's own assets, moved into the dispatcher before escrow) and the postdispatch path (a solver's tokens, moved into the dispatcher to fulfill an order) execute the *order creator's* arbitrary calldata against this same shared contract instance: [3](#0-2) [4](#0-3) 

Nothing in this flow prevents the order-supplied `Call[]` from including `IERC20(anyToken).approve(attackerAddress, type(uint256).max)`. That approval is granted directly from the `CallDispatcher`'s address and is never revoked by the protocol. The subsequent sweep step only forwards balances of tokens the *current* order explicitly declared (`order.inputs` / `order.output.assets`); anything else left in the dispatcher — swap dust, an unaccounted refund token, or balances arising from a differently-crafted call path in a later order — remains in the dispatcher indefinitely, exactly as `applyRewards()`'s ungoverned approvals left the Votium strategy's balances exposed to whatever spender was approved.

### Impact Explanation
Any token balance stranded in the shared `CallDispatcher` (dust, rounding remainders, swap leftovers, or tokens from a misrouted call) is drainable by any address that was previously granted an approval through a prior, unrelated order's calldata. Since placing an order costs only gas plus the (attacker's own, trivial) predispatch amount, an attacker can cheaply pre-plant approvals on commonly-swapped tokens (WETH, USDC, DAI) and passively collect any residual balance other users' orders leave behind in the shared dispatcher over time. This is a permanent, unauthorized-approval-based value leak from a contract that is supposed to be a stateless pass-through, directly analogous to the "rewarder" in the referenced report being handed unrestricted approval and call power over strategy-held assets.

### Likelihood Explanation
Placing a malicious order with crafted `predispatch.call`/`output.call` requires no special privilege — any address can call `placeOrder()`. The only precondition for profit is that the shared dispatcher accumulates a non-zero balance of the approved token outside the declared input/output set, which can occur from routine slippage/rounding in swap-based predispatch/postdispatch flows that the docs themselves acknowledge as a normal "dust" byproduct.

### Recommendation
- Do not allow order-supplied calldata to call `approve()` (or any state-changing call) directly on arbitrary tokens/targets from the shared `CallDispatcher`; restrict the dispatcher's callable targets to an allowlist (e.g., known DEX routers) or require an ephemeral, single-use dispatcher/proxy per order.
- After every `dispatch()` invocation, explicitly revoke any approvals the batch may have granted (reset to zero) rather than leaving them standing indefinitely.
- Sweep *all* token/ETH balances left in the dispatcher after each order's calldata execution, not just the tokens declared in `order.inputs`/`order.output.assets`, so no dust can accumulate for a later attacker to claim.

### Proof of Concept
1. Attacker calls `placeOrder()` with `predispatch.assets = [{token: WETH, amount: 1 wei}]` and `predispatch.call` encoding `Call{to: WETH, data: approve(attacker, type(uint256).max)}`. This executes via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` and grants the attacker an unlimited WETH allowance directly from the shared `CallDispatcher`. [3](#0-2) 
2. Over time, other users' predispatch/postdispatch swap calldata (e.g., Uniswap swaps routed through the same dispatcher) leave WETH dust in the dispatcher that is not part of those orders' declared `inputs`/`output.assets`, so it is never swept. [6](#0-5) 
3. Attacker calls `WETH.transferFrom(dispatcher, attacker, WETH.balanceOf(dispatcher))` at any later time, draining the accumulated dust using the approval planted in step 1.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
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
    }
```

**File:** evm/script/DeployIntentGateway.s.sol (L71-85)
```text
        bytes memory initData = abi.encodeCall(
            IntentGatewayV2.initialize,
            (
                Params({
                    host: HOST_ADDRESS,
                    dispatcher: config.get("CALL_DISPATCHER").toAddress(),
                    solverSelection: config.get("7702").toBool(),
                    surplusShareBps: 6_000, // 60%
                    protocolFeeBps: 5, // 0.05%
                    priceOracle: address(0)
                }),
                peerChains,
                relayer
            )
        );
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-258)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-299)
```text
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
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L504-545)
```text
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
