Confirmed: `_execute` in `IntentsBase.sol` sweeps output tokens by snapshotting `dispatcher.balanceOf` *before* the raw `IERC20.transfer.selector` call, encoding a fixed `balance` amount into the sweep call, and emitting `DustCollected(token, balance)` immediately — with no post-transfer balance check on the gateway side. This differs from the `IntentGatewayV2.placeOrder` predispatch path (lines 291-306), which explicitly re-measures `balanceOf(address(this))` after the sweep to compute `received`. `_execute`'s sweep never re-verifies that `address(this)` actually gained `balance`; it only relies on `CallDispatcher.dispatch`'s `success` bool from the raw `.call()`, which is true even if the ERC20 contract returns `false` (a still-valid, non-reverting failure per EIP-20) instead of reverting.

### Title
`_execute`'s output-token sweep trusts a raw `IERC20.transfer` call's `success` flag instead of verifying the actual balance received - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentsBase._execute`, invoked after a solver fills a cross-chain or same-chain order with attached output calldata, sweeps any leftover output tokens from the `CallDispatcher` back to the gateway using a raw, unchecked `IERC20.transfer` selector call routed through `CallDispatcher.dispatch`, then immediately emits `DustCollected` for the full pre-transfer balance without verifying the gateway actually received those tokens.

### Finding Description
In `_execute` [1](#0-0) , for each ERC20 output asset, the code reads `balance = IERC20(token).balanceOf(dispatcher)` and builds a `Call` that encodes `abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)`, then emits `DustCollected(token, balance)` immediately, before the call is even dispatched.

The actual execution happens later via `ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls))` [2](#0-1) . `CallDispatcher.dispatch` only checks the raw `call()`'s `success` boolean and reverts with `CallFailed` if it is `false` [3](#0-2) . It does not decode or check the ABI-encoded `bool` return value that `IERC20.transfer` is supposed to produce.

Per EIP-20, a compliant token is permitted to return `false` on a failed transfer instead of reverting. If the target ERC20 is such a token (or any target whose call self-reports failure via return data rather than reverting — e.g., paused/blacklist-style tokens that "succeed" at the EVM level but return `false`), `success` from `to.call(...)` will still be `true`, so `CallDispatcher` will not revert, and `_execute` will have already emitted `DustCollected(token, balance)` and returned normally — while the gateway's actual token balance never increased.

This is the same root-cause pattern as the referenced report (UXDController not checking ERC20 transfer/transferFrom results): a raw/low-level ERC20 transfer whose boolean success is never inspected, so the contract's accounting (here, dust bookkeeping and downstream governance sweeps of protocol dust) silently diverges from real token custody. Note this differs from the sibling code path in `IntentGatewayV2.placeOrder`'s predispatch sweep, which re-measures `balanceOf(address(this))` after the dispatch and treats the diff as the real received amount [4](#0-3)  — `_execute` has no equivalent post-transfer verification.

### Impact Explanation
The gateway's dust/fee accounting (used by governance to sweep protocol dust, per `DustCollected` events referenced in the intent-gateway docs) can be permanently desynchronized from actual token custody for non-standard or malicious ERC20 tokens used as order outputs, since `order.output.assets` tokens are attacker/solver-influenced. Funds nominally "collected as dust" per the emitted event are never actually transferred to the gateway, and no revert protects against this silent failure — this is a fund-accounting integrity break tied to a message-dispatch path reachable by any solver filling an order with attached output calldata.

### Likelihood Explanation
Requires the order's output token to be a non-standard ERC20 that returns `false` rather than reverting on failed transfer, and for that transfer to actually fail (e.g., a blacklist/pause condition or insufficient allowance-like edge case on a bespoke token) at the moment of sweep. This is a known-but-uncommon token behavior; likelihood is moderate given intents/order outputs support arbitrary attacker/solver-chosen tokens.

### Recommendation
Replace the raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` construction in `_execute`'s sweep with a balance-diff check identical to the one already used in `IntentGatewayV2.placeOrder`'s predispatch sweep: snapshot `balanceOf(address(this))` before dispatching the sweep calls, and after `dispatch()` returns, compute `received = balanceOf(address(this)) - before` and only emit `DustCollected` for the actually-received amount (or revert if it is less than expected).

### Proof of Concept
1. An order is placed and filled cross-chain/same-chain with `order.output.call` non-empty and one `order.output.assets[i].token` set to a non-standard ERC20 (`FalseReturnToken`) that returns `false` on failed `transfer` instead of reverting.
2. After the solver's output calldata runs, the dispatcher holds `balance` of `FalseReturnToken`. `_execute` builds a sweep `Call` for `abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)` and emits `DustCollected(token, balance)`.
3. `ICallDispatcher(dispatcher).dispatch(...)` executes `to.call(data)`; `FalseReturnToken.transfer` internally fails and returns `false`, but the low-level `call` still reports `success = true` (no revert) — `CallDispatcher` does not decode/check the returned `bool`, so it does not revert.
4. `_execute` returns normally; the gateway's `DustCollected` event and any governance sweep logic believe `balance` of `FalseReturnToken` was collected, but the gateway's actual token balance is unchanged — the tokens remain stuck on the `CallDispatcher`, permanently unaccounted for.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L535-544)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L289-306)
```text
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
```
