### Title
Postdispatch/predispatch calldata executed via the shared `CallDispatcher` can permanently strand funds when the target protocol credits `msg.sender` (the dispatcher) instead of an explicit recipient - (File: evm/src/utils/CallDispatcher.sol, evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentGatewayV2` routes order `predispatch`/`postdispatch` calldata through a single, shared `CallDispatcher` contract that becomes `msg.sender` for every external call it makes. If the target protocol invoked by this calldata records ownership, collateral, or a receipt/position keyed to `msg.sender` (rather than to an address passed as an explicit parameter) — the exact failure mode described in the original `SiloGateway`/`FraxLend` report — the resulting position is permanently locked to the `CallDispatcher` address, and the gateway's dust-sweeping logic cannot recover it because it only sweeps known ERC20/native balances, not protocol-internal positions.

### Finding Description
`CallDispatcher.dispatch()` executes arbitrary `Call[]` on behalf of orders, calling `to.call{value: call.value}(call.data)`, meaning any protocol invoked here sees `CallDispatcher` as `msg.sender`: [1](#0-0) 

`IntentsBase._execute()` uses this same dispatcher for postdispatch calldata attached to an order's output, explicitly documenting that "solvers can route through DEXes, lending protocols, or other DeFi primitives as part of filling an order": [2](#0-1) 

After execution, the only recovery mechanism is sweeping the dispatcher's known ERC20 balances for the order's declared output tokens back to the gateway — there is no generic mechanism to recover a lending-protocol collateral position, an LP share, or any other non-transferable/internal accounting entry that a target protocol may have recorded against the `CallDispatcher`'s address: [3](#0-2) 

The same pattern applies on the `placeOrder` predispatch path, where predispatch assets are sent to the dispatcher, arbitrary calldata is executed with the dispatcher as caller, and only declared input token balances are swept back: [4](#0-3) 

The project's own documentation confirms this is an intended use case ("output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary") without any protocol-compatibility guardrails: [5](#0-4) 

This is structurally identical to the reported `SiloGateway.borrowAsset()` issue: a shared intermediary contract calls into third-party protocols "on behalf of" a beneficiary, but if the invoked protocol's accounting model accrues state to the *caller* (`msg.sender == CallDispatcher`) instead of an address parameter, the resulting collateral/position/receipt is permanently locked to the intermediary — which, unlike a normal EOA/user, has no way to interact with that protocol again to reclaim it, since `CallDispatcher` is stateless and only exposes `dispatch()`.

### Impact Explanation
Because `CallDispatcher` is a single shared singleton (`_params.dispatcher`) used across all orders of an `IntentGatewayV2` deployment, any order whose predispatch/postdispatch calldata targets a protocol with this accounting pattern results in a permanent freeze of the escrowed/output funds routed through that call. Funds credited to the dispatcher inside an external protocol (e.g., collateral balances, LP positions, staking receipts) are unrecoverable by both the user/beneficiary and the protocol's own dust-sweep logic, since the sweep only checks `IERC20(token).balanceOf(dispatcher)` for the order's declared tokens, not arbitrary external-protocol state. This constitutes permanent freezing of funds.

### Likelihood Explanation
The predispatch/postdispatch calldata mechanism is explicitly advertised as supporting "lending protocols" and general DeFi composition, and is fully user/solver-controlled data reachable from a single `placeOrder`/`fillOrder` transaction with no allow-list of compatible target protocols. Any protocol that follows an `msg.sender`-based internal accounting model (a common pattern, as demonstrated by the referenced `FraxLendPair._addCollateral`) will trigger this condition without any special privilege or attacker coordination — it can even be triggered unintentionally by a normal user constructing an order.

### Recommendation
- Document and/or enforce an allow-list of protocols verified to support "credit an explicit recipient" semantics for use in predispatch/postdispatch calldata.
- Consider having `CallDispatcher` (or a variant) act through a per-order ephemeral proxy/sub-account instead of a shared singleton address, so any stranded credit is at least isolated per-order and potentially recoverable, rather than pooled at one shared, stateless contract address.
- Add explicit warnings in the SDK/docs that any protocol invoked via `Call[]` must accrue ownership/collateral to a parameter-supplied address, not `msg.sender`, or funds may be permanently lost.

### Proof of Concept
1. A user places a cross-chain order via `IntentGatewayV2.placeOrder()` with `output.call` set to a `Call[]` that, after the solver fills the order and output tokens are delivered to the `CallDispatcher`, calls a hypothetical lending protocol's `deposit()`/`addCollateral()` function that internally does `userCollateralBalance[msg.sender] += amount` (mirroring `FraxLendPair._addCollateral`).
2. `IntentsBase._execute()` invokes `ICallDispatcher(dispatcher).dispatch(order.output.call)` — the lending protocol sees `msg.sender == CallDispatcher` and credits the collateral position to the dispatcher's address, not the order's beneficiary.
3. The post-execution sweep in `_execute()` only checks `IERC20(token).balanceOf(dispatcher)` for `order.output.assets` tokens; since the tokens were consumed into the lending protocol's internal accounting (no ERC20 balance remains on the dispatcher), nothing is swept.
4. The beneficiary never receives the deposited/collateralized funds, and the collateral position recorded against `CallDispatcher` in the external protocol has no path to be withdrawn by the gateway or the user — the funds are permanently frozen.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L487-516)
```text
    /**
     * @dev Executes arbitrary calldata attached to an order's output via the CallDispatcher.
     * After dispatching the calls, any residual token balances left on the dispatcher
     * are swept back to this contract and accounted for as protocol dust.
     *
     * This enables composable order fulfillment — solvers can route through DEXes,
     * lending protocols, or other DeFi primitives as part of filling an order.
     *
     * @param order The order containing the output calldata to execute.
     * @param outputsLen The number of output assets to sweep after execution.
     */
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L517-534)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L235-300)
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

```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L103-112)
```text
### Postdispatch

The `call` field in `PaymentInfo` contains calldata to execute *after* the order is filled. This enables fill-then-act patterns — for example, output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary.

Execution timing differs by mode:

- **Same-chain**: Calldata executes only after the order is **fully filled**. Partial fills do not trigger calldata — only the final fill that completes the order executes it. This ensures all output tokens are available when the calls run.
- **Cross-chain**: Calldata executes **immediately** after the solver delivers output tokens to the beneficiary, before the settlement message is dispatched back to the source chain.

After execution, any tokens remaining in the `CallDispatcher` are swept back to the gateway and collected as dust (emitting `DustCollected` for each token). When postdispatch calldata is present, 100% of any surplus (solver overpayment) goes to the protocol rather than being split with the beneficiary — this prevents manipulation of surplus distribution through calldata side effects.
```
