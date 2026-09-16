## Analog Found

### Title
Unrestricted `CallDispatcher.dispatch()` lets anyone steal any tokens/ETH held by the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, permissionless, protocol-wide shared contract used by `IntentGatewayV2` (predispatch/postdispatch calldata execution) and by `HyperFungibleToken`/`WrappedHyperFungibleToken` (post-mint calldata execution) to execute arbitrary `Call[]` on behalf of orders/transfers. Its `dispatch(bytes memory encoded)` function is `external` with **no access control whatsoever** — no `onlyGateway`, no `onlyHost`, no caller check of any kind.

### Finding Description
`CallDispatcher.dispatch` decodes an arbitrary `Call[]` and executes each call from the dispatcher's own context, forwarding any ETH the caller specifies in `call.value`: [1](#0-0) 

Because this function has no restriction on `msg.sender`, **anyone** can call it directly with a crafted `Call[]` such as `{to: token, value: 0, data: transfer(attacker, balanceOf(dispatcher))}` for any ERC-20, or `{to: attacker, value: address(dispatcher).balance, data: ""}` for native ETH — sweeping whatever the dispatcher currently holds.

The dispatcher is designed to hold funds only transiently: `IntentGatewayV2.placeOrder` transfers predispatch assets into the dispatcher, invokes `dispatch()` with the order's calldata, and then issues a second `dispatch()` call to sweep the resulting balance back to the gateway: [2](#0-1) 

Documentation confirms the dispatcher is a long-lived, address-listed, shared deployment reused across many orders and chains, and even flags that dust/residuals routinely remain in it between calls: [3](#0-2) [4](#0-3) 

This is the same bug class as the DODORouteProxy report: a shared/intermediate contract that is not supposed to persistently hold value, but can (accidental transfers, leftover swap dust, a call reverting mid-batch on a chain without atomic bundling guarantees, or a race between the "transfer-in" and "sweep-out" calls of `placeOrder`/`fillOrder`), combined with an unauthenticated arbitrary-call execution entrypoint that lets any third party drain whatever balance is currently sitting there — regardless of who put it there or why.

### Impact Explanation
Any ERC-20 tokens or native ETH momentarily or accidentally held by `CallDispatcher` (dust between the predispatch execution and the sweep-back in `placeOrder`, postdispatch execution residue in `fillOrder`/`_execute`, HFT calldata-execution mint targets, or plain accidental transfers) can be stolen in full by an unrelated, unprivileged attacker simply calling `dispatch()` directly on the well-known, publicly listed `CallDispatcher` address. Since the same dispatcher instance is shared across all orders and apps on a chain, this is not scoped to a single user's funds — any value transiently routed through it is at risk of outright theft.

### Likelihood Explanation
`dispatch()` is directly callable by anyone with zero preconditions — no proof, no signature, no gateway/host check — so exploitation requires nothing beyond noticing a non-zero balance on the dispatcher and submitting one transaction. Given the multi-step, non-atomic flow in `placeOrder`/`fillOrder` (transfer-in → external call → sweep-out) and dust noted in the docs as an expected occurrence, the dispatcher is expected to hold non-zero balances at various points, making this readily and repeatedly triggerable.

### Recommendation
Restrict `CallDispatcher.dispatch()` to be callable only by the trusted gateway/token contracts that are meant to use it (e.g., an `onlyAuthorizedCaller` modifier backed by an allowlist set by governance), or make each caller deploy/own its own dispatcher instance rather than sharing one contract across all apps and orders. At minimum, ensure no value is ever expected to rest in the dispatcher between calls within the same transaction, and add a governance-only sweep function instead of relying on an unauthenticated generic executor to move out incidental balances.

### Proof of Concept
1. Wait for (or trigger, e.g., via a predispatch swap that leaves rounding dust, or a direct accidental transfer) a non-zero ERC-20/ETH balance on the publicly known `CallDispatcher` address.
2. Attacker calls `CallDispatcher.dispatch(abi.encode(calls))` directly (not through `IntentGatewayV2`), where `calls[0] = Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(token).balanceOf(dispatcherAddr))})`.
3. `dispatch()` executes the call unconditionally (no caller check), transferring the entire balance to the attacker. The same works for native ETH by setting `call.value` to the dispatcher's balance and `to` to the attacker's address.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L235-311)
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

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L99-112)
```text
### Predispatch

The `predispatch` field in `Order` contains calldata to execute *before* escrowing inputs. The predispatch assets specified in `DispatchInfo.assets` are transferred to the `CallDispatcher`, the encoded calls are executed, and the resulting tokens are transferred back to the gateway for escrow. This enables swap-then-escrow patterns — for example, a user sends ETH which the `CallDispatcher` swaps to DAI on Uniswap, and the resulting DAI is escrowed as the order input.

### Postdispatch

The `call` field in `PaymentInfo` contains calldata to execute *after* the order is filled. This enables fill-then-act patterns — for example, output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary.

Execution timing differs by mode:

- **Same-chain**: Calldata executes only after the order is **fully filled**. Partial fills do not trigger calldata — only the final fill that completes the order executes it. This ensures all output tokens are available when the calls run.
- **Cross-chain**: Calldata executes **immediately** after the solver delivers output tokens to the beneficiary, before the settlement message is dispatched back to the source chain.

After execution, any tokens remaining in the `CallDispatcher` are swept back to the gateway and collected as dust (emitting `DustCollected` for each token). When postdispatch calldata is present, 100% of any surplus (solver overpayment) goes to the protocol rather than being split with the beneficiary — this prevents manipulation of surplus distribution through calldata side effects.
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
