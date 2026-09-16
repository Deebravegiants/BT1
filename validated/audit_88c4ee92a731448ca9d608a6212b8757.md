### Title
Raw ERC20 `transfer()` call without return-value verification in IntentGatewayV2 predispatch sweep - (File: `evm/src/apps/IntentGatewayV2.sol`, `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2` consistently uses OpenZeppelin's `SafeERC20.safeTransferFrom`/`safeTransfer` everywhere it moves ERC20 tokens for orders [1](#0-0) , except in the predispatch "sweep" step, where it builds a raw, unchecked ERC20 `transfer` call via `abi.encodeWithSelector(IERC20.transfer.selector, ...)` and routes it through `CallDispatcher.dispatch`, which only checks the low-level `bool success` of the `.call()` and never inspects/validates the ERC20 return data.

### Finding Description
When an order includes a `predispatch.call`/`predispatch.assets` (used to run arbitrary calldata before pulling the declared inputs), `IntentGatewayV2` moves tokens through the `CallDispatcher`. To sweep tokens back from the dispatcher to the gateway it constructs: [2](#0-1) 
and executes it with: [3](#0-2) 

`CallDispatcher.dispatch` only reverts if the raw `.call()` itself reverts (`success == false`); it never checks the returned `bool` from a token's `transfer()` function. This is exactly the ERC20 non-compliance class described in the report: some tokens (e.g. tokens forked from old USDT-style implementations) return `false` on a failed transfer instead of reverting. Against such a token, `to.call(...)` succeeds (`success == true`) even though no tokens moved, so `CallDispatcher` does not revert, while `IntentGatewayV2`'s own `IERC20.transfer.selector` construction never checks the encoded return value either — unlike the rest of the file, which uses `SafeERC20` and would have reverted safely.

The same unchecked-selector pattern is duplicated in the Tron fork of the gateway. [4](#0-3) 

### Impact Explanation
After the unchecked sweep, the code measures received amounts via a balance-diff and folds any shortfall into `order.inputs[i].amount`, then still records `_orders[commitment][token] += reducedInputs[i].amount` using the pre-mutation fee-reduced amount rather than the tokens actually captured. [5](#0-4)  If a non-compliant token's `transfer()` silently no-ops (returns `false`, doesn't revert) during the sweep, the gateway can escrow/commit to an order input balance it never actually received, letting the order proceed as if fully funded. This creates an accounting mismatch between the gateway's actual token holdings and its escrow ledger, which can be exploited to have a solver fill (and be paid for) an order whose input was never truly deposited — i.e., a theft/insolvency vector against the intents escrow, matching the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Reachable by any unprivileged user submitting an order with a `predispatch` call, provided the input token is a non-standard ERC20 that returns `false` instead of reverting on failed transfers (a documented, non-hypothetical class of tokens, as cited by the report). No special privileges are required — only crafting an order with such a token and appropriate predispatch calldata.

### Recommendation
Replace the raw `abi.encodeWithSelector(IERC20.transfer.selector, ...)` construction in the predispatch sweep of both `evm/src/apps/IntentGatewayV2.sol` and `evm/tron/contracts/apps/IntentGatewayV2.sol` with `SafeERC20.safeTransfer`, consistent with the rest of the contract, or explicitly decode and validate the returned boolean inside `CallDispatcher.dispatch` for calls targeting ERC20 `transfer`/`transferFrom` selectors.

### Proof of Concept
1. Attacker deploys/uses a non-standard ERC20 token `T` whose `transfer()` returns `false` (no revert) when the sender lacks sufficient allowance/balance state internally (or is paused for that account) rather than reverting.
2. Attacker submits an order via `IntentGatewayV2` with `order.predispatch.call` and `order.predispatch.assets` set so `T` ends up custodied by the `CallDispatcher`.
3. The gateway invokes the sweep `Call` `{to: T, data: encodeWithSelector(transfer.selector, address(this), balance)}` via `ICallDispatcher.dispatch`.
4. `T.transfer` executes but returns `false` under a crafted internal condition; `CallDispatcher` sees `success == true` (the low-level call didn't revert) and does not revert.
5. Gateway's balance-diff detects a shortfall and reduces `order.inputs[i].amount`, but the escrow bookkeeping at `_orders[commitment][token] += reducedInputs[i].amount` still uses the originally quoted (pre-shortfall) amount, over-crediting the order relative to actual tokens held.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L250-251)
```text
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L273-282)
```text
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
