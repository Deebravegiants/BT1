### Title
Intent order escrow can be credited without matching token transfer in predispatch sweep due to unchecked low-level `transfer` return value - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`, `evm/src/utils/CallDispatcher.sol`)

### Summary
`IntentGatewayV2.placeOrder`'s predispatch flow sweeps input tokens from the `CallDispatcher`-owned intermediate account back into the gateway using a raw `IERC20.transfer.selector` call routed through `CallDispatcher.dispatch`. `CallDispatcher.dispatch` only checks that the low-level `.call` did not revert, never inspecting/decoding the ERC20 boolean return value [1](#0-0) . In the tron variant of `IntentGatewayV2.sol`, the escrow amount `_orders[commitment][token]` is credited with `reducedInputs[i].amount` *before* the sweep call is even dispatched, and there is no post-transfer balance check to confirm the gateway actually received the tokens [2](#0-1) . This mirrors the Cooler `roll()` bug: a non-reverting-on-failure ERC20 token (one that returns `false` rather than reverting) lets the "transfer" succeed at the call level while moving zero tokens, yet the protocol still records full escrow credit as if the transfer succeeded.

### Finding Description
In the predispatch branch of `placeOrder` (tron variant), the flow is:
1. User-supplied assets are sent to `dispatcher` via `safeTransferFrom` (safe) [3](#0-2) .
2. The dispatcher executes an arbitrary `order.predispatch.call` [4](#0-3) .
3. The gateway builds `transferCalls` that use the *raw* `IERC20.transfer.selector` (not `safeTransfer`) to move `balance` of each input token from `dispatcher` back to `address(this)` [5](#0-4) .
4. Escrow is credited with `reducedInputs[i].amount` immediately after building the call list — **before** the transfer call is dispatched, and with no subsequent verification that the gateway's balance actually increased [6](#0-5) .
5. `ICallDispatcher(dispatcher).dispatch(...)` executes the sweep, but `CallDispatcher.dispatch` treats the call as successful as long as it doesn't revert — it never checks the boolean return data of `transfer()` [7](#0-6) .

Because many real-world ERC20 tokens (and any token deliberately crafted this way) return `false` on a failed transfer instead of reverting, step 5's `.call` reports `success == true` even though no tokens moved. The escrow ledger (`_orders[commitment][token]`) is therefore inflated relative to the gateway's actual token holdings — exactly the "loan rolled over for no additional collateral" pattern from the Cooler report, where a call that silently fails is treated as having succeeded and a debit/credit accounting entry is made anyway.

Notably, the sibling non-tron contract (`evm/src/apps/IntentGatewayV2.sol`) fixes this class of issue for its predispatch sweep by snapshotting balances before/after and using the *actual received* amount for escrow and commitment computation [8](#0-7) , confirming this balance-diff safeguard is the intended mitigation — but it is absent from the tron variant's predispatch escrow path.

### Impact Explanation
An attacker (any unprivileged user placing an order with `predispatch.call`/`predispatch.assets` using or targeting a return-false-on-failure ERC20) can cause the gateway to credit escrow for tokens that were never actually deposited into the contract. Later, when a solver fills the order or the order is redeemed/cancelled, the protocol will attempt to pay out from escrow accounting that is not backed by real token balance, leading to insolvency of the gateway's token reserves — i.e., other users'/solvers' legitimately escrowed funds can be drained to cover the shortfall, a direct fund-loss/insolvency condition.

### Likelihood Explanation
Reachable directly and solely via a single `placeOrder` transaction from any unprivileged caller who supplies `predispatch.call`/`predispatch.assets`, using a token that follows the "return false rather than revert" ERC20 pattern (common among older/non-standard-but-widely-used tokens). No special privileges, governance, or multi-step social engineering are required — only a specific but realistic token behavior plus attacker-controlled predispatch calldata that can make the dispatcher's balance insufficient at sweep time.

### Recommendation
- In `CallDispatcher.dispatch`, when a call target is a token-transfer style operation, decode and validate the boolean return value (or require callers to use `SafeERC20`-encoded calldata that reverts on failure).
- In `IntentGatewayV2.sol` (tron variant), mirror the balance-diff pattern already used in the main EVM contract: snapshot `balanceOf(address(this))` before the sweep dispatch, and only credit escrow with `balanceOf(address(this)) - before`, reverting or reducing escrow if the received amount is less than required.

### Proof of Concept
1. Deploy the tron `IntentGatewayV2` with a token `T` that implements `transfer` returning `false` on insufficient balance instead of reverting.
2. Attacker calls `placeOrder` with `predispatch.call` designed so that, at the time the sweep `transferCalls` executes, the `dispatcher`'s balance of `T` is drained (e.g., via a nested call in `predispatch.call` that itself withdraws `T` from `dispatcher` to elsewhere, exploiting reentry/ordering within the same predispatch execution) or by initially depositing less than `requiredAmount` while still passing checks that only compare pre-sweep balance.
3. The sweep's `transfer(address(this), balance)` call executes through `CallDispatcher.dispatch`; token `T` returns `false` (transfer fails silently) but the low-level `.call` reports `success = true`, so `CallDispatcher` does not revert.
4. `_orders[commitment][token] += reducedInputs[i].amount` was already set (line 441) regardless, so escrow now reflects tokens the gateway never received.
5. When the order is later filled/redeemed, the solver or refund path pays out based on the inflated `_orders` entry, draining real token balance belonging to other escrowed orders. [2](#0-1) [7](#0-6)

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L392-411)
```text
            // Transfer all predispatch assets to the call dispatcher
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L413-414)
```text
            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

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
