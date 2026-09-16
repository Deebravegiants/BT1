### Title
Unrestricted, permissionless `CallDispatcher.dispatch()` combined with full-balance sweeps in `IntentGatewayV2.placeOrder` predispatch flow allows theft/front-running of escrowed input tokens - (File: evm/src/utils/CallDispatcher.sol, evm/src/apps/IntentGatewayV2.sol)

### Summary
The Notional report's root cause is: a "restore" routine assumes *all* balance currently held by a shared contract belongs to the operation being performed, and sweeps it in without distinguishing funds that were legitimately produced by that operation from funds that arrived via donation/front-run. The Hyperbridge `IntentGatewayV2.placeOrder` predispatch flow contains the same class of bug, but worse: the shared `CallDispatcher` singleton that temporarily custodies user input tokens exposes `dispatch(bytes)` with **no caller restriction at all**, and the gateway's own sweep logic reads `IERC20(token).balanceOf(dispatcher)` (the dispatcher's *entire* balance) rather than tracking exactly what the predispatch call produced.

### Finding Description
In `placeOrder` (`evm/src/apps/IntentGatewayV2.sol`, predispatch branch), when an order carries `predispatch.call`/`predispatch.assets`:

1. The user's predispatch input tokens are transferred to the shared `_params.dispatcher` contract: [1](#0-0) 

2. The dispatcher executes the (untrusted) predispatch call: [2](#0-1) 

3. The gateway then sweeps the dispatcher's tokens back to itself using the dispatcher's **full current balance**, not the amount actually produced by the predispatch call for this specific order: [3](#0-2) 

This is the exact "all balances held are assumed to belong to this operation" pattern from the Notional report — any tokens sitting in the shared `dispatcher` (whether leftover dust from a prior order's incomplete sweep, or tokens sent in directly by a third party) get vacuumed into the current `placeOrder` call's accounting.

The severity is amplified because `CallDispatcher.dispatch` itself is completely permissionless — any external account can call it directly at any time to make the dispatcher execute arbitrary `Call[]`: [4](#0-3) [5](#0-4) 

Because `_params.dispatcher` is a single shared, well-known address used by (potentially) every `IntentGatewayV2` order with a predispatch leg, and its `dispatch` function has no access control (no `onlyGateway`/`restrict` modifier, no reentrancy/ownership check), an attacker can:
- Observe a user's `placeOrder` transaction in the mempool after Phase 1 has transferred the user's predispatch assets to the dispatcher but before the gateway calls `dispatch(order.predispatch.call)` and performs its sweep, and front-run it with their own call to `CallDispatcher.dispatch()` containing a `Call` that transfers the dispatcher's ERC-20/ETH balance to themselves.
- More generally, race any legitimate `placeOrder` predispatch flow, since the dispatcher never verifies who invoked `dispatch` or that the call it's asked to execute originated from a legitimate gateway invocation.

Even absent an attacker directly draining it, the balance-based sweep (`balanceOf(dispatcher)`) mixes any residual/donated tokens into the escrow accounting for whichever order happens to sweep next, which is the same "restoration/re-entry ignores provenance of funds" defect flagged in the reference report — the code should track exactly the amount the predispatch call is expected to produce for the current order rather than reading the dispatcher's total balance.

### Impact Explanation
- **Direct theft of user funds**: since `dispatch` is callable by anyone, an attacker can drain tokens/ETH sitting in the shared `CallDispatcher` (deposited there mid-flight by a legitimate `placeOrder` predispatch step) before the gateway's own sweep executes, resulting in permanent loss of the user's escrowed input tokens.
- **Escrow/commitment corruption**: even without an attacker draining funds, using `balanceOf(dispatcher)` for the sweep means unrelated balances (dust from a previous order's rounding, a stuck predispatch call, or a third-party donation) get folded into the current order's `received` amount, corrupting the amount recorded in escrow and the commitment hash computed from it (`keccak256(abi.encode(order))`), which can desynchronize on-chain escrow accounting from what the user actually intended to deposit.
- This is reachable by any unprivileged user placing an order with a predispatch leg (`placeOrder`), matching the "single submitted transaction" bar for high-severity issues.

### Likelihood Explanation
High. `placeOrder` with `predispatch.call`/`predispatch.assets` is a documented, first-class feature (used for cases like "unwrapping LP tokens" per the code's own comment), so predispatch orders are expected to occur in normal operation, not an edge case. `CallDispatcher.dispatch` is public with zero access control, so exploitation requires no privileged position — merely watching the mempool (or racing block inclusion) for `placeOrder` transactions that populate the shared dispatcher, or exploiting any lingering balance left by a prior transaction.

### Recommendation
1. Add access control to `CallDispatcher.dispatch` so only the `IntentGatewayV2` instance(s) authorized to use it (or the specific caller that funded it in the same transaction) may invoke it — e.g., restrict to the calling gateway contract, or make the dispatcher ephemeral/per-call (deploy via `CREATE2`/clone per order) instead of a shared singleton.
2. In `placeOrder`'s predispatch sweep, do not use `balanceOf(dispatcher)`; instead, only sweep the incremental balance produced by the specific predispatch call for this order (e.g., snapshot the dispatcher's balance immediately before transferring assets in and calling `dispatch`, and sweep only the delta), so unrelated/pre-existing funds in the dispatcher can never be attributed to the current order.
3. Ensure the whole predispatch sequence (fund transfer → dispatch → sweep) is atomic and cannot be interleaved with an external `dispatch` call from another transaction — e.g., a transient lock/flag on the dispatcher that only the initiating gateway call can set/clear within the same transaction.

### Proof of Concept
1. Attacker monitors the mempool for a `placeOrder(order, graffiti)` call on `IntentGatewayV2` where `order.predispatch.call.length > 0` and `order.predispatch.assets.length > 0`.
2. After the victim's transaction executes Phase 1 (transferring `order.predispatch.assets` — e.g., 1,000 USDC — to `_params.dispatcher` via `evm/src/apps/IntentGatewayV2.sol:244-256`) but before the victim's transaction reaches the sweep step (`evm/src/apps/IntentGatewayV2.sol:268-289`) in the same block ordering, the attacker submits a higher-gas-price transaction calling `CallDispatcher.dispatch(...)` directly (`evm/src/utils/CallDispatcher.sol:44`) with a `Call[]` of `{to: USDC, value: 0, data: transfer(attacker, 1000e6)}`.
3. Because `dispatch` has no caller restriction, this succeeds, moving the 1,000 USDC out of the dispatcher to the attacker.
4. The victim's `placeOrder` transaction then executes its own `dispatch(order.predispatch.call)` (which may fail or produce nothing useful) and its sweep step observes `balanceOf(dispatcher)` == 0 (or leftover unrelated dust), so `order.inputs[i].amount` is recorded as far less than the user intended (or the transaction reverts due to `InvalidInput()` if `balance < requiredAmount`), and in the drain case, the user's funds are simply gone from the dispatcher, permanently lost.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L244-256)
```text
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L258-258)
```text
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** evm/src/apps/IntentGatewayV2.sol (L268-289)
```text
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

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L32-37)
```text
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
}
```
