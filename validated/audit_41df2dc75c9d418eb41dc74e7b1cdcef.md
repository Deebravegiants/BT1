## Analysis Note

I was unable to fully verify a second candidate path (whether `HyperFungibleToken.sol`'s `Message.from` field can be set independently of `msg.sender`, which would affect the impersonation risk in `pallet-hyper-fungible-token`'s unsigned-`SubstrateCalldata` origin derivation) before running out of tool calls. The finding below is based on what I was able to fully confirm.

### Title
Unauthenticated `CallDispatcher.dispatch()` executes fully attacker-controlled calls with no caller restriction, exposing any assets it transiently holds to reentrant theft during predispatch flows - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch(bytes memory encoded)` is a public, unauthenticated function that ABI-decodes an attacker-supplied `Call[]` array and executes each entry (`to.call{value: call.value}(call.data)`) with no `msg.sender` check whatsoever. This mirrors the CVE-2017-12065 bug class: a reachable entry point takes attacker-controlled parameters and uses them directly to drive arbitrary code execution without validating who is allowed to invoke it or what state it may act upon.

### Finding Description [1](#0-0) 

`dispatch()` has no access-control modifier and no reentrancy guard of its own. It is shared across multiple bridge applications — `IntentGatewayV2.placeOrder`/`_execute` and `HyperFungibleToken`/`WrappedHyperFungibleToken`'s `onAccept` — as the execution point for user-supplied `Call[]` payloads: [2](#0-1) [3](#0-2) [4](#0-3) 

In `IntentGatewayV2.placeOrder`, when `order.predispatch` is set, tokens named in `order.predispatch.assets` (fully attacker-controlled token addresses, since the caller supplies their own `Order`) are transferred into the dispatcher one at a time via `IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount)`, and only afterward is `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` invoked to run the user's calls, followed by a sweep back to the gateway. `placeOrder` carries `nonReentrant`, but that lock is local to `IntentGatewayV2`'s own storage — it does not protect `CallDispatcher`, a separate, unguarded contract. If any `predispatch.assets[i].token` is a contract with a transfer callback (e.g., an ERC-777-style token or any custom token the attacker deploys and lists in their own order), that callback fires mid-`safeTransferFrom`, before the intended `dispatch(order.predispatch.call)` runs, and can call `CallDispatcher.dispatch()` directly with its own `Call[]` to move out whatever balance is already sitting on the dispatcher at that point (e.g., earlier assets in the same multi-asset predispatch loop, or any native ETH previously sent via the dispatcher's unrestricted `receive()`).

### Impact Explanation
Because `dispatch()` is callable by anyone and unaware of which order/flow "owns" the funds currently on the dispatcher, any transient balance it holds during the window between funding and sweeping is exposed to interception. This breaks the implicit invariant relied on by `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` that "whatever lands on the dispatcher during this call belongs to this operation and will be swept back correctly." An attacker able to trigger a reentrant callback during their own predispatch asset transfer (a token type entirely of their choosing) can redirect assets mid-flow via `CallDispatcher.dispatch()`, undermining the escrow accounting that downstream code (dust sweep, `_orders` bookkeeping, commitment-based fills) depends on.

### Likelihood Explanation
Reachability requires only a single `placeOrder` (or cross-chain-triggered `onAccept`) transaction with attacker-chosen `predispatch`/`data` fields — no privileged role, governance, or off-chain component is needed. The trigger condition (a token with a transfer hook among the caller-specified predispatch assets) is entirely within the caller's control since they supply both the order and the token list.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a set of authorized callers (the `IntentGatewayV2`/`HyperFungibleToken` contracts that own a given execution), or give the dispatcher its own reentrancy guard so a nested call into `dispatch()` cannot execute while a prior `dispatch()` invocation for the same contract is still unwinding. At minimum, ensure multi-asset predispatch transfers complete in full before any `dispatch()` call is made reachable, and treat any non-standard/hook-bearing ERC-20 as unsupported for predispatch assets.

### Proof of Concept
1. Attacker deploys `EvilToken`, an ERC-20 with a `transferFrom` hook that, when triggered, calls `CallDispatcher.dispatch(maliciousCalls)` on the shared dispatcher address, sweeping its current balance to the attacker.
2. Attacker calls `IntentGatewayV2.placeOrder` with `order.predispatch.assets = [{token: LegitToken, amount: X}, {token: EvilToken, amount: 1}]` and a `predispatch.call` that would (legitimately) swap `LegitToken` for the order's real input token.
3. During the loop in `placeOrder`, `LegitToken` is transferred to the dispatcher first; on the second iteration, `EvilToken.transferFrom` fires its hook, which reenters `CallDispatcher.dispatch()` directly (bypassing `IntentGatewayV2`'s `nonReentrant` guard entirely, since it protects a different contract) and drains the `LegitToken` balance already sitting on the dispatcher before the gateway's own intended `dispatch(order.predispatch.call)` executes. [5](#0-4) [6](#0-5)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L235-259)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L326-328)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```
