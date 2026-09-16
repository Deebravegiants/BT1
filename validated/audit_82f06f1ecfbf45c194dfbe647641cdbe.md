This confirms the vulnerability: `placeOrder()` in the Tron variant of `IntentGatewayV2` is `payable` and never refunds any unspent `msg.value` back to the caller, unlike the canonical EVM `IntentGatewayV2.sol` version which explicitly performs `_sendValue(msg.sender, msgValue)` at the end.

### Title
Stuck ETH in `IntentGatewayV2::placeOrder()` (Tron variant) when native token is overpaid or unused alongside ERC20 inputs/fees - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2.placeOrder()` accepts `msg.value` for escrowing native-token order inputs and/or for swapping to the fee token to pay dispatch fees, but it never refunds the leftover/unused `msg.value` to the caller. The canonical EVM `IntentGatewayV2.sol` contains an explicit final refund (`_sendValue(msg.sender, msgValue)`), but this step is entirely missing from the Tron contract's `placeOrder()`, causing native tokens to be permanently locked in the contract.

### Finding Description
`placeOrder()` is `payable` and tracks a local `msgValue` variable that is decremented as native-token inputs are consumed [1](#0-0) . When `order.fees > 0`, if `msgValue > 0` the code swaps native ETH for the exact fee-token amount via `swapETHForExactTokens`, but it discards the returned `amounts` array and never reduces `msgValue` by the actual amount spent, nor refunds the caller [2](#0-1) . The function then proceeds directly to emitting `OrderPlaced` and returns, with no logic anywhere in the function to return unspent `msgValue` to `msg.sender` [3](#0-2) .

By contrast, the reference `evm/src/apps/IntentGatewayV2.sol::placeOrder()` correctly captures the Uniswap swap's actual spend (`msgValue -= amounts[0]`) and explicitly refunds any remaining native token to the caller at the end of the function via `_sendValue(msg.sender, msgValue)` [4](#0-3) . This refund logic is completely absent from the Tron variant, so:
1. Any user who sends `msg.value` larger than needed to cover the fee-token swap (analogous to the DeXe report's "eth & erc20 funded simultaneously" case) has the excess ETH permanently trapped since `swapETHForExactTokens` returns unused ETH to the calling contract (IntentGatewayV2 itself), not to the original user, and the contract never forwards it onward.
2. If a user mistakenly (or a front-end bug causes them to) attach `msg.value` to an order whose inputs are entirely ERC20 and whose `order.fees == 0`, the entire `msg.value` is simply stranded in the contract with zero accounting or recovery path.

This is the direct analog of the reported `DistributionProposal::execute()` bug: a function that can be simultaneously "funded" by both native ETH and ERC20/fee-token flows, where the ETH portion is silently absorbed by the contract instead of being used, refunded, or reverted.

### Impact Explanation
Native tokens (TRX on Tron, or the equivalent gas-token on any EVM chain this contract is deployed to) sent to `placeOrder()` in excess of what is consumed by the fee swap, or sent when no native input/fee-swap is required, become permanently locked in the `IntentGatewayV2` contract with no withdrawal path for the depositing user. This is a direct, unrecoverable loss of funds for any user who over-supplies `msg.value`, which is a realistic and easy user/integrator mistake since the sibling EVM contract's ABI and semantics suggest excess value is refunded.

### Likelihood Explanation
Likelihood is high: any ordinary user placing an order who slightly overestimates the required native-token amount for `order.fees`, or who attaches any `msg.value` to an order without a native-token input, triggers the fund loss. No privileged role, malicious actor, or complex conditions are required — a single unprivileged `placeOrder()` call from a normal user is sufficient.

### Recommendation
Mirror the fix already present in `evm/src/apps/IntentGatewayV2.sol`: capture the actual native amount consumed by `swapETHForExactTokens` (its `amounts[0]` return value) and decrement `msgValue` accordingly, then add an explicit refund of any remaining `msgValue` back to `msg.sender` at the end of `placeOrder()` in `evm/tron/contracts/apps/IntentGatewayV2.sol`, consistent with the canonical implementation.

### Proof of Concept
1. A user calls `placeOrder(order, graffiti)` on the Tron `IntentGatewayV2` with an order whose `order.inputs` are entirely ERC20 tokens and `order.fees == 0`.
2. The user attaches `msg.value = X` TRX (e.g. by wallet/UI error).
3. Inside `placeOrder`, `msgValue` starts at `X`; the loop at lines 451-468 only processes ERC20 `safeTransferFrom` for the (non-native) inputs and never touches `msgValue`; since `order.fees == 0`, the fee block at lines 471-488 is skipped entirely.
4. Execution falls through directly to emitting `OrderPlaced` and returns — `msgValue` (still equal to `X`) is never spent, tracked, or refunded.
5. The `X` TRX now sits in the contract's balance permanently, with no function in the contract that allows the user (or anyone) to reclaim it, exactly mirroring the reported "stuck eth" pattern from `DistributionProposal::execute()`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-460)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L490-506)
```text
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
