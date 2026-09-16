## Title
`placeOrder` in Tron `IntentGatewayV2` never refunds unused `msg.value`, permanently locking excess/misdirected native tokens - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` accepts `msg.value` to fund native-token inputs and/or to auto-swap into the protocol fee token, but unlike the canonical EVM implementation it contains no logic to return any leftover, unspent native value to the caller. Any ETH/TRX sent in excess of what the function actually consumes is stranded in the contract forever.

### Finding Description
`placeOrder` tracks a local `msgValue` counter that is decremented as native inputs are consumed [1](#0-0)  and, when `order.fees > 0`, is optionally spent via `swapETHForExactTokens{value: msgValue}` to buy the exact fee-token amount needed [2](#0-1) . After that fee block, the function proceeds directly to emitting `OrderPlaced` and returns [3](#0-2)  — there is no step that checks `msgValue` for a nonzero remainder and returns it to `msg.sender`.

This is in direct contrast to the primary EVM implementation of the same contract, which explicitly refunds any unspent native value at the end of `placeOrder`:
```solidity
// Refund any unspent native tokens to the user.
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
``` [4](#0-3) 

Two concrete loss scenarios in the Tron version:
1. All order inputs are ERC20 (`token != address(0)`) and `order.fees == 0`, but the caller mistakenly attaches `msg.value > 0`. `msgValue` is never touched by the input loop [5](#0-4)  and the fee block is skipped entirely, so the full `msg.value` sits in the contract with no accounting or recovery path.
2. `order.fees > 0` and the caller supplies more native value than the exact amount `swapETHForExactTokens` needs. Uniswap's `swapETHForExactTokens` refunds the leftover ETH to `msg.sender` of that call, which is the `IntentGatewayV2` contract itself (not the original user), since the contract calls the router directly rather than forwarding the user as caller [6](#0-5) . That returned dust is likewise never forwarded back to `msg.sender` of `placeOrder`.

### Impact Explanation
Users placing intent orders via the Tron `IntentGatewayV2` who overestimate the native fee needed, or who mistakenly attach `msg.value` while paying for inputs entirely in ERC20, permanently lose that value — it becomes unrecoverable protocol-held ETH/TRX with no withdrawal path exposed to depositors. Given `placeOrder` is a primary, unprivileged, user-facing entry point reachable by any solver/end user submitting a single transaction, and given the fee-estimation UX (users are expected to send fee amounts computed off-chain, which are inherently approximate for native payments per the project's own documentation warning about slippage/estimation), overpayment is a routine, not edge-case, occurrence. This is a direct, permanent freezing of user funds.

### Likelihood Explanation
High likelihood: any user paying the intent-order transaction fee in native token, or an integrator that forgets to zero out `msg.value` for ERC20-only orders, will trigger this on essentially every over-estimated fee payment — no attacker action is required, only normal usage of the documented "native token payment" flow.

### Recommendation
Mirror the EVM implementation: after all native-value consumption in `placeOrder` (inputs, predispatch, and fee swap), check the remaining `msgValue` and, if nonzero, return it to `msg.sender` via a safe value transfer before emitting `OrderPlaced`, exactly as done in `evm/src/apps/IntentGatewayV2.sol` lines 394-397.

### Proof of Concept
1. Caller builds an `Order` whose `order.inputs` are all ERC20 tokens (`token != address(0)`) and `order.fees == 0`.
2. Caller calls `placeOrder(order, graffiti)` with `msg.value = 1 ether` attached by mistake (e.g., wallet UI defaulting to sending fee estimate as native value).
3. Inside `placeOrder`, the ERC20-only branch of the input loop `IERC20(token).safeTransferFrom(...)` never decrements `msgValue` [7](#0-6) ; since `order.fees == 0`, the fee-swap block is skipped entirely.
4. Function completes, emits `OrderPlaced`, and returns — the 1 ether sent with the call remains in the `IntentGatewayV2` contract balance with no corresponding entry in `_orders[...]` and no code path to withdraw it back to the caller.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L388-410)
```text
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L490-506)
```text
        emit OrderPlaced({
            user: order.user,
            source: order.source,
            destination: order.destination,
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
