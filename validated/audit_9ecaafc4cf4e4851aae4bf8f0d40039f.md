## Title
CallDispatcher and IntentGatewayV2/IntentsBase Ignore ERC20 `transfer` Boolean Return Values, Allowing Tokens to Become Permanently Stranded — (File: evm/src/utils/CallDispatcher.sol, evm/src/apps/IntentGatewayV2.sol, evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`CallDispatcher.dispatch` executes arbitrary `Call[]` batches with a raw low-level `.call()` and only reverts if the call itself reverts; it never inspects the ABI-decoded boolean return value. `IntentGatewayV2` (and its Tron mirror) and `IntentsBase` both build sweep/return-transfer calls with raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` — bypassing `SafeERC20` — and route them through `CallDispatcher`. For any ERC-20 whose `transfer` returns `false` on failure instead of reverting (permitted, and even required-to-be-handled behavior under the ERC-20 spec), the dispatched call reports `success = true` even though no tokens moved.

### Finding Description
`CallDispatcher.dispatch` only checks the low-level call's success flag: [1](#0-0) 

It never decodes `result` to check the ERC20 boolean return, unlike the rest of the codebase which correctly uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom` everywhere else (e.g. `HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentsBase._withdraw`).

`IntentGatewayV2.placeOrder` builds a raw `transfer` call to sweep the predispatch-call output tokens from the `CallDispatcher` back to the gateway, then trusts the *balance delta* it observes, not any ERC-20 return value: [2](#0-1) 

The Tron variant does the same but is worse — it doesn't even re-measure balance after the sweep, it directly credits `reducedInputs[i].amount` to escrow (`_orders[commitment][token] += reducedInputs[i].amount`) assuming the sweep succeeded: [3](#0-2) 

`IntentsBase._execute` (used by `fillOrder`'s postdispatch calldata path) does the same raw, unchecked-return sweep for dust collection after solver-supplied output calldata executes: [4](#0-3) 

If a token whose `predispatch`/`output` calldata routes through the `CallDispatcher` returns `false` on `transfer` instead of reverting (this is explicitly permitted by ERC-20 and the exact bug class the external report describes), the sweep-back call from the `CallDispatcher` to the gateway appears to succeed (no revert), but no tokens actually move. The real tokens remain stuck inside the `CallDispatcher` contract, which has no owner-controlled recovery/rescue function — only `dispatch()` — so they cannot be retrieved.

### Impact Explanation
- On the standard EVM `IntentGatewayV2.placeOrder`, the balance-delta check (`received = balanceOf(this) - balancesBefore[i]`) will compute `received = 0`, silently setting `order.inputs[i].amount = 0` and thus escrowing zero for that leg while the user's real predispatch-swap output sits permanently trapped in the `CallDispatcher`. This is a permanent freezing of user funds.
- On the Tron `IntentGatewayV2` (no balance re-check), the escrow bookkeeping (`_orders[commitment][token] += reducedInputs[i].amount`) is credited even though the tokens never left the `CallDispatcher`, causing the gateway's internal escrow accounting to diverge from its actual on-chain token holdings — a state the gateway will later try to pay out of but does not actually hold, which can lead to insolvency/DoS for other orders' withdrawals sharing that token, or a shortfall discovered at settlement time.
- The `IntentsBase._execute` dust-sweep path similarly emits `DustCollected` events and assumes tokens returned to the gateway when a non-compliant token silently fails, again leaving dust value permanently stuck in the `CallDispatcher`.

This satisfies the "permanent freezing of funds" / "unsound state commitment" bar, reachable from a single unprivileged `placeOrder` (or a solver's `fillOrder` with postdispatch calldata) using a token in the predispatch/output swap step that returns `false` rather than reverting.

### Likelihood Explanation
This requires the predispatch/postdispatch calldata to interact with a non-standard ERC-20 (return-false-on-failure) as one of the swapped/output assets — such tokens exist in production (e.g., legacy tokens, some wrapped/synthetic assets) and predispatch/output calldata is explicitly designed to support arbitrary DEX/DeFi integrations with attacker/solver-chosen tokens, so the trigger condition is realistically reachable by any user or solver who (deliberately or not) routes such a token through the calldata-execution feature.

### Recommendation
In `CallDispatcher.dispatch`, either (a) require calls that target a token's `transfer`/`transferFrom` selector to use `SafeERC20`-equivalent return-value checking, or (b) generically decode `result` when it is non-empty and revert if it decodes to `abi.decode(result, (bool)) == false`. Additionally, replace the raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` calls in `IntentGatewayV2.placeOrder`, the Tron mirror, and `IntentsBase._execute` with calls to a dedicated helper contract that uses `SafeERC20.safeTransfer`, so sweep-back operations use the same return-value-safe library used everywhere else in the codebase.

### Proof of Concept
1. Deploy a mock ERC-20 `FalseReturnToken` whose `transfer` sets balances only if `to != address(0)` but explicitly `return false` when, e.g., a paused flag is set (mimicking real non-compliant tokens) — do NOT revert.
2. Configure an `IntentGatewayV2.Order` with `predispatch.call` that swaps native/ETH into `FalseReturnToken` via a mock router, landing the output balance on the `CallDispatcher`.
3. Set `predispatch` pause flag so the token's `transfer` call (used in the gateway's sweep-back `transferCalls`) returns `false`.
4. Call `placeOrder`. Observe: `ICallDispatcher.dispatch(abi.encode(transferCalls))` does not revert (low-level call succeeded), `balanceOf(gateway)` is unchanged, `order.inputs[i].amount` is set to `0`, and the swapped tokens remain permanently locked in the `CallDispatcher` with no function to recover them.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L273-311)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
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

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
    }
```
