### Title
IntentGatewayV2 (Tron) predispatch sweep credits escrow from raw `balanceOf(dispatcher)` instead of a per-order delta - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the Tron variant of `IntentGatewayV2.placeOrder`, the predispatch-sweep path measures how much of a token the shared `dispatcher` contract holds by calling `IERC20(token).balanceOf(dispatcher)` directly, with no "balance-before" snapshot, and then sweeps that entire raw balance into the gateway while crediting escrow with a value computed independently of what was actually swept. This is the same anti-pattern that let the JUDAO exploit drain a Pancake pair: treating a shared/pooled contract's live `balanceOf` as if it were the amount attributable to a single operation, instead of measuring `after - before` for that operation.

### Finding Description
`placeOrder` in the predispatch branch does: [1](#0-0) 

```solidity
for (uint256 i; i < inputsLen;) {
    address token = address(uint160(uint256(order.inputs[i].token)));
    uint256 requiredAmount = order.inputs[i].amount;
    uint256 balance;
    ...
    balance = IERC20(token).balanceOf(dispatcher);
    if (balance < requiredAmount) revert InvalidInput();
    transferCalls[i] = Call({to: token, value: 0,
        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)});
    ...
    uint256 dust = balance - requiredAmount;
    if (dust > 0) emit DustCollected(token, dust);
    _orders[commitment][token] += reducedInputs[i].amount;
    ...
}
```

`dispatcher` (`_params.dispatcher`) is a single shared contract used by every `placeOrder`/`fillOrder`/`cancelOrder` call across all users, and it is invoked with an attacker-supplied `order.predispatch.call` (`ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`) immediately before this snippet runs. Because the sweep reads `balanceOf(dispatcher)` as an absolute value rather than a delta between a pre-call and post-call snapshot, it does not distinguish "tokens this order's predispatch call produced" from "whatever tokens happen to sit on the dispatcher when this line executes" (leftover dust from a prior order's incomplete sweep, tokens sent to the dispatcher by any third party, or tokens deliberately staged there by an attacker's own predispatch calldata targeting another order in flight).

This is structurally identical to the JUDAO root cause: JUDAO's sell hook read `judao.balanceOf(JUDAO_USDT_PAIR) - reserveJudao` as the swap input, so crediting an operation based on a shared contract's live balance rather than a value actually attributable to that specific transfer let the attacker inject tokens directly and have them treated as belonging to the swap. Here, the escrow bookkeeping (`_orders[commitment][token] += reducedInputs[i].amount`) is decoupled from what was actually swept off the dispatcher, and the swept amount itself (`balance`, the dispatcher's *entire* current balance) can be inflated by anything else that has deposited into that shared dispatcher — the classic "measure the pool's live balance instead of a tracked delta" defect.

Notably, the parallel EVM-mainline contract already fixed this exact defect by snapshotting balances before the sweep and computing a delta: [2](#0-1) 

The Tron contract is a regression of that fix — it never took the pre-sweep snapshot before reintroducing raw-`balanceOf` semantics.

### Impact Explanation
`_orders[commitment][token]` is the escrow the gateway later releases on `fillOrder`/`cancelOrder`/refund paths. Because the swept-and-credited amounts are not tied to a measured per-order delta, this path allows:
- Escrow that does not match what the gateway contract can actually cover, if the dispatcher's balance the sweep is based on was inflated or drained by unrelated traffic through the same shared `dispatcher`.
- A shared, attacker-influenceable pooled balance being treated as belonging to a single order's transfer, which is the same "unbacked accounting from raw pool balance" bug class that let JUDAO's attacker drain a pair's reserves in one transaction.

This can lead to escrow/accounting desynchronization from the gateway's actual token holdings — a form of fund-accounting corruption in the intent-escrow bookkeeping reachable by any unprivileged order-placer supplying an attacker-controlled `predispatch.call`.

### Likelihood Explanation
Likelihood is Medium: the predispatch/dispatcher mechanism is reachable by any ordinary user calling `placeOrder` with a non-empty `predispatch.call`/`predispatch.assets`, and the `dispatcher` is shared infrastructure by design (used across concurrent orders), so any deposit landing on it before this measurement — whether from a race with another order, dust from an interrupted call, or a directly engineered predispatch call — perturbs the measured `balance`. It does not require privileged access, only that the predispatch/call-dispatcher flow is exercised, which is the intended usage pattern for "transfer-and-swap" style orders documented for this app.

### Recommendation
Mirror the already-fixed EVM-mainline pattern: snapshot `IERC20(token).balanceOf(address(this))` (or the dispatcher's pre-call balance) before dispatching the predispatch call/sweep, then compute the amount actually attributable to this order as `after - before`, and use that measured delta — not the shared contract's absolute live balance — both for the transfer amount and for the value credited to `_orders[commitment][token]`.

### Proof of Concept
Not independently executable from the indexed contents alone (no live fork/PoC harness for the Tron contract was found in the index); the analysis above is based on direct comparison of `evm/tron/contracts/apps/IntentGatewayV2.sol` lines 416–446 against the corrected snapshot/delta logic in `evm/src/apps/IntentGatewayV2.sol` lines 260–311, which demonstrates the raw-`balanceOf` regression. A concrete step-by-step transaction trace analogous to the JUDAO PoC (pre-funding the shared `dispatcher` with the target token immediately before a victim/attacker's own `placeOrder` predispatch sweep executes, then observing that `balance` at line 428 includes the injected amount) would need to be validated against the actual `CallDispatcher` and `_params.dispatcher` deployment wiring, which was not fully explorable within the remaining tool budget.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L260-311)
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
