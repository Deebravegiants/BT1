### Title
Unrestricted `CallDispatcher.dispatch()` lets any unprivileged caller execute arbitrary calls under the bridge's shared dispatcher identity - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
The IPA advisory's root cause is that a component executes attacker-influenced content (a chroot'd deployed image) with elevated privileges outside any sandbox boundary — i.e., functionality reachable from an untrusted control sphere is executed with the wrong trust level. The Hyperbridge analog is `CallDispatcher.dispatch()` [1](#0-0) , a single, deterministically-deployed (same `CREATE2` salt/bytecode, no constructor args) contract that is explicitly documented as dispatching "untrusted call(s)" [2](#0-1) , yet the `dispatch()` entrypoint has no access control whatsoever — it can be called directly by any unprivileged address, not only by the app contracts (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`) that are supposed to be the only legitimate callers.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` decodes an arbitrary `Call[]` and executes `to.call{value: call.value}(call.data)` for each entry, with `msg.sender` inside that sub-call being the `CallDispatcher` contract itself [3](#0-2) . There is no `onlyHost`, `onlyApp`, or reentrancy/caller check on this function.

Multiple trusted application flows route attacker- or user-supplied calldata and token balances through this exact contract, relying on it purely as an execution proxy scoped to their own transaction:
- `WrappedHyperFungibleToken.onAccept()` (and the upgradeable variant) executes arbitrary `message.data` — decoded straight from the cross-chain `PostRequest` body that originated from an untrusted source-chain contract call — via `ICallDispatcher(_dispatcher).dispatch(message.data)` [4](#0-3) .
- `IntentGatewayV2.placeOrder()` transfers order input tokens into the same `dispatcher` address, then calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` followed by a second `dispatch()` call that sweeps the dispatcher's *entire current token balance* to the gateway [5](#0-4) .
- Deployment scripts instantiate `CallDispatcher` with `CREATE2{salt: salt}` and no constructor arguments for each app (`DeployHFT.s.sol`, and similarly for `DeployWrappedHFT`/`DeployIntentGateway`) [6](#0-5) , meaning deployments that share the same salt/bytecode across apps resolve to the identical on-chain address — a single shared, cross-application dispatcher identity.

Because `dispatch()` is unauthenticated, any unprivileged actor (a relayer, a bandwidth purchaser, an intent solver, or any random address) can call `CallDispatcher.dispatch()` directly at any time with a self-crafted `Call[]`, executing calls as `msg.sender = CallDispatcher`. This is exploitable in two concrete ways:
1. **Balance sweep**: whenever any bridged message or in-flight order transiently leaves ERC20/native balance sitting in the shared dispatcher (e.g. dust from a partially-consumed `predispatch.call`, or tokens deposited by `WrappedHyperFungibleToken.onAccept` before its own `dispatch()` call completes), an outside caller can invoke `dispatch()` first with a `Call` that transfers that balance to themselves, since the call executes with the dispatcher's own token custody.
2. **Approval hijack**: if any token/contract ever grants an ERC20 allowance to the dispatcher address (a natural pattern for a "call executor" that needs to move tokens it holds, e.g. approving a router mid-`predispatch.call`), any unprivileged caller can invoke `dispatch()` with `transferFrom(victim, attacker, amount)` targeting that token, since `msg.sender` for the ERC20 check is the dispatcher, independent of who called `dispatch()`.

This is the same class of flaw as the CVE: a mechanism designed to execute payloads on behalf of a specific, bounded caller/context is instead globally reachable, so functionality that should stay inside the calling app's trust boundary is exposed to the entire untrusted world.

### Impact Explanation
Any funds that transiently pass through, or any allowance ever granted to, the shared `CallDispatcher` can be stolen by an arbitrary unprivileged third party who front-runs or simply calls `dispatch()` opportunistically — a direct theft-of-funds vector across every app that reuses this dispatcher (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`). This satisfies the "concrete theft ... of funds" acceptance bar because the dispatcher's balance/allowance is not access-controlled to the app that populated it.

### Likelihood Explanation
High: `dispatch()` requires zero privilege and zero proof — it is a plain external call reachable from a single unprivileged transaction. The only precondition is that the shared dispatcher momentarily holds a balance or allowance, which the existing app flows (`IntentGatewayV2.placeOrder`'s multi-step transfer/dispatch/sweep sequence, `WrappedHyperFungibleToken.onAccept`'s post-mint `dispatch(message.data)`) are designed to create routinely.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a known, per-app-configured caller (e.g. `onlyHost`/`onlyApp` modifier keyed to the deploying contract), or eliminate the shared-singleton pattern entirely by deploying a dispatcher instance uniquely bound to (and only callable by) each app contract, so that `msg.sender` inside the sub-calls can never be reused across unrelated trust domains or unprivileged callers.

### Proof of Concept
1. Any user calls `WrappedHyperFungibleToken.send()`/triggers a bridged message whose `message.data` (attacker-controlled) is dispatched via the shared `CallDispatcher`, or a normal `IntentGatewayV2.placeOrder()` executes a `predispatch.call` leaving the dispatcher holding leftover ERC20 balance (e.g., a swap that doesn't consume the full transferred amount).
2. An unrelated, unprivileged attacker directly calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(token).balanceOf(dispatcherAddr))})]))` — no permission is required since `dispatch()` has no caller restriction [3](#0-2) .
3. The call executes with `msg.sender = CallDispatcher`, transferring out the dispatcher's held balance to the attacker, regardless of which app or order the funds belonged to.

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

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L26-37)
```text
/**
 * @title The ICallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This interface is used to dispatch untrusted call(s)
 */
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
}
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L355-357)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L234-289)
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

**File:** evm/script/DeployHFT.s.sol (L14-20)
```text
        CallDispatcher dispatcher = new CallDispatcher{salt: salt}();
        HyperFungibleToken hft = new HyperFungibleToken{salt: salt}(name, symbol, admin);

        hft.configure(HyperFungibleToken.ConfigOptions({
            host: HOST_ADDRESS,
            dispatcher: address(dispatcher)
        }));
```
