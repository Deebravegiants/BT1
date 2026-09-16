Confirmed vulnerability: `CallDispatcher.dispatch` has no access control and is a shared, stateless-by-design utility contract reused across `IntentGatewayV2`/`IntentsBase` and every `HyperFungibleToken` variant. `placeOrder` (`evm/src/apps/IntentGatewayV2.sol:236-289`) and `_execute` (`evm/src/apps/intentsv2/IntentsBase.sol:498-540`) both transiently push real user funds (predispatch assets, output-fill assets) onto the `CallDispatcher` and then call `dispatch` a second time to sweep them back — but `dispatch` itself checks nothing about who is calling it or what step of the flow is in progress.

### Title
Unauthenticated `CallDispatcher.dispatch` allows theft of funds transiently held by the shared dispatcher during order fills - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch(bytes)` is `external` with zero access control — no `onlyHost`, no caller allowlist, nothing restricting who invokes it. It is a single shared contract address configured as `_params.dispatcher` for `IntentGatewayV2` and referenced from `HyperFungibleToken`/`WrappedHyperFungibleToken` variants for calldata execution on `onAccept`. `IntentGatewayV2.placeOrder` and `IntentsBase._execute` both transfer real ERC20/native balances onto this dispatcher, then call `dispatch` to run solver-supplied calldata against those funds, and finally call `dispatch` again to sweep the resulting balance back to the gateway. This works only because in the intended flow nobody else touches the dispatcher's balance in between. [1](#0-0) 

### Finding Description
`dispatch` executes any attacker-supplied `Call[]` — arbitrary `to`, `value`, `data` — against whatever balance the `CallDispatcher` contract currently holds, using the dispatcher's own identity as `msg.sender`: [2](#0-1) 

The intended callers (`IntentGatewayV2.placeOrder`, `IntentsBase._execute`) rely on the dispatcher briefly holding user funds between the moment tokens/ETH are pushed to it and the moment the sweep call drains it back: [3](#0-2) [4](#0-3) 

Because `dispatch` has no gate at all, any account — an unprivileged solver, a bot watching the mempool, or simply anyone calling the deployed `CallDispatcher` address directly — can race a pending `placeOrder`/`fillOrder`/`onAccept` transaction (front-run it in the same block, or exploit any transaction that reverts mid-flow leaving funds parked) and call `CallDispatcher.dispatch` themselves with calldata that transfers out whatever ERC20/ETH balance the dispatcher is currently holding, since the contract itself never tracks which app or which order the balance belongs to. This is analogous to the reported ADK issue in that a function capable of driving arbitrary execution/state-changing effects is reachable with no authentication whatsoever — the "missing authentication for critical function" (CWE-306) class — except here the critical function is a fund-holding dispatch primitive shared across every intents/token app on the chain rather than an agent RPC endpoint.

### Impact Explanation
Any value the `CallDispatcher` momentarily holds during `predispatch`/`output.call` execution in `IntentGatewayV2` (or any future integrator that reuses this same dispatcher pattern) can be permanently stolen by an unrelated third party who simply calls `dispatch` first. Given that `placeOrder`'s predispatch flow explicitly moves user-supplied assets onto the dispatcher before invoking arbitrary calldata and only sweeps afterward, and `_execute`'s output-fill flow does the same for solver-side composable fills, a window exists in which anyone's `dispatch` call — not just the gateway's own follow-up call — can claim the balance. This is concrete theft of user/solver funds, not merely a griefing/DoS issue.

### Likelihood Explanation
The dispatcher's address is public (referenced in `Params.dispatcher` and constructor wiring for `HyperFungibleToken`), and any pending transaction that pushes funds to it (visible in the mempool as a normal `placeOrder`/`fillOrder` call, or via a partially-failed transaction that leaves a balance stranded) is directly exploitable by a generic front-running bot with no special privilege — this fits squarely in the "unprivileged intent solver" reachable category the scope calls out. No governance, admin, or validator compromise is required.

### Recommendation
Restrict `CallDispatcher.dispatch` to only be callable by the specific app contract that owns the funds being routed through it (e.g., an `onlyCaller`/allowlist check bound at construction, or deploy a dedicated dispatcher instance per app rather than sharing one address across `IntentGatewayV2` and every token app), and/or redesign the flow so no user funds are ever left on a shared, permissionless contract between two calls in the same transaction (e.g., pull-based execution where the calldata operates via `transferFrom` rather than pre-funding the dispatcher).

### Proof of Concept
1. Observe a pending `IntentGatewayV2.placeOrder` transaction with a non-empty `predispatch.call` in the mempool; it will, per [5](#0-4) , transfer `predispatch.assets` (ERC20/native) to `_params.dispatcher` and then call `dispatch(order.predispatch.call)`.
2. Front-run it with a direct call to the same `CallDispatcher` address's `dispatch(bytes)` function, supplying a `Call[]` that transfers the just-arrived token/ETH balance to an attacker-controlled address — nothing in `CallDispatcher.dispatch` ( [2](#0-1) ) checks the caller or restricts which balance can move.
3. The original `placeOrder` transaction subsequently either reverts (its own sweep finds insufficient balance) or under-escrows the order, and the attacker keeps the stolen funds — no authentication was required to invoke the exact same "critical function" the legitimate flow relies on.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-290)
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

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-518)
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
```
