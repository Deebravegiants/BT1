## Finding

### Title
Permissionless `CallDispatcher.dispatch()` forwards arbitrary `Call.value` from the contract's own balance with no caller restriction or value-accounting check - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch()` is the Hyperbridge analog of `WalletImpl.execCalls()`: a function that iterates an attacker/user-supplied `Call[]` and forwards native value per-call via `to.call{value: call.value}(data)`. Just like `WalletImpl`, it never reconciles the value it is about to forward against the value that was actually contributed/earmarked for that specific invocation - it simply trusts whatever native balance happens to sit in the contract at call time. Unlike `WalletImpl.execCalls()` (which is at least gated `onlyOwner`), `CallDispatcher.dispatch()` has **no access control whatsoever** - it is a bare `external` function callable by anyone, at any time, directly, not only through `IntentGatewayV2`/`HyperFungibleToken`.

### Finding Description
`CallDispatcher` is a shared, standalone contract with a `receive() external payable {}` and a fully public `dispatch(bytes memory encoded)`: [1](#0-0) 

It decodes an arbitrary `Call[]` and, for each entry, forwards `call.value` out of its own current balance to `call.to`, with no check that:
- the caller is an authorized protocol contract (e.g. `IntentGatewayV2`, `HyperFungibleToken`), and
- the sum of `Call.value` in the batch corresponds to funds that were actually just deposited into the dispatcher for this specific request.

This mirrors the reported `WalletImpl.execCalls()` root cause exactly: a batch-call executor that forwards `value` without validating it against the funds actually supplied for that execution. Here, the interface itself is explicitly documented as dispatching "untrusted call(s)": [2](#0-1) 

Production callers rely on this contract as a transient holding/forwarding vault: `IntentGatewayV2.placeOrder()` sends predispatch assets to the dispatcher, calls `dispatch(order.predispatch.call)` (calldata fully controlled by the order's creator), then sweeps the resulting balance back: [3](#0-2) 

and `IntentsBase._execute()` does the same for postdispatch output calldata, again fully attacker/order-creator controlled, then sweeps whatever balance remains as "dust": [4](#0-3) 

Because `dispatch()` is a standalone, unauthenticated `external` entrypoint and the value it forwards is drawn from the dispatcher's *current total balance* rather than being tied to a specific caller's contribution, any native ETH that happens to be resident in `CallDispatcher` at any point (from its public `receive()`, from rounding/dust that a sweep pass fails to fully collect, or simply between the "transfer-in" and "sweep-back" steps of a legitimate flow if reentered) can be redirected to an arbitrary address by anyone crafting a `Call[]` with an inflated `value` field and calling `dispatch()` directly - completely outside of, and without needing permission from, `IntentGatewayV2` or `HyperFungibleToken`.

### Impact Explanation
Any native ETH balance sitting in the singleton `CallDispatcher` - which is shared across every order and every token-bridge calldata execution in the protocol - can be permissionlessly drained by an unrelated third party, since `dispatch()` performs no caller check and no reconciliation between the value it forwards and the value legitimately deposited for the request being serviced. This is a direct fund-theft vector matching the "concrete theft ... of funds" bar in scope.

### Likelihood Explanation
`dispatch()` requires no special privilege, no proof, and no prior state - a single unprivileged call is sufficient once any ETH balance exists in the contract (e.g. via its public `receive()`, or transient balances during the atomic predispatch/postdispatch windows of `IntentGatewayV2`/`IntentsBase`, both of which pass fully attacker-controlled `Call[]` calldata into `dispatch()`).

### Recommendation
Restrict `CallDispatcher.dispatch()` to authorized callers only (e.g. an `onlyAuthorizedCaller` allowlist of `IntentGatewayV2`/`HyperFungibleToken` instances), and additionally require that the total `Call.value` forwarded in a batch be explicitly funded/reconciled by the calling context (e.g. pass and check an expected total value, or use `msg.value`-based accounting analogous to fixing `WalletImpl.execCalls()`), rather than implicitly trusting whatever balance the dispatcher currently holds.

### Proof of Concept
1. Any amount of native ETH becomes resident in `CallDispatcher` (e.g., a direct transfer to its `receive()`, or unswept dust left after a legitimate `IntentGatewayV2`/`IntentsBase` flow).
2. An attacker calls `CallDispatcher.dispatch(encoded)` directly (no relationship to any order, no `IntentGatewayV2` interaction needed) with `encoded` decoding to `Call[] = [{ to: attacker, value: <dispatcher's balance>, data: "" }]`.
3. `dispatch()` executes `attacker.call{value: balance}("")`, which succeeds since it is fully backed by the dispatcher's current balance, transferring the funds to the attacker with no authorization check at any point in the call path. [5](#0-4)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L37-61)
```text
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-259)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```
