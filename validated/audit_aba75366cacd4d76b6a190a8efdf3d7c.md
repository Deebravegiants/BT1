## Title
Phantom escrow credit via unchecked ERC20 `transfer` return value in `IntentGatewayV2.placeOrder` predispatch sweep (Tron variant) - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron build of `IntentGatewayV2.placeOrder` credits escrow (`_orders[commitment][token]`) for predispatch-routed inputs *before* verifying that the token was actually delivered back to the gateway, and the delivery itself is performed through `CallDispatcher.dispatch`, which only checks that the low-level `.call` did not revert — it never inspects the ABI-encoded boolean return value of `IERC20.transfer`. A token whose `transfer` returns `false` instead of reverting on failure lets an attacker create escrow bookkeeping for tokens that were never actually received by the gateway contract, matching the report's core bug class ("some ERC20 tokens return false instead of revert ... protocol can open positions without funding").

### Finding Description
In the predispatch branch of `placeOrder`, the sweep-back transfer is built as raw calldata and routed through the untrusted-call executor: [1](#0-0) 

Crucially, `_orders[commitment][token] += reducedInputs[i].amount;` (line 441) happens *inside the same loop that builds `transferCalls`*, before `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` (line 449) is even executed. The escrow ledger is therefore incremented purely on the assumption that the subsequent `transfer` call will succeed.

That `transfer` call is executed by `CallDispatcher.dispatch`, which only asserts the low-level call did not revert: [2](#0-1) 

There is no decoding/validation of the `bool` return value. Standard-conforming ERC20 tokens that return `false` on failure (rather than reverting) — and, since order input tokens are attacker-supplied, a fully malicious/custom ERC20 an attacker deploys — can make this `transfer` a silent no-op: `success` is `true` (the call itself didn't revert), so `CallDispatcher` does not revert, and `placeOrder` proceeds having already credited `_orders[commitment][token]` with the full `reducedInputs[i].amount`, even though the gateway's actual token balance never increased.

This is a genuine regression relative to the non-Tron `evm/src/apps/IntentGatewayV2.sol`, which measures the *actual* balance delta after the sweep dispatch and reduces `order.inputs[i].amount` to the real received amount rather than trusting the transfer call blindly: [3](#0-2) 

The Tron variant has no equivalent post-dispatch balance check for the predispatch path, so the escrow map can become inflated relative to the gateway's real token holdings.

That escrow map is later paid out unconditionally on cancellation/refund via `IERC20.safeTransfer`, drawing from the contract's aggregate token balance (which is shared across all orders using the same token): [4](#0-3) 

### Impact Explanation
An attacker who places an order with a `predispatch.call`/`predispatch.assets` routing to a malicious ERC20 input token can obtain a fully-backed-looking escrow entry (`_orders[commitment][token]`) without the gateway contract ever actually holding those tokens. When that order is later cancelled/refunded (or otherwise settled against `_orders`), `_withdraw` transfers real tokens out of the contract's pooled balance of that token — balance that in practice is funded by other users' legitimately escrowed orders of the same token. This is a direct theft/drain of other users' escrowed funds and/or an unbacked escrow credit, i.e., concrete theft of funds reachable from a single unprivileged `placeOrder` transaction.

### Likelihood Explanation
`placeOrder` is a fully permissionless entry point, and the input token is attacker-controlled (any ERC20 address can be listed as an order input), so an attacker can deploy a purpose-built token whose `transfer()` returns `false` under attacker-chosen conditions instead of reverting. No privileged role, governance, or race condition is required — this is directly reachable by any user submitting a single transaction.

### Recommendation
- In `CallDispatcher.dispatch`, decode and validate ERC20 `transfer`/`transferFrom` return data (or require the caller to use `SafeERC20`-style calls) instead of only checking `success` of the raw `.call`.
- In `IntentGatewayV2.placeOrder` (Tron variant), mirror the non-Tron implementation's pattern: snapshot the gateway's token balance before the sweep dispatch and credit `_orders[commitment][token]` based on the *measured* balance delta after `ICallDispatcher(dispatcher).dispatch(...)` returns, rather than crediting escrow before the transfer is confirmed to have moved funds.

### Proof of Concept
1. Attacker deploys `MAL` ERC20 token whose `transfer(address,uint256)` always returns `false` (no revert) when the recipient is the `IntentGatewayV2` contract, but behaves normally otherwise (e.g., to pass any earlier checks).
2. Attacker calls `placeOrder` with `order.predispatch.call`/`assets` set up so that after predispatch execution, the `CallDispatcher` holds `balance >= requiredAmount` of `MAL` (attacker fully controls `MAL`, so this is trivial to arrange, e.g., mint to itself and transfer to the dispatcher via `predispatch.assets`).
3. `order.inputs[0].token = MAL`, `amount = requiredAmount`.
4. In `placeOrder`'s predispatch loop (`evm/tron/contracts/apps/IntentGatewayV2.sol:416-446`), `balance` check passes, `transferCalls[0]` is built to call `MAL.transfer(address(this), balance)`, and `_orders[commitment][MAL] += reducedInputs[0].amount` is executed unconditionally.
5. `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` executes `MAL.transfer(...)`, which returns `false` without reverting; `CallDispatcher` sees `success = true` and does not revert.
6. The gateway now shows `_orders[commitment][MAL] == reducedInputs[0].amount` even though its real `MAL` balance did not increase.
7. Attacker calls `cancelOrder`/triggers `_withdraw`, which calls `IERC20(MAL).safeTransfer(beneficiary, amount)` from the gateway's balance — draining `MAL` tokens that belong to other users' escrowed orders (or is undetectable dilution of pool solvency for that token). [1](#0-0) [2](#0-1) [4](#0-3)

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```
