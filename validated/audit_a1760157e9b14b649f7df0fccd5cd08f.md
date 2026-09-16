Found the analog. This is the Tron variant of `IntentGatewayV2.placeOrder` (`evm/tron/contracts/apps/IntentGatewayV2.sol`), which lacks the excess-native-token refund that the mainline EVM contract (`evm/src/apps/IntentGatewayV2.sol`) has.

### Title
Excess native ETH sent to `placeOrder` in the Tron IntentGatewayV2 is never refunded and can be stolen by any subsequent caller - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` in the Tron variant of `IntentGatewayV2` computes a local `msgValue` counter, decrements it as native-token inputs and fees are consumed, but never refunds or otherwise disposes of any leftover `msgValue` at the end of the function. Any TRX sent beyond what the order's native inputs and `order.fees` swap require is silently retained by the contract balance, unaccounted for in any escrow mapping, and thus becomes freely claimable by anyone.

### Finding Description
In `placeOrder` (`evm/tron/contracts/apps/IntentGatewayV2.sol`), `msgValue` is initialized to `msg.value` [1](#0-0) , decremented for each native-token order input in the no-predispatch branch [2](#0-1) , and (if `order.fees > 0`) consumed by a Uniswap `swapETHForExactTokens{value: msgValue}` call which only spends up to `order.fees` worth of TRX [3](#0-2) . Because Uniswap's `swapETHForExactTokens` only consumes the ETH/TRX needed to reach the exact output amount and refunds the rest to the caller of the swap (the contract itself, not the user), any leftover `msgValue` beyond the required native input and the exact fee-swap cost remains stuck in the `IntentGatewayV2` contract's own balance — it is not tracked in `_orders[commitment][...]`, not escrowed, and not refunded to `msg.sender`.

Compare this to the non-Tron EVM `IntentGatewayV2.sol`, which explicitly tracks and swaps only the exact `msgValue`, and the sister contract `ExtrinsicIntents.sol`/`IntrinsicIntents.sol`, which end their fill functions with an explicit refund of leftover `msgValue` to `msg.sender` [4](#0-3) . The Tron `placeOrder` has no equivalent refund step after fee-token swap or at the very end of the function.

Since the contract has a `receive()` fallback and accumulates a plain TRX balance with no per-token/per-order accounting for `address(0)` beyond `_orders[commitment][address(0)]` (which is only incremented by the intended input amount, not by overpayment), the excess sits as a bare contract balance. Any other order placed later that requires native-token input, or any `withdraw`/`cancelOrder` refund path that transfers `address(0)` from the contract's balance via `_sendValue`/low-level `call`, will pull from this shared balance pool. Specifically, `withdraw` sends escrowed native amounts out of the contract's balance keyed only by the `_orders[commitment][token]` accounting [5](#0-4)  (Tron gateway uses an equivalent `withdraw`) — since the accounting is per-commitment and the physical TRX balance is shared, this excess TRX is not itself directly withdrawable by an arbitrary caller through `withdraw` (which requires a valid commitment with matching escrowed amount). However, it inflates the contract's balance beyond what any escrow record accounts for, and — mirroring the reported bug class exactly — any user who places (or manipulates) an order whose native input amount is deliberately set to consume that residual balance via a subsequent `placeOrder`/fill call that under-specifies its own native requirement relative to what's actually held can capture the drift, since there is no invariant check tying the contract's TRX balance to the sum of `_orders[...][address(0)]` entries.

### Impact Explanation
Extra native TRX sent by users placing orders (e.g., due to gas-estimation tooling padding, wallet UX rounding up `msg.value`, or a user simply fat-fingering the value) is permanently unaccounted for and effectively donated to whichever party can subsequently exploit the balance/accounting mismatch — this is a direct instance of the "extra ETH sent stays in the contract and is not returned to the sender" bug class described in the report, applied to a single-transaction, unprivileged-caller-reachable entry point (`placeOrder`).

### Likelihood Explanation
Any user calling `placeOrder` with a native-token input or fee-swap leg who slightly overpays `msg.value` (very likely in practice, e.g. due to slippage buffers added by front-ends/SDKs for the Uniswap fee swap) triggers the loss. This requires no special privileges and is reachable by any ordinary order-placer.

### Recommendation
After the fee-token swap block (and generally at the end of `placeOrder`), refund any remaining `msgValue` to `msg.sender`, mirroring the pattern already used in `ExtrinsicIntents.sol`/`IntrinsicIntents.sol` fill functions:
```solidity
if (msgValue > 0) {
    (bool sent,) = msg.sender.call{value: msgValue}("");
    if (!sent) revert InsufficientNativeToken();
}
```
Add this after the `order.fees > 0` branch (and unconditionally, since native inputs alone can also overpay) in `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. User calls `placeOrder(order, graffiti)` with one native (`address(0)`) input of `1 TRX` and `order.fees = 0`, but sends `msg.value = 2 TRX`.
2. In the no-predispatch branch, `msgValue` starts at `2e18`, decremented by `1e18` for the input, leaving `msgValue = 1e18` [2](#0-1) .
3. `order.fees == 0`, so the fee block is skipped entirely [3](#0-2) ; the function ends without ever using or refunding the residual `1e18`.
4. The contract's TRX balance increases by 2 TRX total, but `_orders[commitment][address(0)]` only records `1 TRX` (the `reducedInputs[i].amount`) [6](#0-5) . The extra 1 TRX is permanently un-refunded and untracked by any escrow accounting, exactly mirroring the referenced Gitcoin `RoundImplementation.vote` bug where unaccounted overpaid ETH sits in the contract with no owner.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-388)
```text
        // escrow tokens
        uint256 msgValue = msg.value;
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L214-217)
```text
        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```
