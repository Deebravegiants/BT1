Confirmed: `CallDispatcher` at `evm/src/utils/CallDispatcher.sol:44-62` is a single shared, stateful contract address (`_params.dispatcher`) reused across every order for a given `IntentGatewayV2` deployment [1](#0-0) . Both `predispatch.call` and `output.call` are attacker/solver-controlled `Call[]` batches executed via `ICallDispatcher(dispatcher).dispatch(...)` against this shared contract [2](#0-1) , and the same dispatcher receives token balances from later, unrelated orders (predispatch assets, or solver-supplied output tokens before the sweep) [3](#0-2) .

### Title
Dangling infinite ERC20 approval left on shared `CallDispatcher` by attacker-crafted order calldata enables theft of funds from unrelated orders - (File: `evm/src/utils/CallDispatcher.sol`, `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`placeOrder`/`fillOrder` let any user or solver supply arbitrary `Call[]` calldata (`order.predispatch.call`, `order.output.call`) that is executed by the single, contract-wide `CallDispatcher` instance shared by all orders on a gateway. A malicious order can include a call such as `IERC20(token).approve(attacker, type(uint256).max)`, mirroring the exact `approveToRouter`-style infinite-approval pattern used legitimately elsewhere in this codebase for swap routers (e.g. `IntentGatewayV2Test.sol:1358-1363`, `UniV3UniswapV2Wrapper.sol:93`). Because the `CallDispatcher` is not single-use or per-order, that approval persists in the token contract's storage after the malicious order's `dispatch()` call returns.

### Finding Description
`CallDispatcher.dispatch` blindly executes whatever calls are ABI-encoded into it, with no restriction on target or calldata beyond "target must have code" [4](#0-3) . `IntentGatewayV2`/`IntentsBase` route both `predispatch` (pre-escrow) and `output.call` (post-fill) calldata through this same dispatcher address for every order on the gateway: `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` at placement [2](#0-1) , and `ICallDispatcher(dispatcher).dispatch(order.output.call)` at fill, followed by a sweep of only the *dispatcher's currently known output tokens* [3](#0-2) .

Any order placer can embed a call like `abi.encodeWithSelector(IERC20.approve.selector, attackerAddress, type(uint256).max)` targeting a token the dispatcher is known to routinely hold (e.g. USDC/DAI used in escrow/fill flows), exactly as demonstrated by the project's own test helpers (`abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)` in `IntentGatewayV2Test.sol:1358-1363`). Since the dispatcher contract is reused across orders and there is no `approve(spender, 0)` reset or dispatcher-per-order isolation, this approval remains live indefinitely. On any subsequent, unrelated order where that same token is transferred into the dispatcher — via `predispatch.assets` transfer (`IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount)`, `IntentGatewayV2.sol:250`) or via a solver sending output tokens to the dispatcher as beneficiary before the post-fill sweep (`IntentsBase.sol:498-527`) — the attacker can front-run the sweep with `transferFrom(dispatcher, attacker, balance)` using the standing allowance and drain those funds before the legitimate gateway logic sweeps them back.

### Impact Explanation
This is concrete theft of funds: unrelated users' escrowed input tokens or solvers' output tokens transiently held by the shared `CallDispatcher` can be stolen by an unprivileged attacker who placed an earlier order purely to plant the approval, then races (or simply front-runs, since approvals persist across blocks) subsequent legitimate token transfers into the dispatcher. This satisfies "concrete theft ... of funds" reachable from a single submitted transaction (placing one malicious order), matching the required impact bar.

### Likelihood Explanation
Likelihood is high: placing an order with attacker-chosen `predispatch.call`/`output.call` is a fully permissionless, single-transaction action available to any user/solver — no privileged role is required, unlike the excluded malicious-admin/governance categories. The dispatcher's shared, persistent nature and lack of allowance-reset logic make the dangling approval trivially plantable and durably exploitable against any later order using the same token.

### Recommendation
- Reset every approval the `CallDispatcher` grants immediately after use (`approve(spender, 0)`), or better, require `forceApprove`-style exact-amount, single-use allowances scoped to the swap amount rather than `type(uint256).max`.
- Deploy a fresh, single-use `CallDispatcher` (or a minimal proxy clone) per order instead of one shared, stateful instance, eliminating any cross-order approval residue.
- Alternatively, have `CallDispatcher.dispatch` disallow `approve` calls to non-allowlisted spenders, or have the gateway explicitly revoke allowances for all tokens involved in an order immediately after `dispatch()` returns.

### Proof of Concept
1. Attacker calls `placeOrder` with `predispatch.assets = [{token: USDC, amount: 1}]` and `predispatch.call` encoding `Call[]{ {to: USDC, data: approve(attacker, type(uint256).max)} }`. This is executed via `ICallDispatcher(dispatcher).dispatch(...)` in `IntentGatewayV2.sol:258`, leaving `USDC.allowance(dispatcher, attacker) = type(uint256).max`.
2. A later, unrelated victim places an order with `predispatch.assets` containing USDC, which is transferred to the same `dispatcher` via `IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount)` (`IntentGatewayV2.sol:250`) before the gateway's own sweep call executes.
3. Attacker calls `USDC.transferFrom(dispatcher, attacker, amount)` using the standing allowance from step 1, draining the victim's tokens out of the dispatcher before the gateway's sweep (`IntentGatewayV2.sol:261-289`) can pull them back into escrow.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-527)
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
```
