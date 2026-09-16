### Title
`CallDispatcher.dispatch` has no caller restriction, letting anyone drain residual token balances/allowances left on the shared dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
The autonolas `GuardCM` finding shows that a guard which is supposed to restrict what a privileged multisig can execute can be bypassed because one execution path (`delegatecall` to a non-owner target) is left completely unchecked, letting the caller reach arbitrary code with the guard's authority. The Hyperbridge analog is `CallDispatcher.dispatch`, a function that also executes arbitrary attacker/solver-supplied `Call[]` against arbitrary targets, but — unlike the intended trust model — carries **no caller restriction at all**. Any account can call it directly, at any time, to execute calls out of the dispatcher's own context and balance.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` is declared `external` with no modifier restricting `msg.sender`: [1](#0-0) 

It is used by `IntentsBase._execute` (`IntentGatewayV2`) and by the `HyperFungibleToken`/`WrappedHyperFungibleToken` apps as a shared, singleton "untrusted call" executor: tokens are minted or transferred to the dispatcher address, and then `dispatch()` is invoked with solver/order-supplied calldata to swap, approve, or otherwise act on those tokens: [2](#0-1) 

The `IntentGatewayV2` path explicitly sweeps any leftover balance out of the dispatcher back to the gateway in the same atomic transaction: [3](#0-2) 

However, this sweep only clears **balances**, not **allowances**, and the dispatcher's own docs acknowledge that residual approvals are a known hazard: [4](#0-3) 

Because `dispatch()` is unauthenticated, any leftover ERC-20 allowance or ETH/token balance sitting on the `CallDispatcher` between transactions — e.g. from an order/solver that sizes an approval larger than what the downstream swap call actually consumes, or from any transaction that leaves residual value on the shared dispatcher for any other reason (rounding, partial fills, a reverted/skipped downstream call inside a multi-call batch that nonetheless doesn't cause the whole batch to revert) — can be swept out by **any unprivileged third party**, not just the gateway/token contract that created the allowance. The attacker simply submits an ordinary transaction calling `CallDispatcher.dispatch(...)` with a `Call{to: token, data: transferFrom(dispatcher, attacker, amount)}` or `transfer`, since the function performs no check on `msg.sender` and no check that the call originates from `IntentGatewayV2`/`HyperFungibleToken`.

This mirrors the root cause of the GuardCM bug: a shared execution primitive that is supposed to operate only within a specific, permissioned flow instead exposes an open door that any caller can walk through to reach the same execution power, defeating the implicit trust boundary the surrounding contracts rely on (that only the gateway/token contract routes calls through the dispatcher while it holds funds).

### Impact Explanation
Any value (tokens, or dangling ERC-20 allowances) that transiently or accidentally remains on the `CallDispatcher` contract — a contract shared across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` — can be permanently stolen by an unprivileged attacker with a single transaction, since `dispatch()` has no access control. This is a direct theft-of-funds vector rather than a theoretical one, given the protocol's own documentation calls out that "unlimited allowances" left after a solver/order's calldata execution are unsafe specifically **because** the dispatcher is a shared, generally-callable contract.

### Likelihood Explanation
Reachability requires nothing more than an ordinary EVM transaction from any address to `CallDispatcher.dispatch()` — no ISMP message, proof, or governance action is needed. The only precondition is that some balance or approval is left on the dispatcher, which the protocol's own docs treat as a realistic operational risk for solver-composed `Call[]` payloads (predispatch/postdispatch swaps, HFT calldata execution). Given the dispatcher is reused across multiple apps and deployments (a single "existing `CallDispatcher` deployment" address is documented as shared), the surface for such residue accumulating and being swept by a third party is non-trivial.

### Recommendation
Restrict `CallDispatcher.dispatch` to only be callable by an authorized/allow-listed caller (e.g., the specific `IntentGatewayV2`/`HyperFungibleToken` instances that are meant to use it), or make the dispatcher single-use/ephemeral (e.g., deploy a fresh dispatcher per call via `CREATE2`/`CREATE`, or use a transient-storage guard so `dispatch()` can only be invoked once per top-level transaction that funded it). Additionally, have every caller of `dispatch()` explicitly revoke any allowances it grants to the dispatcher (`approve(token, 0)`) after the calls complete, not just sweep balances, closing the "residual allowance" attack surface called out in the docs.

### Proof of Concept
1. A solver fills an order (or a `HyperFungibleToken.send` cross-chain mint) whose `Call[]` approves the `CallDispatcher` for more than the downstream swap/router actually consumes (a common pattern if the composer is not careful with "exact amounts," as the docs warn against).
2. The gateway/token contract's atomic flow mints/transfers tokens to `CallDispatcher`, calls `dispatch(calls)`, and (for `IntentGatewayV2`) sweeps the dispatcher's **balance**, but the **approval** for the unspent portion remains outstanding on-chain, referencing the router/DEX as spender.
3. Any third-party attacker submits a plain transaction: `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transferFrom.selector, dispatcher, attacker, leftoverAllowance)})]))` — this succeeds because `dispatch()` performs no caller check, draining the leftover allowance/value out of the shared dispatcher to the attacker. [5](#0-4)

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L504-533)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-96)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```
