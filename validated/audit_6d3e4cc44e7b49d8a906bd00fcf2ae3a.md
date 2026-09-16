### Title
Unchecked ERC20 `transfer` return value in `CallDispatcher` lets `IntentGatewayV2.placeOrder`'s predispatch-sweep credit unbacked escrow - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` computes the escrowed amount for a predispatch-swept token from the *pre-transfer* dispatcher balance and the order's declared input amount, then only afterwards executes the actual `IERC20.transfer()` call through `CallDispatcher`. `CallDispatcher.dispatch` only checks that the low-level `call` did not revert — it never inspects the boolean return value of the ERC20 `transfer`. If the swept token's `transfer()` returns `false` on failure instead of reverting (a common non-standard-ERC20 behavior, the exact bug class flagged in the referenced report), the gateway credits `_orders[commitment][token]` with tokens it never actually received.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, inside `placeOrder`'s predispatch branch: [1](#0-0) 

the flow is:
1. `balance = IERC20(token).balanceOf(dispatcher)` is snapshotted **before** any transfer.
2. A `Call` is built encoding `IERC20.transfer(address(this), balance)`, to be executed later via `ICallDispatcher(dispatcher).dispatch(...)`.
3. `_orders[commitment][token] += reducedInputs[i].amount` is credited **immediately**, using the order's declared/expected amount — not any post-transfer balance check.
4. Only after the full loop does `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` actually run the transfer.

`CallDispatcher.dispatch` executes each call and only reverts if the raw call itself reverts: [2](#0-1) 

It never decodes/validates the ABI-encoded boolean return of `IERC20.transfer`. Per the referenced report's bug class, ERC20 tokens that return `false` on failure instead of reverting will make this low-level call "succeed" (`success == true`) while transferring zero or fewer tokens than expected.

This contrasts with the mainline (non-Tron) `IntentGatewayV2.sol`, where the equivalent predispatch-sweep code measures the *actual* balance delta after the dispatch call and sets `order.inputs[i].amount` to the real amount received: [3](#0-2) 

The Tron variant lacks this balance-verification step for the escrow credit (`_orders[commitment][token] += reducedInputs[i].amount`), relying instead on the unchecked low-level call succeeding.

### Impact Explanation
If the input token used in a predispatch-and-sweep order silently fails to transfer (returns `false` without reverting) during the sweep from the `CallDispatcher` back to the gateway, `_orders[commitment][token]` is credited with tokens the gateway does not actually hold. When a solver later fills this order and claims the escrowed input via `_withdraw`/`onAccept`, the payout is satisfied from the gateway's real balance — which is actually funded by *other users'* escrowed orders. This is a concrete freezing/theft-of-funds vector: it creates an accounting shortfall that eventually causes some other legitimate order's escrow withdrawal to fail or drains funds meant for other users, since `_orders` mapping no longer reflects real token backing.

### Likelihood Explanation
Reachable by any unprivileged user calling `placeOrder` with a `predispatch.call`/`predispatch.assets` set and a token contract they control or select (attacker can use a custom ERC20 with non-reverting failure semantics, or exploit an existing non-standard token listed for use in the gateway). No privileged role or governance action required — a single transaction from an ordinary intent placer triggers the vulnerable path.

### Recommendation
Mirror the mainline EVM contract's approach: after `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` runs, measure the actual balance change on the gateway (`IERC20(token).balanceOf(address(this))` before/after) and credit `_orders[commitment][token]` with the real received amount rather than the pre-computed `reducedInputs[i].amount`. Additionally, harden `CallDispatcher.dispatch` (or a wrapper) to validate ERC20 return data for `transfer`/`transferFrom` selectors (e.g., via `SafeERC20`-style decoding) so that a `false` return is treated as a failure and reverts, consistent with how `safeTransferFrom`/`safeTransfer` are used elsewhere in the codebase.

### Proof of Concept
1. Deploy a malicious/non-standard ERC20 `EvilToken` whose `transfer()` returns `false` (instead of reverting) whenever called by `CallDispatcher` under a chosen condition (e.g., always returns `false` for calls from a specific dispatcher address, or simulate insufficient balance without reverting).
2. Attacker calls `placeOrder` with `order.predispatch.assets` containing `EvilToken`, and `order.inputs` also specifying `EvilToken` as the input to be swept back to the gateway.
3. During execution: `balance = IERC20(EvilToken).balanceOf(dispatcher)` is read; `_orders[commitment][EvilToken] += reducedInputs[i].amount` is credited; then `ICallDispatcher(dispatcher).dispatch(...)` calls `EvilToken.transfer(gateway, balance)`, which returns `false` but does not revert — `CallDispatcher` sees `success == true` and does not revert the batch.
4. The gateway's actual `EvilToken` balance is unchanged (0 received), yet `_orders[commitment][EvilToken]` reflects the full expected amount.
5. A colluding/attacker-controlled solver fills the order, and `_withdraw` pays out `EvilToken` from the gateway's actual holdings — which are backed only by other legitimate users' escrowed `EvilToken` balances (or reverts, freezing those other orders' funds), depending on the gateway's real token holdings at withdrawal time.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
```text
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
