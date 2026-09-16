### Title
Excess native token sent to `placeOrder()` is permanently lost on the Tron IntentGatewayV2 (no refund path) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` accepts `msg.value` for native-token inputs and for the native-swap fee payment path, but unlike its EVM sibling it never returns any leftover `msgValue` to the caller. Any native coin sent beyond what is actually consumed by input escrow and the fee-swap is permanently trapped in the contract.

### Finding Description
`placeOrder()` in [1](#0-0)  tracks a local `msgValue` copy of `msg.value` and decrements it as native legs are consumed — first for `order.predispatch.assets` at [2](#0-1) , then for native `order.inputs` at [3](#0-2) , and finally for the optional fee swap at [4](#0-3) . After the fee block, the function proceeds directly to emitting `OrderPlaced` and returns, with no code path that forwards any remaining `msgValue` back to `msg.sender` [5](#0-4) .

This is the exact bug class from the report: a function meant to accept native coin as payment silently absorbs excess/unintended `msg.value` instead of reverting or refunding it. The upstream EVM implementation of the same function explicitly guards against this by refunding any unspent native token: [6](#0-5) . The Tron fork is missing this final refund step entirely, even though it computes and mutates `msgValue` in the same way as the EVM version.

Concretely, native coin is stranded whenever:
- A user overpays `msg.value` beyond the sum of native `order.inputs` amounts and (if paid in native) `order.fees` swap cost — e.g. fat-fingered value, or a wallet that always includes a safety buffer.
- `order.fees == 0` (no fee to swap) but the user still sends `msg.value` covering only native inputs plus extra, since the only consumer of `msgValue` besides inputs is the fee-swap block, which is skipped when `order.fees == 0`.
- Any of the native input/predispatch amounts leave a remainder that the fee-swap doesn't fully consume (e.g., swap uses less than the full `msgValue` if Uniswap returns unused ETH separately, or fees are paid via ERC20 despite `msgValue > 0`).

### Impact Explanation
This is a permanent loss of user funds: native coin sent to `placeOrder()` beyond what the function internally accounts for is not credited to any escrow slot, not swapped, and not refunded — it sits in the contract's balance with no accounting entry and no withdrawal path tied to the depositor. This matches "permanent freezing/loss of funds" for any unprivileged user submitting an order transaction, satisfying the Medium severity bar from the analogous CPortModule report.

### Likelihood Explanation
Any caller of `placeOrder{value: X}(...)` on the Tron IntentGatewayV2 who sends `X` larger than the exact sum required for native inputs and the native fee-swap (or who pays fees in the fee token via approval while still attaching `msg.value` for a native input, leaving a small remainder) will trigger the loss. Since the SDK/documentation for the sibling EVM contract explicitly warns users that "the placement transaction's `msg.value`... plus the quoted `nativeValue`... Never zero out `value`" [7](#0-6) , overestimating `msg.value` is a realistic and even encouraged client behavior, making this reachable in normal usage, not just adversarial input.

### Recommendation
Mirror the EVM `IntentGatewayV2.sol` behavior in the Tron contract: after the fee-escrow block, add a refund of any remaining `msgValue` back to `msg.sender` (or `_sendValue(msg.sender, msgValue)` equivalent), exactly as done at [6](#0-5) . Alternatively, revert if `msgValue` is non-zero after all native consumption paths are accounted for.

### Proof of Concept
1. User calls `placeOrder{value: 1.5 ether}(order, graffiti)` on the Tron `IntentGatewayV2`, where `order.inputs` contains one native-token (`address(0)`) entry of `1 ether` and `order.fees == 0`.
2. In the native-input branch, `msgValue` (`1.5 ether`) is decremented by `1 ether`, leaving `msgValue = 0.5 ether` [8](#0-7) .
3. Because `order.fees == 0`, the fee-swap block at [4](#0-3)  is skipped entirely — `msgValue` is never touched again.
4. The function emits `OrderPlaced` and returns; the `0.5 ether` remainder stays in the contract's balance, uncredited to `_orders[commitment]` and with no user-triggerable withdrawal for it — permanently lost to the sender.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-388)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L398-403)
```text
                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
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

**File:** docs/content/developers/evm/intent-gateway/placing-orders.mdx (L486-488)
```text
<Callout type="warn">
The placement transaction's `msg.value` is the `value` from `AWAITING_PLACE_ORDER` — the order's native-token input amounts — plus the quoted `nativeValue` when paying the solver fee in native token. Never zero out `value`.
</Callout>
```
