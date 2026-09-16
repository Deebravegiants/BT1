Confirmed: in the Tron `IntentGatewayV2.placeOrder` predispatch branch, the credit to escrow (`_orders[commitment][token] += reducedInputs[i].amount`) at [1](#0-0)  happens *before* the actual sweep transfer is executed and is based solely on the pre-transfer `balance = IERC20(token).balanceOf(dispatcher)` check at [2](#0-1) , never verified against the post-transfer balance. The sweep itself is executed as a raw low-level call encoded with `IERC20.transfer.selector` and routed through `CallDispatcher.dispatch`, which only checks that the external call did not revert — it never decodes/validates the boolean return value of `transfer()`, as seen in [3](#0-2) .

### Title
Escrow credited on unchecked `transfer()` return value in `IntentGatewayV2.placeOrder` predispatch path allows phantom escrow accounting - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
When an order includes a `predispatch` call, `placeOrder` sweeps `order.inputs` tokens from the `dispatcher` contract back to the gateway using a raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` call dispatched through `CallDispatcher`. `CallDispatcher.dispatch` only reverts if the low-level `.call` itself reverts; it does not check the ERC20 `transfer` return value [4](#0-3) . `placeOrder` then unconditionally credits `_orders[commitment][token] += reducedInputs[i].amount` based on the dispatcher's balance measured *before* the sweep, without re-checking the gateway's actual received balance afterward [1](#0-0) .

### Finding Description
For an ERC20 implementation that returns `false` on failed transfer instead of reverting (a well-known non-standard-but-common behavior, e.g. old/deflationary/pausable/blacklist tokens), the sweep call `to.call(data)` in `CallDispatcher.dispatch` succeeds (`success == true`) even though no tokens actually moved to the gateway. `placeOrder` has no post-transfer balance check in this branch (unlike the mainline EVM `IntentGatewayV2.sol`, which explicitly re-measures `IERC20(token).balanceOf(address(this))` before/after the sweep and sets `order.inputs[i].amount` to the actual delta, see [5](#0-4) ). Instead, the Tron variant credits escrow purely from the pre-sweep `balanceOf(dispatcher)` check, so `_orders[commitment][token]` is incremented by `reducedInputs[i].amount` regardless of whether the tokens ever reached the gateway.

### Impact Explanation
Once the phantom escrow entry exists, downstream logic (order fill/cancel/refund flows keyed on `_orders[commitment][token]`) treats the gateway as holding real backing for that amount. This can lead to: (a) permanent freezing/DoS of legitimate fills or refunds when the gateway later attempts to move tokens it doesn't actually hold and reverts, blocking the commitment path entirely, or (b) if any code path pays out from aggregate token balances rather than per-order accounting, draining balances backed by other users' genuinely escrowed funds. Either outcome is a fund-safety issue reachable from a single unprivileged `placeOrder` transaction using an attacker-chosen `predispatch.call` and token address.

### Likelihood Explanation
`placeOrder` and the `predispatch` mechanism (custom `dispatcher`/`predispatch.call`/`predispatch.assets`) are fully attacker-controlled inputs from any unprivileged caller; the only requirement is supplying a token contract for `order.inputs[i].token` that returns `false` rather than reverting on transfer failure (easily attacker-deployed, or exploitable against any already-integrated non-reverting ERC20). No special privileges or state are required beyond crafting the order and a compatible token/dispatcher call.

### Recommendation
Replace the raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` sweep with `SafeERC20.safeTransfer`/`safeTransferFrom` (as already used elsewhere in the same file, e.g. lines 405, 459), or — matching the mainline EVM `IntentGatewayV2.sol` mitigation — measure the gateway's actual token balance before and after the sweep and use that delta (capped at `requiredAmount`) when crediting `_orders[commitment][token]`, instead of crediting from the pre-sweep dispatcher balance unconditionally.

### Proof of Concept
1. Attacker deploys a token `EvilToken` whose `transfer()` always returns `false` without reverting (compiles to standard ERC20 interface but violates the revert-on-failure assumption).
2. Attacker calls `placeOrder` with `order.predispatch.call` set to a no-op/self-serving call and `order.inputs[0].token = EvilToken`, `order.inputs[0].amount = X`, ensuring `IERC20(EvilToken).balanceOf(dispatcher) >= X` is satisfied (e.g., attacker funds the dispatcher with `X` `EvilToken` balance via `balanceOf` manipulation logic in the token, without any real transferable value).
3. `placeOrder` executes: pre-sweep `balance` check passes at [6](#0-5) ; `_orders[commitment][EvilToken] += reducedInputs[0].amount` is credited at line 441.
4. `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` executes the sweep; `EvilToken.transfer()` returns `false`, `CallDispatcher` sees `success == true` (call didn't revert) and does not revert.
5. Gateway's actual `EvilToken` balance is unchanged (0 received), yet `_orders[commitment][EvilToken]` reflects `X` tokens escrowed — a phantom escrow entry with no backing funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L427-435)
```text
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L437-446)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L291-306)
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
```
