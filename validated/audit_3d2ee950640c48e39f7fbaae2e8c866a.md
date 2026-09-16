### Title
`CallDispatcher.dispatch()` has no caller restriction, letting anyone drain any assets it is holding - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, shared, protocol-wide contract referenced by `IntentGatewayV2` (`_params.dispatcher`) that temporarily custodies user/solver funds during predispatch swaps (`placeOrder`) and postdispatch calldata execution (`_execute`/`fillOrder`). Its `dispatch(bytes memory encoded)` function is `external` with **no access-control modifier at all** — any address, not just `IntentGatewayV2`, can call it directly and force the dispatcher to execute arbitrary `Call[]` (including `IERC20.approve`/`transfer` or forwarding held ETH) against whatever balance the dispatcher currently holds. This mirrors the FootiumEscrow bug class: an unprivileged, un-gated "approve/execute arbitrary call" entrypoint on a fund-holding contract that anyone can invoke to seize assets that are not theirs.

### Finding Description
`CallDispatcher.dispatch` is defined with zero caller checks: [1](#0-0) 

`IntentGatewayV2.placeOrder` treats this contract as a trusted, ephemeral custodian: it transfers `order.predispatch.assets` to `dispatcher`, then calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, then sweeps the resulting balance back: [2](#0-1) 

`IntentsBase._execute` similarly routes solver output calldata (and any tokens sitting on the dispatcher after a fill) through the same shared dispatcher: [3](#0-2) 

Because `dispatch()` itself enforces no `msg.sender` restriction (unlike, e.g., a `onlyGateway`-gated mint/burn as seen in `HyperFungibleTokenImpl.sol`), the dispatcher is not actually protected by `IntentGatewayV2`'s logic — it is protected only by the assumption that nobody else calls it while it is holding funds. Any ERC-20 token that leaves residual balance on the dispatcher (fee-on-transfer intermediates, multi-hop swap dust, a call that reverts partway through a batch in a token that doesn't clean up, or simply someone directly sending tokens to the dispatcher address) can be swept out by literally anyone via a direct call: `dispatch(abi.encode([Call{to: token, value:0, data: approve(attacker, type(uint256).max)}]))` followed by `transferFrom`, or more directly a `Call{to: token, data: transfer(attacker, balance)}`. The same applies to native ETH, since the contract accepts ETH via `receive() external payable {}` with no owner/session binding.

This is structurally identical to the Footium report: a shared asset-holding contract exposes an unrestricted "do arbitrary approval/transfer" entrypoint that is reachable by any address, independent of which order/user's funds are currently sitting there.

### Impact Explanation
Any token balance transiently or persistently held by the singleton `CallDispatcher` (dust from predispatch swaps, unswept postdispatch outputs, accidental/incidental transfers) can be seized by an arbitrary unprivileged caller, since `dispatch()` performs the call with the dispatcher's own authority (`to.call{value: call.value}(call.data)`), effectively letting anyone act as the dispatcher and grant approvals or move out tokens/ETH that do not belong to them. Because the dispatcher is shared across every order placed through `IntentGatewayV2` (source and destination chains, predispatch and output-calldata paths), this is a protocol-wide, permanent loss-of-funds primitive, not scoped to a single user's mistake.

### Likelihood Explanation
`dispatch()` is a public external function with no gating, callable in any transaction by any EOA or contract at any time — no privileged role, governance action, or malicious insider is required, satisfying the "unprivileged... token bridger" reachability bar. The main constraint is that the dispatcher must actually be holding a positive balance at the time of the call (e.g., dust left after a predispatch swap that doesn't perfectly reconcile, or output tokens momentarily staged for `_execute`), which is a normal, expected occurrence in fee-on-transfer/multi-hop swap scenarios explicitly acknowledged by the protocol's own `DustCollected` accounting.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by an authorized caller (e.g., the `IntentGatewayV2` instance(s) that are supposed to use it), for example via an `onlyAuthorized` modifier checking `msg.sender` against a stored allow-list of gateway addresses set at construction/initialization. Alternatively, deploy a fresh, single-use `CallDispatcher` per `placeOrder`/`fillOrder` invocation (e.g., via `CREATE2` and self-destruct/sweep-then-abandon pattern) so no shared, externally reachable contract ever custodies funds across independent calls.

### Proof of Concept
1. Note `CallDispatcher.dispatch` is `external` with no modifier: [4](#0-3) .
2. A legitimate `placeOrder` with predispatch swap logic (e.g., ETH→USDC via Uniswap) sends predispatch assets to `dispatcher` and expects `dispatch()` to only be invoked by the gateway with the agreed `Call[]`: [5](#0-4) .
3. If any residual token/ETH balance is left on the shared `dispatcher` after such a flow (e.g., an intermediate swap token not included in `order.inputs`, or accidental direct ETH transfer via its permissionless `receive()`), an attacker can call `dispatcher.dispatch(abi.encode([Call({to: residualToken, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})]))` directly — bypassing `IntentGatewayV2` entirely — then `transferFrom` the approved balance to themselves, or directly issue a `transfer` call to move out any ETH/tokens. No permission check in `dispatch()` prevents this.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-260)
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

            // Build sweep calls and snapshot gateway balances before the sweep.
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-510)
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
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L387-393)
```text
        // Setup calls: wrap ETH, approve WETH, and swap
        Call[] memory calls = new Call[](3);
        calls[0] = Call({to: WETH, value: ethAmount, data: abi.encodeWithSignature("deposit()")});
        calls[1] = Call({
            to: WETH, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, UNISWAP_V3_ROUTER, ethAmount)
        });
        calls[2] = Call({to: UNISWAP_V3_ROUTER, value: 0, data: swapCalldata});
```
