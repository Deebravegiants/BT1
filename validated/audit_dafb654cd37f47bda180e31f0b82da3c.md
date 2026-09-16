## Analysis

The reported bug class — unchecked ERC20 `transfer`/`transferFrom` return values allowing "phantom" transfers on non-standard tokens — has a concrete analog in the Tron variant of `IntentGatewayV2`.

### Root cause

In the mainline EVM `IntentGatewayV2.sol`, after sweeping predispatch-call output tokens from the `CallDispatcher` back to the gateway, the contract verifies the actual amount received by diffing `balanceOf(address(this))` before/after the sweep, and mutates `order.inputs[i].amount` to the real received amount: [1](#0-0) 

The **Tron** version of the same contract omits this post-transfer balance verification. It checks the dispatcher's pre-transfer balance, issues a raw `IERC20.transfer.selector` call via `CallDispatcher.dispatch`, and then unconditionally credits escrow using the *pre-computed* `reducedInputs[i].amount` — never confirming that the gateway (`address(this)`) actually received the tokens: [2](#0-1) 

The sweep call is dispatched through `CallDispatcher.dispatch`, which only checks that the low-level `call` did not revert (`success`) — it never decodes/validates the ABI-encoded boolean return value of `transfer()`: [3](#0-2) 

### Impact path

For a token that returns `false` on a failed `transfer()` instead of reverting (the exact bug class cited in the report), the low-level call inside `CallDispatcher.dispatch` succeeds (`success == true`) even though no tokens moved. The Tron `IntentGatewayV2` then credits `_orders[commitment][token] += reducedInputs[i].amount` with phantom collateral it never actually received: [4](#0-3) 

This escrow entry is later paid out via `_withdraw`, which uses `safeTransfer` against the gateway's *pooled* token balance (shared across all orders of that token), not an isolated per-order balance: [5](#0-4) 

Because the gateway's balance of that token is a shared pool, an attacker's phantom escrow credit can be paid out of other legitimate users' real deposits of the same token — this is the same "solver/lender loses funds because collateral was never actually held" pattern as the original Cooler.sol report, reachable via a single unprivileged `placeOrder` call with predispatch calldata.

### Title
Unchecked ERC20 transfer return value in Tron `IntentGatewayV2` predispatch sweep allows uncollateralized escrow credit - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron `IntentGatewayV2.placeOrder` predispatch flow sweeps tokens from the `CallDispatcher` back to the gateway using a raw, unchecked `IERC20.transfer` call dispatched via `CallDispatcher.dispatch`, which only checks that the call did not revert, not that the token's boolean return value was `true`. Unlike the mainline EVM `IntentGatewayV2.sol`, the Tron variant never verifies the gateway's actual post-transfer balance before crediting escrow.

### Finding Description
`CallDispatcher.dispatch` (`evm/src/utils/CallDispatcher.sol:44-62`) treats a call as successful purely based on `success` from the low-level `.call()`, ignoring the ABI-decoded return data. When the predispatch branch of `placeOrder` in the Tron `IntentGatewayV2` builds a sweep transaction (`abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)`), a non-standard or malicious ERC20 that returns `false` on failure (rather than reverting) will let this call "succeed" without moving any tokens. The code proceeds to credit `_orders[commitment][token] += reducedInputs[i].amount` unconditionally, without re-checking `IERC20(token).balanceOf(address(this))` after the sweep, unlike the equivalent EVM mainline logic which explicitly performs this balance-diff check.

### Impact Explanation
Because `_orders[commitment][token]` tracks escrow from a shared pool of the gateway's token balance (not per-order segregated funds), a user can register a phantom escrow entry for a token they never actually deposited into the gateway. Any subsequent legitimate withdrawal (`_withdraw`, `safeTransfer`) against that phantom entry drains real balance contributed by other users' orders of the same token — resulting in direct theft/insolvency of the escrow pool. This is a High severity, unbacked-fund-crediting bug matching "forged message delivery / unauthorized app action" and "concrete theft of funds" criteria.

### Likelihood Explanation
Exploitable via a single unprivileged `placeOrder` transaction using an attacker-deployed (or any non-standard) ERC20 as a predispatch/input asset. No special privileges, governance, or multi-step social engineering required — only requires that the token contract violates the strict ERC20 revert-on-failure convention, a documented and known class of tokens.

### Recommendation
In the Tron `IntentGatewayV2` predispatch branch, after dispatching the sweep transfer calls, recompute the actual received amount via a `balanceOf(address(this))` diff (as already done in the mainline EVM `IntentGatewayV2.sol`) and use that verified amount — not the pre-computed `reducedInputs[i].amount` — when crediting `_orders[commitment][token]`. Additionally, harden `CallDispatcher.dispatch` (or the sweep-call construction) to decode and require `true` from ERC20 `transfer`/`transferFrom` return data, or replace raw selector encoding with `SafeERC20.safeTransfer` semantics.

### Proof of Concept
1. Attacker deploys a malicious ERC20 `EvilToken` whose `transfer()` returns `false` under attacker-controlled conditions instead of reverting.
2. Attacker calls Tron `IntentGatewayV2.placeOrder` with a predispatch asset/call in `EvilToken`, arranging for the `CallDispatcher` to hold `EvilToken` balance ≥ `requiredAmount` (satisfying the pre-transfer `balanceOf(dispatcher)` check) while the actual `transfer(address(this), balance)` call returns `false`.
3. `CallDispatcher.dispatch` sees `success == true` (call didn't revert) and does not revert, per `evm/src/utils/CallDispatcher.sol:59-60`.
4. `IntentGatewayV2` credits `_orders[commitment][EvilToken] += reducedInputs[i].amount` at `evm/tron/contracts/apps/IntentGatewayV2.sol:441`, despite never having received the tokens.
5. If any other legitimate user has previously deposited real `EvilToken`-type or a shared-pool token into the gateway via other orders, attacker's order (once filled/cancelled and withdrawn) triggers `_withdraw`'s `safeTransfer` at `evm/src/apps/intentsv2/IntentsBase.sol:468`, paying the attacker from the shared pool funded by other users' genuine deposits.

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
