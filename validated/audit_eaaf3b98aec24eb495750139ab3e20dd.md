### Title
Unspent Native Token Not Refunded After Fee Swap in `IntentGatewayV2.placeOrder()` (Tron) — Leftover ETH Permanently Stuck In Contract - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` performs a `swapETHForExactTokens()` call to convert user-supplied native token into the fee token, but — unlike the mirrored EVM implementation — never captures the actual amount spent by the swap nor refunds the remaining `msgValue` to the caller. Any native token sent in excess of what the fee swap actually consumes is silently left in the contract, unaccounted for and unrefunded, exactly mirroring the "leftover tokens stuck due to unused router output" bug class described in the reference report.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol`, the reference (correct) implementation captures the router's return value and refunds any unspent native token to the user: [1](#0-0) 

In the Tron port, the equivalent block calls the same router function but drops both the amount bookkeeping and the final refund: [2](#0-1) 

Because `IUniswapV2Router02.swapETHForExactTokens{value: msgValue}(...)` is called with the *entire remaining* `msgValue` rather than only the amount needed, and the caller of the router is the `IntentGatewayV2` contract itself (`msg.sender` inside the router call), any dust refunded by the router (`msg.value - amounts[0]`) is sent back to the `IntentGatewayV2` contract address — not to the end user. The Tron `placeOrder()` never reads this refund, never emits `DustCollected`, and has no final `if (msgValue > 0) _sendValue(msg.sender, msgValue)` step (which exists in the canonical EVM contract). The excess native token therefore accumulates in the contract with no on-chain record tying it to the depositor.

This is directly analogous to the `Auction.addInitialLiquidity()` finding: a router/AMM-style call that doesn't use 100% of the supplied funds, combined with the caller omitting any leftover-sweep/refund step, results in funds being trapped in the contract.

### Impact Explanation
Every call to `placeOrder()` on the Tron deployment with `order.fees > 0` and `msg.value` greater than what the fee swap actually requires (which is the common case, since users must overestimate gas/price-impact when funding a "swap for exact fee tokens" call) permanently strands the difference in the `IntentGatewayV2` contract instead of returning it to the user. Funds are not attributed to any specific order/commitment and are not covered by the `DustCollected`/`DustSwept` accounting used elsewhere in the same contract, so they can only be recovered later through a privileged governance `SweepDust` action — not by the user who overpaid. This is a concrete, unprivileged-user-triggered fund loss for the affected depositor, matching the Medium severity of the original finding.

### Likelihood Explanation
This triggers on essentially every ordinary `placeOrder()` call on Tron that pays the order fee in native token, since callers must send `msg.value` greater than or equal to the exact fee-swap cost and typically cannot predict the precise amount consumed by `swapETHForExactTokens`. No special conditions, front-running, or malicious actors are required — it is a straightforward path reachable by any user placing an order.

### Recommendation
Mirror the canonical EVM implementation: capture the `amounts` array returned by `swapETHForExactTokens`, decrement `msgValue` by `amounts[0]`, and after the fee-escrow block, refund any remaining `msgValue` to `msg.sender` (as `evm/src/apps/IntentGatewayV2.sol` already does). Additionally emit `DustCollected` for any unavoidable residual so it is auditable and sweepable if a refund path is not feasible.

### Proof of Concept
1. User calls `placeOrder(order, graffiti)` on the Tron `IntentGatewayV2` with `order.fees = X` and `msg.value = Y` where `Y > requiredForSwap(X)` (e.g., sending 5 native tokens when the swap only needs 0.01 to buy `X` fee tokens), and with no native-token order inputs (so all of `msg.value` reaches the fee-swap branch).
2. `swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` executes; the underlying router computes `amounts[0] < msgValue`, deposits `amounts[0]` worth of ETH, and refunds `msgValue - amounts[0]` back to `msg.sender` of the router call — which is the `IntentGatewayV2` contract, not the user.
3. `placeOrder()` completes: `_orders[commitment][TRANSACTION_FEES] = order.fees` is set correctly, but the leftover `msgValue - amounts[0]` native token now sits in the contract's balance with no event emitted and no code path returning it to the user.
4. Compare with `evm/tests/foundry/IntentGatewayV2Test.sol::testPlaceOrder_FeeSwap_RefundsExcessNativeToken`, which asserts the EVM contract refunds unspent ETH after the identical swap — the Tron contract has no equivalent test or refund logic, confirming the excess is trapped. [3](#0-2)

### Citations

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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3751)
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
```
