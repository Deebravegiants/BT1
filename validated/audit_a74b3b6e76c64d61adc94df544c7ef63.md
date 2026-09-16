Found a valid analog: the Tron `IntentGatewayV2.placeOrder` never refunds unspent native (`msgValue`) sent by the user, unlike the main EVM `IntentGatewayV2.sol` version which explicitly does so.

### Title
Unrefunded excess native token permanently stuck in Tron IntentGatewayV2.placeOrder - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`placeOrder` in the Tron variant of `IntentGatewayV2` is `payable` and tracks a local `msgValue` counter that is decremented as native ETH is consumed for order inputs and, optionally, for a Uniswap V2 swap to cover `order.fees`. Unlike the canonical EVM implementation of the same function, the Tron contract never sends back any `msgValue` left over after these deductions.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `placeOrder` (starting around line 338) computes `msgValue = msg.value` and decrements it as native-token inputs are consumed [1](#0-0) , and again optionally when swapping native token for the fee token via `swapETHForExactTokens` [2](#0-1) . After this, the function proceeds straight to emitting `OrderPlaced` and returns, with no code path that forwards the remaining `msgValue` back to `msg.sender` [3](#0-2) .

This is the exact bug class described in the report: an optional/conditional operation (here, the native→fee-token swap, analogous to Swivel's optional PT swap) consumes only part of the funds a caller supplied, and the leftover amount is silently retained by the contract instead of being returned to the caller.

Contrast this with the maintained EVM version of the same function, `evm/src/apps/IntentGatewayV2.sol`, which explicitly refunds any unspent native token to the user after the same fee-swap logic: `if (msgValue > 0) { _sendValue(msg.sender, msgValue); }` [4](#0-3) . The Tron contract lacks this final refund step entirely — it is a near-exact structural duplicate of the EVM `placeOrder` (same fee-token swap block, same `msgValue` accounting) [5](#0-4)  but is missing the corresponding sweep-back call.

### Impact Explanation
Any user calling `placeOrder` on the Tron deployment with `msg.value` exceeding what is needed for native-token order inputs plus the exact-output fee swap (`swapETHForExactTokens` only spends up to `order.fees` worth of native token, refunding nothing itself back to the gateway caller) will have the excess permanently locked in the `IntentGatewayV2` contract. This occurs in the normal, single-transaction, unprivileged `placeOrder` flow — not an edge case requiring misconfiguration — matching the report's criterion of "not a user mistake" since overpaying native token for a swap that has slippage/price uncertainty is a normal usage pattern. Funds can only be recovered via the privileged `SweepDust` / withdrawal path triggered by Hyperbridge, which is operationally infeasible at scale, exactly mirroring the original report's assessment of admin-`withdraw()`-only recovery. This constitutes a genuine freezing-of-funds vulnerability reachable by any user submitting a single transaction.

### Likelihood Explanation
Likelihood is high: any caller who does not compute the exact native-token amount needed (e.g., due to a live swap quote fluctuating between quote time and transaction execution) will overpay, and the excess is trapped every time this path executes. No adversarial conditions are required.

### Recommendation
Add the same excess-refund step present in the EVM version of `placeOrder`: after the fee-handling block, check `if (msgValue > 0)` and send the leftover native token back to `msg.sender`, matching `evm/src/apps/IntentGatewayV2.sol` lines 394-397.

### Proof of Concept
1. User calls `placeOrder{value: X}(order, graffiti)` on the Tron `IntentGatewayV2`, where `order.inputs` includes only ERC20 tokens (no native-token input) and `order.fees > 0`.
2. `msgValue` starts at `X` and is untouched by the ERC20-only input loop [6](#0-5) .
3. The fee swap branch executes `swapETHForExactTokens{value: msgValue}(order.fees, ...)`, which only spends enough native token to receive exactly `order.fees` in `feeToken` — the router keeps sending the full `msgValue` as `msg.value` but Uniswap's `swapETHForExactTokens` refunds unspent ETH to `msg.sender` of that call, which is the `IntentGatewayV2` contract itself, not the original user [7](#0-6) .
4. Because `placeOrder` never checks or forwards any leftover native balance to `msg.sender` afterward, that refunded ETH (the difference between `X` and the amount actually needed for the swap) remains stuck in the `IntentGatewayV2` contract balance, inaccessible to the user through any public function.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-349)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-506)
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
