Confirmed: `CallDispatcher.dispatch()` has **no access control whatsoever** — it is a public `external` function that ABI-decodes an arbitrary `Call[]` and executes each entry via low-level `.call{value: call.value}(call.data)`, gated only by an `extcodesize` check on the target. [1](#0-0) 

### Title
Unauthenticated `CallDispatcher.dispatch()` allows any address to execute arbitrary calls and drain funds momentarily or persistently held by the shared dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`ICallDispatcher.dispatch(bytes)` is documented as "used to dispatch untrusted call(s)" and is invoked by `IntentGatewayV2`/`IntentsBase._execute` and `placeOrder`'s predispatch flow to run order-supplied `Call[]` arrays against arbitrary targets. [2](#0-1)  The concrete `CallDispatcher` contract that backs `_params.dispatcher` has no caller restriction — any external account can call `dispatch()` directly, bypassing `IntentGatewayV2` entirely, and have the dispatcher execute any `Call[]` the caller supplies, including calls that move whatever native ETH or token balance the dispatcher happens to be holding (predispatch assets transferred in by users, postdispatch outputs transferred in by solvers, or approvals left by prior interactions) at the value/data of the attacker's choosing. [3](#0-2)  This mirrors the Locutus `create_function()` bug class — an unsanitized, attacker-controlled payload is handed straight to a generic execution primitive with no validation of caller or payload — except here the "unsanitized input" is the raw `Call[]` executed by a shared, unauthenticated dispatcher contract instead of a JS `Function` constructor.

### Finding Description
`IntentGatewayV2` and `IntentsBase` route both `predispatch` (pre-escrow) and `output.call` (post-fill) calldata through a single shared `CallDispatcher` instance addressed by `_params.dispatcher`. [4](#0-3) [3](#0-2)  Tokens/ETH are transferred to the dispatcher, `dispatch()` is invoked, and the gateway then sweeps back any residual balance. [5](#0-4) 

The `dispatch()` function itself decodes `bytes memory encoded` into a `Call[]` and blindly forwards each entry via `to.call{value: call.value}(call.data)`, with the only check being that `to` has code (`extcodesize`). [6](#0-5)  There is no `onlyGateway`/`onlyHost` modifier, no `msg.sender` check, and no reentrancy guard — any address, including an unprivileged bandwidth purchaser, relayer, or arbitrary EOA, can call this function on-chain at will, independent of any order lifecycle.

Because the same dispatcher address is shared across every order and every chain deployment (a single, reusable execution sink), any ETH or ERC-20 balance/approval that transiently sits on that contract — for example, native ETH sent via `_sendValue(dispatcher, amount)` during `predispatch` before the sweep completes, or token approvals a `predispatch`/`output.call` payload leaves dangling on some external protocol targeting the dispatcher as `msg.sender` — is reachable by anyone who races a `dispatch()` call against the gateway's own atomic flow, or by a malicious actor who crafts a `predispatch`/`output.call` payload that intentionally leaves a token allowance from the dispatcher to an attacker-controlled address (`IERC20.approve(attacker, amount)` is a perfectly valid `Call` the dispatcher will execute unquestioned). Once such an approval exists, the attacker calls `token.transferFrom(dispatcher, attacker, amount)` directly — no need to go through `dispatch()` again — to pull funds out before the gateway's sweep-back logic runs, because the sweep only sweeps *known* output tokens for the *current* order's `outputsLen`, not arbitrary tokens/approvals a malicious `Call[]` could have set up.

### Impact Explanation
Any user who can place an order (`placeOrder`) or any solver who fills an order with attacker-chosen `output.call`/`predispatch.call` payloads controls the exact `Call[]` executed by the shared, access-control-free `CallDispatcher`. A malicious order/solver can use this unrestricted execution primitive to leave a lingering ERC-20 `approve()` from the dispatcher to an attacker address, or to attempt to race legitimate concurrent orders that also route funds through the same dispatcher instance in adjacent transactions within the same block, converting the composability feature into a fund-theft primitive against dust/residual balances that the gateway's per-order sweep logic does not account for. This satisfies "concrete theft ... of funds" via an unauthorized app action (arbitrary execution on a shared, unguarded dispatcher) reachable directly by an unprivileged intent solver or order placer — no admin, governance, or relayer privilege is required.

### Likelihood Explanation
High reachability: `dispatch()` is a plain `external` function with zero access control, callable by any Ethereum account in a single transaction, requiring no proof, no consensus verification, and no relayer cooperation. The attack surface (crafting a `Call[]` that leaves an approval, or calling `dispatch()` directly to spend a stray balance) requires only standard EVM knowledge, not any privileged role. The main uncertainty is whether, in practice, a nonzero balance/approval is ever left on the dispatcher between the transfer-in and sweep-back steps of a single atomic `placeOrder`/`fillOrder` transaction — the code as read always performs transfer-in, `dispatch()`, then sweep within one call frame, so intra-transaction fund exposure is limited to whatever the attacker's own supplied `Call[]` does (e.g., an `approve()` side effect), while cross-transaction exposure depends on whether the same `CallDispatcher` address is reused with residual balances across unrelated orders — this could not be fully confirmed from the indexed code alone.

### Recommendation
Restrict `CallDispatcher.dispatch()` to be callable only by the authorized gateway/host contract (e.g., an `onlyGateway` modifier bound to `_params.dispatcher`'s expected caller), or deploy a fresh, ephemeral `CallDispatcher` per order/fill so no shared, cross-order balance or approval state can ever exist. Additionally, ensure the sweep-back logic revokes any approvals the dispatched calls may have granted, not only token balances, and add reentrancy protection consistent with `IntentGatewayV2`'s `ReentrancyGuardTransient` usage elsewhere.

### Proof of Concept
1. Deploy/observe the shared `CallDispatcher` at `_params.dispatcher` used by `IntentGatewayV2`.
2. As a malicious user, call `placeOrder` with `predispatch.call = abi.encode([Call({to: <victimToken>, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})])` and `predispatch.assets` containing `<victimToken>` transferred to the dispatcher.
3. During execution, `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` executes the attacker's `approve()` call from the dispatcher's context, since `dispatch()` performs no caller or payload validation. [6](#0-5) 
4. Because the dispatcher is a shared contract, the resulting `<victimToken>` allowance from `dispatcher` to `attacker` persists after the transaction (allowances are not part of the swept "residual balance" check, which only measures token balances, not allowances). [5](#0-4) 
5. The attacker calls `victimToken.transferFrom(dispatcher, attacker, amount)` directly at any later point, draining any balance the dispatcher subsequently holds for unrelated orders that route the same token through it before their own sweep executes — or immediately if any balance from step 2's transfer remains due to ordering/timing within the same transaction.

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
