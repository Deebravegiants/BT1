### Title
`CallDispatcher.dispatch()` has no caller restriction, allowing any unprivileged account to hijack tokens/ETH mid-flight during multi-step predispatch/postdispatch/calldata-execution sequences shared across IntentGatewayV2, HyperFungibleToken, and WrappedHyperFungibleToken — (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The reported bug class is that a privileged execution surface (the Router's `execute()`) is shared across unrelated components with no ownership/isolation check, so a bug in one flow can drain funds belonging to another. Hyperbridge's structural analog is `CallDispatcher`: a single, permissionless, unauthenticated executor reused by every app that needs "escrow → arbitrary call → sweep" semantics (`IntentGatewayV2` predispatch/postdispatch, `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution). Its `dispatch()` entrypoint has no access control at all, so any address — not just the app that is mid-flow — can invoke it while tokens/ETH are transiently parked on the dispatcher between the "transfer-in" and "sweep-back" steps of these multi-call sequences.

### Finding Description
`CallDispatcher.dispatch()` is declared fully public with zero restriction on the caller: [1](#0-0) 

It also implements an unrestricted `receive()` so it can accumulate native ETH from anyone: [2](#0-1) 

Every consuming app relies on the same instance and the same two-phase pattern: (1) push assets to the dispatcher via one or more *separate* external transfers, (2) later call `dispatch()` to run the encoded `Call[]`, then (3) sweep the residual balance back. In `IntentGatewayV2.placeOrder`, predispatch assets are pushed to `dispatcher` in a loop of individual `_sendValue`/`safeTransferFrom` calls *before* `dispatch()` is invoked: [3](#0-2) 

and the resulting balance is only swept back afterward, in a second `dispatch()` call: [4](#0-3) 

The same untrusted, ownerless dispatcher is reused for post-fill calldata in `IntentsBase._execute`: [5](#0-4) 

and again for `onAccept` calldata execution in the wrapped token bridge: [6](#0-5) 

Because `token` in `order.predispatch.assets` is attacker-supplied for the attacker's own order, and `IERC20.safeTransferFrom` on a hookable token (e.g. ERC-777-style `tokensToSend`) re-enters the caller's context *before* the full predispatch loop and the intended `dispatch(order.predispatch.call)` step complete, an attacker can re-enter and call `CallDispatcher.dispatch()` themselves — a different contract from `IntentGatewayV2`, so it is not covered by `placeOrder`'s `nonReentrant` guard — to redirect whatever balance is currently sitting on the shared dispatcher (assets already transferred in this loop, or ETH sent via `_sendValue`) to an address of their choosing, ahead of the legitimate swap/sweep. Because `dispatch()` has no notion of "whose flow is this" (no per-caller/per-order isolation, unlike the enum/TypeOfVault isolation recommended in the source report for routers), any unprivileged account reaching this shared executor can act on balances it did not deposit.

### Impact Explanation
`CallDispatcher` transiently custodies real user value (input tokens for escrow, swap proceeds, minted/unlocked bridge tokens, native ETH) across three independently-deployed apps. Because `dispatch()` is unauthenticated, the isolation the original report calls for at the router level is entirely absent at the shared-executor level: a bug or hook in the token/contract targeted by one flow's `Call[]` can be leveraged to steal assets that are momentarily parked on the dispatcher for a *different* leg of the same transaction (or, if any deposit step can be interleaved via reentrancy, for a different user's order). This is a concrete theft-of-funds path reachable by an ordinary intent placer/solver — no privileged role required.

### Likelihood Explanation
Likelihood is contingent on finding a callback-capable token/asset accepted as `order.predispatch.assets[i].token` (or an equivalent hook in the HFT/WHFT flows) that fires mid-loop, i.e. before the compensating `dispatch()`/sweep call executes. `IntentGatewayV2` does not restrict predispatch token types, and fee-on-transfer/callback tokens are explicitly supported and tested elsewhere in the codebase, indicating no allowlist prevents such tokens. The attack requires no privileged access — only the ability to place an order with an attacker-chosen token — making the precondition attacker-controlled and readily reachable.

### Recommendation
Restrict `CallDispatcher.dispatch()` to authenticated callers (e.g., an `onlyAuthorizedApp` allowlist maintained per deploying app, mirroring the report's recommendation to store a `TypeOfVault`/owner tag per component and check it in `execute()`), or replace the shared singleton with a per-call, single-use dispatcher/escrow context so no balance can ever be observed or acted upon by a party outside the flow that deposited it. At minimum, add reentrancy protection so a hookable asset transferred into the dispatcher cannot trigger a nested `dispatch()` call before the depositing flow completes its own `dispatch()`/sweep.

### Proof of Concept
1. Attacker crafts an ERC-777-like token `T` with a `tokensToSend` hook that, when triggered during `transferFrom`, calls `CallDispatcher.dispatch()` directly with a `Call[]` that transfers the dispatcher's current balance of a *different* asset (already deposited earlier in the same `predispatch.assets` loop, e.g. native ETH sent via `_sendValue`) to an attacker-controlled address.
2. Attacker places an order via `IntentGatewayV2.placeOrder` with `predispatch.assets = [ETH_amount, T_amount]` and a `predispatch.call` that would normally swap the combined balance on Uniswap.
3. During the loop in `evm/src/apps/IntentGatewayV2.sol` lines 234-258, the ETH is sent to `dispatcher` first; then `safeTransferFrom` for `T` triggers the `tokensToSend` hook, which calls `CallDispatcher.dispatch()` (unguarded, `evm/src/utils/CallDispatcher.sol` lines 44-61) to sweep the ETH already sitting on the dispatcher to the attacker before the intended `dispatch(order.predispatch.call)` runs.
4. The subsequent legitimate `dispatch()` call and sweep either revert (denying the user's own order) or complete with reduced funds — while the diverted ETH is now attacker-held, demonstrating that a caller other than the intended flow can act on the shared dispatcher's balance mid-transaction.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

**File:** evm/src/utils/CallDispatcher.sol (L41-62)
```text
    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-258)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-289)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-504)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L326-328)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```
