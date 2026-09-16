## Analysis: Fee-on-transfer / unswept-balance escrow miscrediting in `evm/tron/contracts/apps/IntentGatewayV2.sol`

### Title
Predispatch escrow crediting in `IntentGatewayV2.placeOrder` (Tron variant) trusts pre-sweep balances instead of verified post-sweep receipts, allowing under-collateralized escrow entries — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2.placeOrder` computes the amount credited to escrow (`_orders[commitment][token]`) from the **CallDispatcher's balance measured before the sweep transfer executes**, and unconditionally credits `reducedInputs[i].amount` (derived from the order's originally requested amount) rather than the amount actually delivered to `address(this)` afterward. This is the exact bug class in the reference report: a balance/accounting value is captured or assumed at the wrong point in execution and then trusted as if it reflects the real post-transfer state, letting real and recorded balances diverge.

### Finding Description
In the predispatch branch of `placeOrder`:
<cite repo="Alyssadaypin/hyperbridge--025" path="evm/tron/contracts/apps/IntentGatewayV2.sol" start="416="/> [1](#0-0) 

For each input token, the code:
1. Reads `balance` — the dispatcher's ERC20/native balance **before** any sweep call has run.
2. Builds a `transferCalls[i]` entry to move `balance` from the dispatcher to `address(this)`.
3. Computes `dust = balance - requiredAmount` and immediately credits `_orders[commitment][token] += reducedInputs[i].amount` — **before** `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` is even called at line 449.

The escrow ledger is therefore populated using a value that assumes the subsequent sweep will deliver exactly `balance` (or at least `requiredAmount`) to the gateway, with no verification step afterward. This is structurally identical to the audited `TradingUtils#_executeTrade` bug: a "pre-state" balance is used to derive a credited amount that should instead come from measuring `postBalance - preBalance` *after* the movement occurs.

Contrast with the corrected pattern used in the sibling EVM implementation, which snapshots `balancesBefore[i]` immediately before the sweep dispatch, then measures the **actual delta** afterward and only credits/records that measured amount: [2](#0-1) 

The Tron variant omits this delta measurement entirely, so:
- **Fee-on-transfer / deflationary ERC20 tokens**: `IERC20(token).transfer(address(this), balance)` can deliver less than `balance` to the gateway. The escrow is still credited with `reducedInputs[i].amount` (based on the pre-transfer `balance`/`requiredAmount`), even though the gateway's actual on-chain balance is lower. This directly creates an unbacked escrow liability.
- **Any sub-call in the batched sweep that does not revert the whole dispatch on partial failure** compounds this: escrow crediting happens in the same loop *before* `dispatch(abi.encode(transferCalls))` is invoked, so a failed or partial transfer for one token is never reflected in the already-computed escrow credit.

### Impact Explanation
`_orders[commitment][token]` is the authoritative escrow ledger that downstream `fillOrder`/settlement logic pays out against. If this ledger is credited with more value than the gateway actually holds, the contract becomes insolvent for that token: some combination of solver payouts, refunds, or cancellations will fail or drain the real balance leaving later claimants unable to be paid — a permanent freezing/loss-of-funds scenario for users whose orders reference the inflated escrow. This is reachable by any unprivileged user simply by calling `placeOrder` with a predispatch call routing through a fee-on-transfer token (or any token/flow where sweep delivery can fall short of the pre-sweep balance reading), matching the "intents escrow" reachable path explicitly in scope.

### Likelihood Explanation
Likelihood is Medium-High: predispatch calldata and asset routing through the `CallDispatcher` is a first-class, user-controlled feature of `placeOrder` (`order.predispatch.call` / `order.predispatch.assets`), and the input token is user-selected. Any user picking or being routed through a fee-on-transfer token, or any scenario where the sweep's actual delivery is less than the balance read pre-sweep, triggers the miscrediting deterministically — no privileged actor or special timing is required.

### Recommendation
Mirror the corrected pattern already present in `evm/src/apps/IntentGatewayV2.sol`: snapshot the gateway's own balance (`address(this).balance` / `IERC20(token).balanceOf(address(this))`) immediately before invoking `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))`, then measure the actual delta afterward, and use that measured delta (capped/compared against `requiredAmount`, with excess emitted as `DustCollected`) as the value credited into `_orders[commitment][token]` and used for `reducedInputs`. Do not credit escrow based on a balance read before the sweep executes.

### Proof of Concept
1. User calls `placeOrder` with `order.predispatch.call` set to route the deposited native/ERC20 asset through the `CallDispatcher`, ending with the dispatcher holding a fee-on-transfer ERC20 token (`token`) with balance `B >= requiredAmount`.
2. In the loop at `evm/tron/contracts/apps/IntentGatewayV2.sol` lines 418–446, `balance = IERC20(token).balanceOf(dispatcher) = B`; since `B >= requiredAmount` the check passes, `dust = B - requiredAmount` is emitted, and `_orders[commitment][token] += reducedInputs[i].amount` is credited immediately.
3. At line 449, `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` executes `token.transfer(address(this), B)`. Because `token` charges a transfer fee, the gateway actually receives `B' < B` (potentially `B' < requiredAmount`).
4. The gateway's real token balance is now `B'`, but the escrow ledger `_orders[commitment][token]` records `reducedInputs[i].amount` (derived from the pre-transfer `requiredAmount`), which can exceed `B'`.
5. When this or other orders are later filled/cancelled and funds are paid out of the shared token balance according to the ledger, the gateway can be short of tokens, causing failed payouts or under-collateralized/unbacked claims for legitimate order participants.

Note: I was unable to fully verify, within the available tool budget, whether `ICallDispatcher.dispatch` (in `evm/src/utils/CallDispatcher.sol`) always reverts the entire batch on any individual sub-call failure. If it does revert atomically, the primary confirmed exploitation vector is the fee-on-transfer token path described above (which does not depend on the dispatch's failure semantics); if it does not revert atomically, the miscrediting risk is broader still since a partially-failed sweep would also go undetected.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-449)
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

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
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
