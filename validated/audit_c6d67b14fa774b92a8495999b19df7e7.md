### Title
Unrefunded native-token overpayment in Tron `IntentGatewayV2.placeOrder` permanently strands user funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` swaps any supplied `msg.value` for the exact fee-token amount needed to cover `order.fees` via `swapETHForExactTokens`, but — unlike the canonical EVM implementation — never refunds the native-token remainder to the caller after escrowing inputs and fees. Any leftover `msgValue` is silently retained by the contract with no accounting or recovery path for the user, so overpaying (a near-certain outcome given the two-transaction quote→submit flow used by callers) causes a real, permanent loss of user funds. This mirrors the underlying bug class in the Livepeer report: a payable "fee-covering" call path where the amount of native value supplied vs. what is actually consumed is not properly reconciled, and the mismatch (excess this time, rather than shortfall) results in silently lost funds rather than a safe revert or full refund.

### Finding Description
`placeOrder` accepts `msg.value` to optionally cover `order.fees` via a Uniswap swap: [1](#0-0) 

After escrowing inputs (which, for the native-input branch, decrements `msgValue` by exactly the amount consumed as order input) and swapping for the fee token (which consumes only `amounts[0] <= msgValue`, per `swapETHForExactTokens` semantics — see `IUniswapV2Router02` usage elsewhere in the repo), any positive remainder of `msgValue` is never returned to `msg.sender`. The function proceeds directly to `emit OrderPlaced(...)` and returns.

Compare this to the canonical EVM `IntentGatewayV2.placeOrder`, which performs the identical escrow/fee-swap sequence but explicitly refunds the leftover value: [2](#0-1) 

```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
    order.fees, path, address(this), block.timestamp
);
msgValue -= amounts[0];
...
// Refund any unspent native tokens to the user.
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
```

The Tron contract's `placeOrder` (lines 471–506) has no equivalent `_sendValue(msg.sender, msgValue)` call after the fee block, and `msgValue` is a local variable that is simply discarded once the function returns — the ETH/TRX it represents stays trapped in the contract's balance with no bookkeeping (`_orders[commitment][address(0)]` is not credited for it, and it is not emitted as `DustCollected`).

### Impact Explanation
Because the SDK/off-chain flow quotes `order.fees` and its native-token equivalent (`nativeValue`) in a separate step before submitting `placeOrder`, and because Uniswap pricing can move between the quote and the transaction, users are expected to send a native value that at least covers, and typically slightly exceeds, the exact fee-swap requirement (the EVM-side refund logic exists precisely to handle this expected overpayment safely). On Tron, that same expected overpayment is not returned: user funds sent as `msg.value` beyond what the fee swap actually consumes are permanently and irrecoverably lost to the contract with no owner/admin sweep path credited to them specifically. This is a direct, unconditional loss of user native-token funds on every `placeOrder` call where `msg.value` exceeds the exact underlying swap cost — which is the normal case, not an edge case.

### Likelihood Explanation
This is not a low-probability attack path — it is the default operational outcome for any legitimate user who follows the documented native-fee-payment flow (quote a `nativeValue`, then submit `placeOrder{value: nativeValue}` or more), since the exact on-chain swap cost will essentially never equal the off-chain quoted value precisely. Every such transaction on the Tron deployment silently forfeits the unspent remainder. No malicious actor or special conditions are required to trigger the loss.

### Recommendation
Add the same unspent-native-token refund used in the canonical EVM `IntentGatewayV2.placeOrder` to the Tron variant: track the running `msgValue` through both the input-escrow and fee-swap paths, and call `_sendValue(msg.sender, msgValue)` (or equivalent) for any remainder before returning from `placeOrder`.

### Proof of Concept
1. User calls `quote`/off-chain estimation and determines `nativeValue` for `order.fees`.
2. User calls `IntentGatewayV2(tron).placeOrder{value: nativeValue}(order, graffiti)` where `order.inputs` are ERC20 (no native input consumption), so `msgValue` inside the function equals `nativeValue`.
3. Inside `placeOrder`, `swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` spends only `amounts[0] < msgValue` (the actual current on-chain swap price), leaving `msgValue - amounts[0] > 0` unaccounted.
4. The function reaches `emit OrderPlaced(...)` and returns without refunding the leftover value — see `evm/tron/contracts/apps/IntentGatewayV2.sol` lines 471–506, which contain no refund call, unlike lines 394–397 of `evm/src/apps/IntentGatewayV2.sol`.
5. The leftover TRX/native value remains in the contract balance permanently, not credited to any escrow slot the user can later withdraw.

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
