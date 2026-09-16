### Title
Unguarded `balanceOf(dispatcher)` reads in the predispatch escrow sweep let an order steal residual/dust tokens from the shared dispatcher - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.placeOrder`'s predispatch flow on the Tron variant computes the amount to escrow for an order's inputs from a raw, unnetted `balanceOf`/native-`balance` read on the shared, persistent `_params.dispatcher` contract instead of measuring the delta actually produced by that order's own predispatch call. This is the same bug class as the reported "utilization rate manipulation": an externally-readable balance that any party can inflate is trusted verbatim inside protocol accounting.

### Finding Description
In the predispatch branch of `placeOrder`, tokens are transferred to a shared `dispatcher` address (`_params.dispatcher` - a single persistent contract reused by every order, not deployed fresh per order), an attacker-controlled arbitrary call is executed on it, and then the sweep step reads: [1](#0-0) 

```solidity
uint256 requiredAmount = order.inputs[i].amount;
uint256 balance;
if (token == address(0)) {
    balance = address(dispatcher).balance;
    ...
} else {
    balance = IERC20(token).balanceOf(dispatcher);
    if (balance < requiredAmount) revert InvalidInput();
    ...
}
uint256 dust = balance - requiredAmount;
if (dust > 0) emit DustCollected(token, dust);
_orders[commitment][token] += reducedInputs[i].amount;
```

`balance` is the *entire current* balance sitting on the shared `dispatcher`, not the amount this order's own `predispatch.assets` transfer or `predispatch.call` produced. There is also no `amount == 0` guard on `order.predispatch.assets[i].amount` in this contract (unlike the non-predispatch branch a few lines below), so an attacker can submit a predispatch step that contributes nothing of value, execute a no-op call, and rely purely on whatever balance already happens to sit on the shared `dispatcher` (leftover dust from another order's incomplete/interleaved predispatch flow, or tokens someone else donated/transferred there) to satisfy `balance >= requiredAmount`.

The fixed main EVM contract avoids exactly this by snapshotting balances before the sweep and crediting only the measured delta: [2](#0-1) 

The Tron contract has no equivalent `balancesBefore` snapshot / delta measurement, so it inherited the vulnerable pattern the main contract was patched away from.

### Impact Explanation
Because `_orders[commitment][token] += reducedInputs[i].amount` credits the caller's own declared `order.inputs[i].amount` (which the caller freely chooses) as long as the dispatcher's *raw* balance happens to cover it, an attacker can place an order whose escrow is backed by tokens they never contributed — tokens belonging to another pending/legitimate predispatch flow on the shared dispatcher, or tokens simply sent to the dispatcher by anyone. A solver later fills this order and is paid real output on the destination chain against a source-chain escrow that the placer never actually funded, resulting in concrete theft of escrowed funds and/or fund loss for the party whose residual balance was swept away.

### Likelihood Explanation
The `dispatcher` address is a protocol parameter shared by every `placeOrder` predispatch call, and `order.predispatch.call` is fully attacker-supplied calldata executed by `ICallDispatcher(dispatcher).dispatch(...)`. Any attacker can submit a `placeOrder` transaction with a low/zero predispatch-asset amount whenever residual balance exists on the dispatcher (which can be induced deliberately via a preceding transaction, a directly-sent token transfer, or via reentrancy through the attacker-controlled predispatch call itself). No special privilege is required — this is reachable from a single unprivileged `placeOrder` transaction.

### Recommendation
Mirror the fix already applied to `evm/src/apps/IntentGatewayV2.sol`: snapshot `balanceOf(dispatcher)` / `address(dispatcher).balance` (and the gateway's own balance) before the predispatch call and sweep, and credit escrow (and dust) only with the measured delta actually produced by this order's own predispatch step, never the dispatcher's raw absolute balance. Also add the missing `amount == 0` revert check on `order.predispatch.assets[i].amount` for consistency with the non-predispatch branch.

### Proof of Concept
1. Governance/deploy sets a single shared `_params.dispatcher` contract used by all `placeOrder` predispatch flows (as in `evm/tron/contracts/apps/IntentGatewayV2.sol`).
2. User A places a legitimate order with a predispatch call that (due to attacker-crafted reentrancy, or simply because it is mid-execution) leaves `X` tokens of `TOKEN` sitting on `dispatcher` before its own sweep runs, or an attacker directly `transfer()`s `X` tokens of `TOKEN` to the known `dispatcher` address.
3. Attacker calls `placeOrder` with `order.inputs[0] = {token: TOKEN, amount: X}` and a no-op `predispatch.call`/zero-amount `predispatch.assets` (no `amount==0` guard exists to stop this).
4. The sweep step reads `balance = IERC20(TOKEN).balanceOf(dispatcher) == X`, satisfies `balance >= requiredAmount`, sweeps `X` tokens into the gateway, and credits `_orders[commitment][TOKEN] += X` to the attacker's order — funded entirely by tokens the attacker never supplied.
5. A solver fills the attacker's order and is paid the destination-chain output against this bogus escrow, while the original depositor (User A or whoever the swept tokens belonged to) loses their funds.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L260-299)
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
```
