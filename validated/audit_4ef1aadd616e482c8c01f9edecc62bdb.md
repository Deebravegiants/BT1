### Title
Missing Token Transfer Verification in `IntentGatewayV2.placeOrder` (Tron variant) predispatch sweep path credits escrow without verifying actual token receipt - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder`'s predispatch branch sweeps ERC20 tokens from the `CallDispatcher` back to the gateway using a low-level `IERC20.transfer` call routed through `CallDispatcher.dispatch`, but credits escrow (`_orders[commitment][token] += reducedInputs[i].amount`) unconditionally, without verifying that the tokens were actually received by the gateway. This mirrors the reported `Clearinghouse.lendToCooler` bug class: a token movement whose success is never checked before the contract's accounting assumes it happened.

### Finding Description
In `placeOrder`'s predispatch branch [1](#0-0) , for each ERC20 input the gateway builds a `Call` that invokes `IERC20.transfer(address(this), balance)` on the token, encoded via `abi.encodeWithSelector(IERC20.transfer.selector, ...)`, to be executed by the `CallDispatcher`. This call array is then executed with `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` [2](#0-1) .

`CallDispatcher.dispatch` only checks that the low-level `.call()` did not revert; it never decodes or checks the boolean return value of the ERC20 `transfer` call: `(bool success, bytes memory result) = to.call{value: call.value}(call.data); if (!success) revert CallFailed(to, result);` [3](#0-2) . For any ERC20 implementation that returns `false` on failure instead of reverting (non-standard/legacy tokens), the outer `.call()` succeeds (`success == true`) even though the token transfer logically failed and no balance moved.

Critically, immediately after building the sweep `Call[]`, the Tron variant increments escrow state directly from the expected/required amount — `_orders[commitment][token] += reducedInputs[i].amount;` [4](#0-3)  — **before** the sweep call is even dispatched, and with no post-transfer balance check on `address(this)`. Compare this to the non-Tron `IntentGatewayV2.sol` on EVM, which explicitly snapshots balances before the sweep and computes `received = IERC20(token).balanceOf(address(this)) - balancesBefore[i]`, mutating `order.inputs[i].amount` to the actually-received amount before crediting escrow [5](#0-4) . The Tron variant omits this verification entirely, so `_orders[commitment][token]` is credited with the full expected amount regardless of whether the underlying `IERC20.transfer` from the `CallDispatcher` to the gateway actually succeeded and moved funds.

### Impact Explanation
If the predispatch calldata swaps into (or the order specifies) a non-standard ERC20 token that silently returns `false` on transfer failure rather than reverting — or if the sweep transfer otherwise fails to deliver the full `balance` while `CallDispatcher`'s low-level call still reports `success == true` — the gateway credits `_orders[commitment][token]` with an amount of tokens it never actually holds. This creates unbacked escrow accounting: a phantom balance that can later be paid out to a solver via `_withdraw`'s `IERC20(token).safeTransfer(beneficiary, amount)` [6](#0-5) , draining real tokens belonging to other users' legitimately escrowed balances of that same token. This is a concrete theft/permanent-freezing-of-funds vector reachable from a single unprivileged `placeOrder` transaction with a crafted predispatch order using a non-reverting-on-failure ERC20.

### Likelihood Explanation
Exploitability depends on the existence of an ERC20 token in scope for the deployed gateway that returns `false` (rather than reverting) on a failed `transfer`. Many legacy/non-standard ERC20 tokens exhibit this behavior (this is exactly the risk `SafeERC20` is designed to guard against, and which the rest of the codebase consistently uses `safeTransferFrom`/`safeTransfer` for — except this specific sweep path, which is forced to use a raw low-level call because it is executed indirectly through `CallDispatcher`). Any user can trigger `placeOrder` with `predispatch.call` and `predispatch.assets` set, feeding an order whose `inputs` token is such a non-standard token. No relayer, prover, or privileged role involvement is required — it is directly reachable from a single submitted transaction.

### Recommendation
After `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` executes, snapshot `IERC20(token).balanceOf(address(this))` before and after the sweep (as already done in the non-Tron `IntentGatewayV2.sol`), and credit `_orders[commitment][token]` with the actually-received delta rather than the pre-computed `reducedInputs[i].amount`. Alternatively/additionally, have `CallDispatcher` decode and enforce the ERC20 boolean return value for calls targeting `transfer`/`transferFrom` selectors, or use `SafeERC20`-style checked-return semantics for any call whose success the caller's accounting depends on.

### Proof of Concept
1. Attacker (or any user) calls `placeOrder` on the Tron `IntentGatewayV2` with `order.predispatch.call` and `order.predispatch.assets` populated, and `order.inputs[0].token` set to a non-standard ERC20 `T` that returns `false` (instead of reverting) when its internal `transfer` logic fails (e.g., insufficient balance on the `CallDispatcher` after the predispatch calldata executes, due to a crafted predispatch call that drains `T` from the dispatcher before the sweep).
2. During predispatch processing, `balance = IERC20(token).balanceOf(dispatcher)` is checked against `requiredAmount` and passes at that point [7](#0-6) , but the attacker's `order.predispatch.call` (executed just before, at line 414) can itself manipulate `T`'s state (e.g., via a reentrant-like internal hook, or a token with transfer-restriction logic keyed on `msg.sender`/allowance state) so the subsequent `transfer` call from `CallDispatcher` to the gateway returns `false`.
3. `_orders[commitment][token] += reducedInputs[i].amount` executes unconditionally at line 441, crediting the escrow mapping with the full expected amount even though the sweep `Call` (dispatched afterward at line 449) delivered zero or partial tokens.
4. The order later gets filled/cancelled and `_withdraw` pays out `_orders[commitment][token]` in real `T` tokens to a beneficiary/solver, drawing down the gateway's actual `T` balance — which is backed by other users' legitimately escrowed `T` tokens — resulting in fund loss for those other users once the gateway's real balance is insufficient to cover all outstanding escrow claims.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L448-449)
```text
            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/src/utils/CallDispatcher.sol (L59-60)
```text
            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
```

**File:** evm/src/apps/IntentGatewayV2.sol (L289-311)
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

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
