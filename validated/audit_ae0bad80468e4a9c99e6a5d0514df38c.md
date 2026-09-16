## Title
Missing deadline/slippage protection in native-to-fee-token swap during `placeOrder` enables MEV sandwich extraction from user's escrowed ETH - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
When a user pays the IntentGateway's `order.fees` in native ETH, `placeOrder` performs an on-chain Uniswap V2 swap (`swapETHForExactTokens`) to convert that ETH into the protocol fee token. The swap is called with `deadline = block.timestamp` — which provides zero real deadline protection — and with the swap's implicit "maximum input" set to whatever ETH remains in the transaction, so an attacker can sandwich the swap and force the trade to consume materially more of the user's escrowed ETH than a fair-market execution would, exactly the "no slippage protection on liquidity/swap operations" bug class described in the reference report (there, the missing protection was on Uniswap `mint`/`burn`; here it's on the routed swap the protocol itself performs on the user's behalf).

### Finding Description
In `placeOrder`, when the caller pays `order.fees` with native tokens, the gateway swaps ETH for the fee token directly through the Uniswap V2 router: [1](#0-0) 

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
```

This is `swapETHForExactTokens`, requesting a fixed output amount (`order.fees`) and offering up to the entire remaining `msgValue` as input. Two problems compound here:

1. **`deadline = block.timestamp`** is the classic Uniswap anti-pattern: the deadline is evaluated at execution time, so it always passes regardless of how long the transaction sits in the mempool. This gives an attacker unlimited time to observe the pending `placeOrder` transaction and manipulate the WETH/feeToken pool price beforehand.
2. **No caller-supplied slippage/maximum-input bound**: the contract does not let the user express "I am only willing to spend up to X ETH for this fee," it silently allows the swap to consume as much of `msgValue` as the (potentially manipulated) pool price demands, refunding only what's left (`msgValue -= amounts[0]`).

An attacker can front-run the `placeOrder` transaction to push the WETH→feeToken price unfavorably, let the victim's swap execute at the bad price (consuming more ETH from the victim's own escrowed funds for the same `order.fees` output), then back-run to restore the price and pocket the difference — the same sandwich mechanic described in the source report, just applied to the protocol's own fee-conversion swap rather than a liquidity mint/burn.

The identical pattern exists in the Tron deployment of the same contract: [2](#0-1) 

### Impact Explanation
Any unprivileged user calling `placeOrder` with native ETH and a non-zero `order.fees` is exposed. The loss is bounded by the ETH they submitted for the order but is a real, extractable value loss (classic sandwich MEV) with no way for the caller to protect themselves — there is no slippage/maximum-input parameter exposed on `placeOrder`. Given `placeOrder` is a core, permissionless entry point of the Intent Gateway used by every order originator, this is a systemic, repeatedly exploitable value-extraction vector rather than an edge case.

### Likelihood Explanation
High: this code path executes unconditionally whenever a user pays fees with native ETH, which is an expected, common usage pattern documented in the Intent Gateway fee table (`Fill fee (order.fees) | At order placement | User (in fee token or native ETH)`). Sandwiching a public mempool transaction with a `block.timestamp` deadline and no minimum-output/maximum-input guard is a well-understood, low-cost MEV strategy requiring no special privilege — only visibility into the mempool.

### Recommendation
- Replace `deadline: block.timestamp` with a caller-supplied `deadline` parameter (as `Order`/`FillOptions`-style structs already do elsewhere, e.g. `FillOptions.validUntil`) so pending transactions cannot be executed arbitrarily late.
- Expose an explicit maximum-ETH-in (or equivalently a minimum acceptable refund) parameter that the user signs as part of the order, and pass it as the true `msg.value` cap to `swapETHForExactTokens`, reverting if the fair-price maximum is exceeded, instead of implicitly allowing the swap to consume the full `msgValue`.
- Consider deriving an oracle- or TWAP-based sanity bound on the acceptable fee-token price (similar to the pattern already used in `SimplexPaymaster.swapAndDeposit`, which derives `amountOutMin` from Chainlink oracles) so the fee-conversion swap cannot be executed at an arbitrarily manipulated spot price.

### Proof of Concept
1. User calls `placeOrder{value: X}(order, graffiti)` with `order.fees = F` (in `feeToken`) and no predispatch, so the flow reaches the fee-swap branch with `msgValue = X`.
2. Attacker observes the pending transaction in the mempool and front-runs it with a large WETH→feeToken buy (or sell, depending on pool direction) to move the pool price against the victim.
3. Victim's transaction executes: `swapETHForExactTokens{value: X}(F, [WETH, feeToken], address(this), block.timestamp)` still succeeds (deadline is always satisfied) but consumes `amounts[0]` ETH close to `X` instead of the fair-market amount, because there is no minimum-output-per-input bound the victim could have set.
4. Attacker back-runs to restore the price and sells into the temporarily inflated pool, capturing the price impact they created as profit, funded by the victim's escrowed ETH refund shrinking (`msgValue -= amounts[0]`) or reverting if `amounts[0] > msgValue`.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L331-390)
```text

    /**
     * @notice Places an order with the given order details.
     * @dev This function allows users to place an order by providing the order details.
     * @param order The order details to be placed.
     * @param graffiti The arbitrary data used for identification purposes.
     */
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
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }

        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;
```
