### Title
Excess native ETH sent to `placeOrder` is permanently trapped in the Tron `IntentGatewayV2` contract - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron port of `IntentGatewayV2.placeOrder` accepts `msg.value` to cover native-token order inputs and, optionally, a native→fee-token swap for `order.fees`. Unlike the canonical EVM implementation, it never refunds any native token left over after these two consumption paths, so a user who overpays with ETH/TRX permanently loses the surplus.

### Finding Description
`placeOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol` tracks a running `msgValue` variable that is decremented as native-token order inputs are escrowed [1](#0-0) , and, if `order.fees > 0`, is fully passed into `swapETHForExactTokens{value: msgValue}(...)` to buy the exact `order.fees` amount of fee tokens [2](#0-1) . The Uniswap router only consumes what is needed for `amountOut = order.fees` and — depending on the router implementation — may retain or return the unused ETH to the caller of the swap (this contract), not to the end user. After this block, the function immediately emits `OrderPlaced` and returns; there is no `msgValue -= amounts[0]` bookkeeping and, critically, no final "refund any unspent native tokens to the user" step.

This is the same bug class as the reported Aave issue: a function is designed to consume a native-token payment in parts, but the code path that should return/forward the remainder is missing, so ether that legitimately belongs to the caller is not accounted for and cannot be recovered by the caller.

The sibling, actively-maintained EVM contract explicitly fixes this by tracking `amounts[0]` returned from the swap and sweeping any remainder back to `msg.sender`: [3](#0-2) 
The Tron variant, `evm/tron/contracts/apps/IntentGatewayV2.sol`, lacks this final refund block entirely (confirmed by reading through the end of its `placeOrder` function without any `_sendValue`/refund logic being invoked before `OrderPlaced` is emitted) [4](#0-3) .

Overpayment is a realistic, unprivileged user action: any caller who does not compute the exact native fee-swap amount off-chain (e.g., using a slightly generous `msg.value` to tolerate slippage/price movement in `swapETHForExactTokens`, mirroring the documented native-fee flow described for the EVM gateway) will send more native token than is consumed [5](#0-4) .

### Impact Explanation
Any unspent native token (TRX/ETH) sent with `placeOrder` becomes stuck in the `IntentGatewayV2` contract with no code path to retrieve it — it is not credited to any order's escrow (`_orders[commitment][...]`), not tracked as `TRANSACTION_FEES`, and not returned to the sender. This constitutes a permanent freezing/loss of user funds for every order placed with even a marginal native-token overpayment, satisfying the "permanent freezing of funds" impact class.

### Likelihood Explanation
Likelihood is high: overpaying `msg.value` for a swap-based fee payment is an ordinary, expected client behavior (buffering against price movement/slippage on `swapETHForExactTokens`), and the contract provides no built-in protection or sweep mechanism. No privileged role or unusual conditions are required — a single `placeOrder` call with `order.fees > 0` and `msg.value` exceeding the amount consumed by the swap is sufficient.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: capture the actual amount spent by `swapETHForExactTokens` (`amounts[0]`), subtract it from `msgValue`, and add an explicit "refund any unspent native tokens to the user" transfer at the end of `placeOrder` (and audit any other native-token-consuming entry points in the Tron contract, e.g. `fillOrder`/`cancelOrder`, for the same missing-refund pattern).

### Proof of Concept
1. User calls `placeOrder{value: X}(order, ...)` on the Tron `IntentGatewayV2` where `order.fees > 0` and all `order.inputs` are ERC20 (no native input legs), so the entire `msgValue = X` is available for the fee swap.
2. Set `X` deliberately higher than the ETH needed to buy `order.fees` fee tokens via `swapETHForExactTokens` (e.g., `X = 5 ether` while the swap only needs `0.01 ether`, analogous to the EVM test `testPlaceOrder_FeeSwap_RefundsExcessNativeToken` [6](#0-5) ).
3. On the EVM contract, the user's balance decreases by only the amount actually spent on the swap (excess refunded). On the Tron contract, tracing `placeOrder`'s code path shows no such refund call is ever made after the swap block [4](#0-3) , so the full `X` sent by the user remains locked in the contract balance with no accounting entry or withdrawal path, resulting in permanent loss of the overpaid amount.

### Citations

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

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L275-284)
```text
#### Native token

The placement transaction carries `nativeValue` extra wei, which the gateway swaps into the fee token through its configured router (unused native is refunded). Check the balance now; the placement step adds `nativeValue` to the transaction:

```typescript title="check-native-fee.ts" lineNumbers
const nativeBalance = await sourceChain.client.getBalance({ address: account.address })
if (nativeBalance < nativeValue) throw new Error("Insufficient native balance for the solver fee")
```

The wallet still pays normal transaction gas on top of this value.
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3752)
```text
    /// @notice placeOrder with fee swap refunds unused ETH after swapETHForExactTokens.
    function testPlaceOrder_FeeSwap_RefundsExcessNativeToken() public {
        uint256 inputAmount = 1000 * 1e6;
        uint256 feeAmount = 1 * 1e18; // 1 DAI worth of fees

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: feeAmount,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        uint256 userEthBefore = user.balance;

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        // Send 5 ETH for a fee swap that should cost much less
        intentGateway.placeOrder{value: 5 ether}(order, bytes32(0));
        vm.stopPrank();

        // User should get back most of the 5 ETH — the swap only needed a tiny fraction
        uint256 ethSpent = userEthBefore - user.balance;
        assertTrue(ethSpent < 1 ether, "User should have been refunded most of the 5 ETH");
        assertTrue(ethSpent > 0, "User should have spent some ETH on the fee swap");
    }
```
