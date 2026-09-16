### Title
Overpaid native ETH in `IntentGatewayV2.placeOrder` (Tron) is never refunded and becomes permanently stuck - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron port of `IntentGatewayV2` accepts native ETH for order inputs and for the solver fee swap in `placeOrder`, but — unlike the canonical EVM implementation — it never refunds any unspent `msg.value` left over after those transfers. Any excess ETH sent by a user is silently retained by the contract with no accounting, no dust-tracking event, and no on-chain path to recover it, permanently freezing the overpaid funds.

### Finding Description
`placeOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol` tracks a running `msgValue` local variable as it consumes native ETH for predispatch assets, order inputs, and the fee-token swap: [1](#0-0) [2](#0-1) [3](#0-2) 

At every point where native ETH is consumed (`msgValue -= amount`), the function subtracts the required amount and moves on. The function ends at `emit OrderPlaced(...)` with no check of whether `msgValue > 0` remains, and no transfer back to `msg.sender`.

This is a direct behavioral regression from the canonical EVM `IntentGatewayV2.sol`, which explicitly refunds unspent value after the identical fee-swap logic: [4](#0-3) 

The Tron variant is missing this "Refund any unspent native tokens to the user" step entirely. Any ETH sent in excess of the exact input + fee-swap requirement (e.g. a user overestimating the amount needed to cover Uniswap slippage for the `swapETHForExactTokens{value: msgValue}(order.fees, ...)` fee purchase, or simply padding the value for safety) is absorbed into the contract's balance with no bookkeeping.

Critically, this leftover ETH is not even tracked as protocol "dust" — `DustCollected` events are only emitted for the protocol-fee portion deducted from `order.inputs`, not for stray `msg.value`. The only fund-recovery mechanism in the contract, `SweepDust` (handled in `onAccept`), requires a cross-chain governance-authorized message specifying an exact `token`/`amount`/`beneficiary`; since the overpayment is never recorded anywhere, governance has no way to know how much is owed to which user, and even if swept, it would go to an arbitrary beneficiary chosen by the sweep request rather than back to the original overpaying user.

### Impact Explanation
Any unprivileged user placing an order with native ETH via this Tron `IntentGatewayV2` deployment can have a portion of their submitted ETH permanently locked in the contract with no path to recovery, matching the "permanent freezing of funds" impact class from the original report. Given the fee-swap step consumes ETH through a Uniswap router where the amount consumed depends on live pool pricing (`swapETHForExactTokens`), users routinely cannot predict the exact ETH required and will send a buffer amount, guaranteeing this leftover-refund scenario is a routine occurrence rather than an edge case.

### Likelihood Explanation
High. Every `placeOrder` call using native ETH for inputs and/or `order.fees` (the standard SDK flow instructs users to pad `nativeValue` for the fee swap; the canonical EVM contract's own test suite validates that unused value must be refunded) will trip this path whenever the value provided exceeds the exact on-chain requirement, which is the normal, expected caller behavior, not an adversarial one.

### Recommendation
Mirror the canonical EVM `IntentGatewayV2.placeOrder` behavior: after all native-token consumption in `placeOrder` (predispatch, escrow, and fee swap), check `if (msgValue > 0)` and refund the remainder to `msg.sender` via a low-level call, exactly as done in `evm/src/apps/IntentGatewayV2.sol` lines 394-397. Apply the same audit to any other payable entry points in the Tron contract that consume partial `msg.value` (e.g., ensure `cancelOrder`'s dispatch paths do not similarly strand excess value).

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a Uniswap V2 router with non-trivial fee-token/WETH price.
2. Call `placeOrder{value: X}(order, graffiti)` where `order.inputs[0]` is a native-ETH input of amount `A`, and `order.fees = F` (fee-token amount), sending `X = A + B` where `B` is intentionally larger than the ETH actually required to swap for `F` fee tokens (e.g., pad for slippage).
3. Trace execution: `msgValue` starts at `X`; `msgValue -= A` for the input leg; the fee-swap branch executes `swapETHForExactTokens{value: msgValue}(F, ...)`, which only consumes the router-determined amount `amounts[0]` and returns leftover ETH to the caller (the *Uniswap wrapper's* internal refund) — but the Tron `placeOrder` code does **not** capture that returned value or track it in `msgValue`, and does not refund any of the original padding `B` overshoot back to `msg.sender`.
4. `emit OrderPlaced(...)` fires and the function returns successfully.
5. Check `address(intentGateway).balance` — it now holds the unrefunded overpayment permanently, verifiable against `user.balance` decreasing by more than `A` (input) plus the actual fee-swap cost.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-411)
```text
        // escrow tokens
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
