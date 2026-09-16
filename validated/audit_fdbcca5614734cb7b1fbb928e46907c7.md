### Title
Stranded native ETH in Tron `IntentGatewayV2.placeOrder()` fee-swap path — leftover funds never refunded - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` performs a `swapETHForExactTokens` to pay `order.fees` in the fee token when the user sends native ETH, but — unlike the canonical EVM implementation — it never deducts the amount actually spent from `msgValue`, and it never refunds the leftover `msgValue` to `msg.sender` at the end of the function. Any native ETH sent by the user beyond what the swap consumes is permanently stranded in the contract.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the fee-escrow branch of `placeOrder` is: [1](#0-0) 

This calls `IUniswapV2Router02.swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)`, sending the *entire remaining* `msgValue` to the router even though the router only needs to spend just enough ETH to buy the exact `order.fees` amount of the fee token. The router refunds the unspent ETH back to the caller — which is the `IntentGatewayV2` contract itself (`address(this)` initiated the call) — but the function:
1. Never captures the returned `amounts[0]` (actual ETH spent) to subtract from `msgValue`.
2. Never checks or sweeps a leftover `msgValue` back to `msg.sender` after this block, unlike the sibling code path.

By contrast, the canonical EVM implementation of the same logic correctly tracks and refunds unspent ETH: [2](#0-1) 

Here `msgValue -= amounts[0];` is applied and any positive residual `msgValue` is sent back to `msg.sender` via `_sendValue`. The Tron contract's `placeOrder` has no equivalent refund statement anywhere after the fee block or at the end of the function (confirmed by reading through line 506, where the function ends with the `OrderPlaced` emit and no ETH refund).

### Impact Explanation
Because the excess ETH sent for the fee swap lands back on the `IntentGatewayV2` contract (not the user) and is never accounted for in any escrow/dust bookkeeping (`_orders[...]` or `DustCollected`), it accumulates as unbacked native balance in the contract with no code path to withdraw or credit it to anyone. This is a permanent freezing/loss of user funds: every `placeOrder` call that pays fees via native ETH (any amount above the exact swap cost, which is the normal/expected case since users must overestimate the ETH needed for slippage) leaves residual ETH stuck. Given the contract exposes no admin sweep function for stray native balance visible in this flow, the funds are effectively lost to depositing users, and since anyone can call `placeOrder` this is reachable by any unprivileged user, i.e., permanent freezing of funds.

### Likelihood Explanation
High likelihood: this occurs on every ordinary `placeOrder` call where `order.fees > 0` and the caller pays with native ETH (which the code explicitly supports as the alternative to `feeToken` transfer). Users must send `msg.value` greater than or equal to the fee-token cost, and any slippage buffer beyond the exact swap amount is stranded automatically without any attacker action required.

### Recommendation
Mirror the EVM contract's fix in the Tron variant: capture `amounts` from `swapETHForExactTokens`, subtract the spent amount from `msgValue`, and refund any residual `msgValue` to `msg.sender` at the end of `placeOrder` (as done in `evm/src/apps/IntentGatewayV2.sol` lines 383-397).

### Proof of Concept
1. User calls `IntentGatewayV2.placeOrder{value: 5 ether}(order, graffiti)` on the Tron deployment, with `order.fees = 1e18` (fee token) and an ERC20 input (no native input), so all `msg.value` reaches the fee-swap branch as `msgValue`.
2. `swapETHForExactTokens{value: 5 ether}(1e18, path, address(this), ...)` executes; the router only needs a small fraction of the 5 ETH to buy exactly `order.fees` fee tokens and refunds the remainder (~4.9+ ETH) to `address(this)` (the `IntentGatewayV2` contract).
3. `placeOrder` returns without ever decrementing `msgValue` or sending anything back to `msg.sender`.
4. The ~4.9 ETH now sits in the `IntentGatewayV2` contract's balance, uncredited to any escrow, and unrecoverable by the user who sent it — repeat across users to accumulate stranded, un-withdrawable ETH in the contract.

### Citations

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-397)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
