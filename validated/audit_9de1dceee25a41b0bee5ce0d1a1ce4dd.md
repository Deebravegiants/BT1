## Analysis

The report's root cause — sizing a transfer by reading the contract's aggregate `balanceOf()` instead of tracking an exact, per-operation amount — has a direct analog in Hyperbridge's intent settlement path on the Tron/EVM IntentGatewayV2 predispatch flow.

### Title
Shared CallDispatcher Balance Swept via `balanceOf()` Misattributes Foreign Funds as Protocol Dust in `placeOrder` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the predispatch branch of `placeOrder`, the amount swept from the shared `CallDispatcher` back into the gateway — and the amount classified as "protocol dust" — is derived from `IERC20(token).balanceOf(dispatcher)`, the dispatcher's entire token balance, rather than the specific amount attributable to the current order.

### Finding Description
`placeOrder` computes the sweep amount as the dispatcher's raw balance and treats anything above the order's `requiredAmount` as dust:
<cite repo="AYontt/hyperbridge--024" path="evm/tron/contracts/apps/IntentGatewayV2.sol" start="416="441" end="441" /> [1](#0-0) 

```solidity
for (uint256 i; i < inputsLen;) {
    address token = address(uint160(uint256(order.inputs[i].token)));
    uint256 requiredAmount = order.inputs[i].amount;
    uint256 balance;
    ...
    balance = IERC20(token).balanceOf(dispatcher);
    if (balance < requiredAmount) revert InvalidInput();
    transferCalls[i] = Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)});
    ...
    uint256 dust = balance - requiredAmount;
    if (dust > 0) emit DustCollected(token, dust);
    _orders[commitment][token] += reducedInputs[i].amount;
    ...
}
```

`_params.dispatcher` is a single shared `CallDispatcher` contract used across every `placeOrder`/`fillOrder`/`_execute` call in the protocol, and `order.predispatch.call` executes arbitrary attacker-supplied calldata through it (`ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`) immediately before this balance read. Any token residue sitting on the dispatcher that is not attributable to the current order — leftover from a prior order's predispatch leg, dust from another user's fee-on-transfer token, or funds routed there in the same transaction by the arbitrary `predispatch.call` itself — is swept in full and the surplus above `requiredAmount` is unilaterally reclassified as protocol dust (`DustCollected`), rather than being returned to its rightful depositor. This is exactly the WIchiFarm bug class: sizing a transfer/accounting event from `balanceOf()` of a shared pool instead of a precisely tracked, order-scoped delta. The updated mainline `evm/src/apps/IntentGatewayV2.sol` fixed this by snapshotting balances before/after and computing `received` as an exact delta: [2](#0-1) 
but the Tron fork at `evm/tron/contracts/apps/IntentGatewayV2.sol` retains the vulnerable raw-`balanceOf()` sweep.

### Impact Explanation
Dust collected this way is only recoverable through the governance-only `SweepDust` path to a beneficiary chosen by governance, not the original depositor: [3](#0-2) 
So any unrelated tokens transiently present on the shared dispatcher are permanently diverted from their owner into protocol dust, and the escrow recorded (`reducedInputs[i].amount`) never accounts for them — a concrete loss of user funds via unauthorized reassignment, without requiring any privileged actor.

### Likelihood Explanation
The dispatcher is shared infrastructure and `predispatch.call` is fully attacker-controlled calldata executed via `dispatch()` right before the vulnerable balance read, giving any user placing an order a direct lever to interact with (and potentially leave/read) balances on the same dispatcher contract that other in-flight or preceding orders use. No special privileges are needed — a single `placeOrder` call with a crafted `predispatch` is sufficient to trigger the flawed accounting.

### Recommendation
Replace the `balanceOf()`-based sweep with an exact delta measurement (as already done in the non-Tron `IntentGatewayV2.sol`): snapshot the dispatcher's/gateway's balance immediately before the predispatch call and again after the sweep, and use `after - before` as both the transferred amount and the basis for dust/escrow accounting, never the dispatcher's absolute balance.

### Proof of Concept
1. User A calls `placeOrder` with a `predispatch.call` that, via the shared dispatcher, leaves 100 units of Token X sitting on `dispatcher` (e.g., an intermediate step deposits to the dispatcher but the call reverts partway, or a fee-on-transfer/rebasing token leaves residue), while `order.inputs[0].amount` (Token X) is 10.
2. User B's subsequent `placeOrder` (same or later transaction) for the same token, with `requiredAmount = 5`, reads `balance = IERC20(token).balanceOf(dispatcher)`, which now includes A's stranded 100 units plus B's own transferred amount.
3. The full `balance` is swept to the gateway; `dust = balance - requiredAmount` (which includes A's 100 units) is emitted as `DustCollected` and becomes claimable only by governance via `SweepDust`, while B's order escrow only records `reducedInputs[0].amount` — A's funds are never returned to A.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L417-441)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-306)
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
```
