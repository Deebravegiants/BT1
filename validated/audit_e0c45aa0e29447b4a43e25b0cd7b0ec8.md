### Title
Missing zero-amount validation combined with no reentrancy guard in Tron `IntentGatewayV2.placeOrder`'s predispatch path allows sweeping/misappropriating another order's escrow via the shared `CallDispatcher` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2.placeOrder` (`evm/tron/contracts/apps/IntentGatewayV2.sol:338-506`) omits two safety checks that exist in the canonical EVM implementation (`evm/src/apps/IntentGatewayV2.sol:194,242,264`): (1) a zero-amount check on `order.predispatch.assets[i].amount` / `order.inputs[i].amount`, and (2) the `nonReentrant` guard. Both are present on the canonical contract but absent on the Tron variant.

### Finding Description
In the canonical implementation, `placeOrder` is `nonReentrant` [1](#0-0)  and explicitly reverts on zero-amount predispatch assets and inputs before sweeping the `CallDispatcher`'s balance back to the gateway [2](#0-1) .

The Tron variant's `placeOrder` has neither guard:
- No `nonReentrant` modifier: [3](#0-2) 
- No zero-amount check on `order.predispatch.assets[i].amount` before funding the dispatcher: [4](#0-3) 
- No zero-amount check on `order.inputs[i].amount` in the sweep-back loop, where `requiredAmount` is used to determine how much of the dispatcher's *entire current balance* is treated as escrow vs. "dust": [5](#0-4) 

The `CallDispatcher` is a single shared, stateless-execution contract used by every order's predispatch phase — it just forwards arbitrary calls and holds transient balances [6](#0-5) . Because the sweep step reads `IERC20(token).balanceOf(dispatcher)` / `address(dispatcher).balance` — the dispatcher's *total* current balance, not an amount scoped to the current order — and computes `dust = balance - requiredAmount`, setting `requiredAmount = 0` (via `order.inputs[i].amount = 0`, unvalidated) makes the entire dispatcher balance for that token classified as "dust" and swept to the gateway contract, while `_orders[commitment][token] += reducedInputs[i].amount` credits nothing to the attacker's own commitment.

Combined with the missing `nonReentrant` guard, an attacker can craft `order.predispatch.call` to reenter `placeOrder` (or otherwise interleave transactions, since Tron has no atomic mempool ordering guarantee against a malicious relayer/miner) while a legitimate order's predispatch assets are sitting in the shared `CallDispatcher` mid-flight (funded but not yet swept back into that legitimate order's escrow). The attacker's own order specifies `amount = 0` for the matching input token, so the sweep-back logic scoops up the *victim's* funded balance from the dispatcher and routes it into the gateway as unlabeled "dust" (`DustCollected`) rather than crediting the victim's own `_orders[commitment][token]`. The victim's order then either fails to reach the required escrow to be filled, or the swept value is permanently reclassified as protocol-owned dust reachable only via the privileged `SweepDust` governance flow — a concrete loss/freezing of the victim's escrowed input tokens.

### Impact Explanation
This allows theft/permanent freezing of another user's escrowed input tokens routed through the shared `CallDispatcher` during the predispatch phase, and is triggerable by any unprivileged caller of `placeOrder`. The victim's funds end up either stuck as unattributed protocol dust (reclaimable only by governance via `SweepDust`) or simply missing from `_orders[commitment][token]`, meaning the order cannot be properly filled/redeemed for the amount the user actually paid.

### Likelihood Explanation
Requires the shared `CallDispatcher`/predispatch path to be in use (an optional order feature) and for an attacker to interleave/reenter around a victim's in-flight `placeOrder` call — feasible given the missing `nonReentrant` guard and the fact that Tron's transaction ordering can be influenced by relayers/attackers. This is a Medium-likelihood, targeted attack rather than something that fires automatically on every transaction, but it requires no special privileges to execute.

### Recommendation
- Add `nonReentrant` to Tron's `placeOrder`, matching the canonical EVM implementation.
- Add the missing zero-amount checks: `if (amount == 0) revert InvalidInput();` for `order.predispatch.assets[i].amount` and `if (order.inputs[i].amount == 0) revert InvalidInput();` for `order.inputs[i].amount`, matching `evm/src/apps/IntentGatewayV2.sol:242` and `:264`.
- Scope the dust calculation to a balance-delta measured before/after the predispatch call (as the canonical version does via `balancesBefore`), rather than trusting the dispatcher's absolute balance, so a shared/pooled dispatcher balance can never be misattributed to an unrelated order.

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` with a configured `_params.dispatcher` (shared `CallDispatcher`).
2. Victim calls `placeOrder` with `order.predispatch.call`/`order.predispatch.assets` set (non-zero amount), funding the shared `CallDispatcher` with token `T` before its own sweep-back step executes.
3. Attacker's crafted `order.predispatch.call` (executed via the same shared `CallDispatcher`) reenters `placeOrder` (no `nonReentrant` guard blocks this) with `order.inputs[i].token = T`, `order.inputs[i].amount = 0`, and empty/no-op `predispatch.assets`.
4. In the attacker's nested call, `requiredAmount = 0`, so `balance = IERC20(T).balanceOf(dispatcher)` (which now includes the victim's funded amount) is entirely computed as `dust` and swept via `transferCalls` to `address(this)` (the gateway), while `_orders[attackerCommitment][T] += 0` credits the attacker nothing but the tokens leave the dispatcher.
5. The victim's outer `placeOrder` call resumes, but the dispatcher balance it expected to sweep for its own escrow is now gone (already swept out by the reentrant attacker call), so the victim's own `_orders[victimCommitment][T]` under-credits or reverts on `InvalidInput`/`InsufficientNativeToken`, either freezing the victim's transaction/funds or lets an already-broadcast fill be under-collateralized.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-195)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();
```

**File:** evm/src/apps/IntentGatewayV2.sol (L241-264)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-338)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L393-411)
```text
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L417-446)
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

                unchecked {
                    ++i;
                }
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
