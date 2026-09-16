### Title
Unrefunded excess `msg.value` is permanently stranded in `IntentGatewayV2.placeOrder` on the Tron deployment - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder` on the Tron contract variant accepts `msg.value` to pay for either native-token order inputs or (via Uniswap) the order's solver/relayer fees, but unlike the canonical EVM implementation of the same function, it never refunds any leftover, unused native token to the caller after escrow and fee handling complete.

### Finding Description
`placeOrder` tracks a running `msgValue` variable that is decremented as native-token inputs are consumed and, if `order.fees > 0`, is passed entirely into `IUniswapV2Router02.swapETHForExactTokens{value: msgValue}(...)`: [1](#0-0) 

Two related loss paths exist:

1. **No fee owed at all, but `msg.value` was sent.** If `order.fees == 0` (or the user funds all inputs with ERC20 via `safeTransferFrom` while still attaching `msg.value`), the `if (order.fees > 0)` block at line 471 is skipped entirely, and `msgValue` — still holding the full unspent `msg.value` — is never used or returned. The function then proceeds straight to emitting `OrderPlaced` and returns, with no refund path: [2](#0-1) [3](#0-2) 

2. **Fee is owed and paid with native token, but the swap overpays.** `swapETHForExactTokens` only consumes exactly the ETH-equivalent needed to buy `order.fees` amount of fee tokens; the router automatically refunds any unused ETH to the caller, which is the `IntentGatewayV2` contract itself (`msg.sender` of the swap call), not the end user. The Tron code discards the return value of `swapETHForExactTokens` (`amounts[0]`), never decrements `msgValue` by the amount actually spent, and never forwards the router's refund back to the user: [4](#0-3) 

Contrast this with the canonical (non-Tron) EVM implementation of the identical function, which explicitly captures the swap's `amounts[0]`, decrements `msgValue`, and refunds any remainder to `msg.sender`: [5](#0-4) 

This is the same bug class as the referenced report: a `payable` entry point accepts `msg.value` for a purpose, but a code path exists (ERC20-only funding, or fee overpayment) where that value is neither consumed nor returned, and is permanently retained by the contract.

### Impact Explanation
Any user (unprivileged; a normal order placer / funder) who calls `placeOrder` on the Tron `IntentGatewayV2` and either (a) attaches native token while funding all inputs with ERC20/fee-token, or (b) overestimates the native amount needed to cover `order.fees` via the Uniswap swap, permanently loses that excess ETH/TRX. There is no `receive`/refund mechanism reachable by the depositor to recover it after the fact — the funds sit in the contract's balance with no per-order accounting tying them back to the sender (unlike escrowed `_orders[commitment][token]` balances, which are recoverable via `cancelOrder`/`withdraw`). This is a direct, permanent loss of user funds triggered by a single ordinary transaction, satisfying "concrete... permanent freezing of funds."

### Likelihood Explanation
Likelihood is fairly high in practice: any front-end or integrator that (like the SDK's `quoteNative`-style estimation pattern used elsewhere in the repo) computes a native-fee quote with a safety buffer (as documented elsewhere, e.g. 1% buffers) and sends that buffered amount as `msg.value` will trigger case (2) on every order that pays fees natively, since `swapETHForExactTokens` will always leave some dust unrefunded to the user. Case (1) additionally triggers whenever a caller supplies `msg.value` by mistake (e.g., wallet default behavior, or a caller who intends to self-relay/pay fees in fee-token but still attaches value) while using ERC20 inputs.

### Recommendation
Mirror the mainline EVM implementation: capture the actual ETH consumed by `swapETHForExactTokens` and refund the difference, and add an unconditional refund of any remaining `msgValue` at the end of `placeOrder` regardless of whether `order.fees > 0`:

```solidity
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
    (bool sent,) = msg.sender.call{value: msgValue}("");
    if (!sent) revert InsufficientNativeToken();
}
```

### Proof of Concept
1. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs` consisting solely of an ERC20 token (`token != address(0)`), and `order.fees == 0`, but attaches `msg.value = 1 TRX` by mistake (e.g., wallet UI default).
2. Execution enters the `else` branch at line 450, transfers the ERC20 input via `safeTransferFrom`; `msgValue` remains `1 TRX`, untouched.
3. `order.fees == 0`, so the `if (order.fees > 0)` block at line 471 is skipped.
4. The function emits `OrderPlaced` and returns; the `1 TRX` sent as `msg.value` is now part of the contract's balance with no accounting entry crediting it back to the user.
5. There is no function callable by the user to reclaim this stranded native balance — it is permanently lost (or effectively donated to whatever privileged sweep mechanism the protocol may later add for its own benefit, not the user's). [6](#0-5) [7](#0-6)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-506)
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
