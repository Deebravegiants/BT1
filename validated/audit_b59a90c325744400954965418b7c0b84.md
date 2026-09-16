### Title
Excess native token sent to `EvmHost.dispatch()`/`fundRequest()` is silently trapped in the contract instead of being refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` and forward the *entire* `msg.value` into `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)`, but never handle the refund that the Uniswap router sends back when `msg.value` exceeds the amount actually required for the swap.

### Finding Description
Each of the three payable entry points in `EvmHost.sol` follows the same pattern: [1](#0-0) [2](#0-1) [3](#0-2) 

In each case, `msg.value` is passed wholesale to `swapETHForExactTokens{value: msg.value}(post.fee /* or get.fee / amount */, path, address(this), block.timestamp)`. The standard `UniswapV2Router02.swapETHForExactTokens` implementation computes the exact input `amounts[0]` needed to receive the requested output amount, and if `msg.value > amounts[0]` it refunds the difference via `TransferHelper.safeTransferETH(msg.sender, msg.value - amounts[0])`. Critically, `msg.sender` from the router's perspective is `EvmHost` itself (the contract that invoked the router), not the original caller of `dispatch`/`fundRequest`. Thus any overpayment is refunded back into `EvmHost`'s own balance and is never returned to the user who supplied the excess ETH.

This is directly analogous to the reported Allo `createPool` issue: a caller who sends more native currency than strictly required to cover a required fee has the excess silently retained by the protocol contract instead of being returned or exactly checked. Unlike `IntentGatewayV2.placeOrder`, which explicitly refunds unspent native token to `msg.sender` after the same kind of Uniswap swap: [4](#0-3) 

`EvmHost.sol`'s `dispatch`/`fundRequest` functions have no equivalent refund step, and no `require(msg.value == amounts[0])`-style exactness check either. Any caller who over-estimates fees (which the code's own documentation actively encourages, e.g. "Apply a generous 2x buffer" and calling `quote()*2` for the LayerZero endpoint), will lose the surplus permanently to the `EvmHost` contract.

### Impact Explanation
This causes a direct, permanent loss of funds for any unprivileged caller (any user, app, or the SDK-generated adapters such as `HyperbridgeLzEndpoint.send()` which explicitly multiplies the fee quote by 2x, or `HyperFungibleToken.send()`) who supplies `msg.value` greater than the exact amount consumed by the internal Uniswap swap. The overpaid native token is neither returned to the caller nor accounted for anywhere as protocol revenue that a user could reclaim - it is stuck as unaccounted ETH balance inside `EvmHost`, effectively an unbacked/unclaimed asset accumulation with no code path returning it to depositors.

### Likelihood Explanation
High likelihood: the documentation itself instructs integrators to overpay as a buffer against price movement/sandwich risk (see `HyperbridgeLzEndpoint.quote()` doubling the fee, and the general guidance to "estimate fees off-chain" and provide slack). Any normal, honest usage pattern where a caller sends slightly more ETH than the exact required swap input (which is essentially guaranteed given `getAmountsIn` price fluctuation between quote-time and execution-time) will trigger fund loss on every call, not just as an edge case.

### Recommendation
After each `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the returned `amounts[0]` and refund `msg.value - amounts[0]` back to `_msgSender()` (mirroring the pattern already implemented in `IntentGatewayV2.placeOrder`, e.g. via a `_sendValue`-style safe ETH transfer), instead of allowing the router's refund to be captured by `EvmHost` itself.

### Proof of Concept
1. `feeToken()` price via `swapETHForExactTokens` requires exactly `X` wei of ETH to obtain `post.fee` fee tokens.
2. User calls `EvmHost.dispatch{value: X + Δ}(post)` (e.g., following documented guidance to add slippage buffer, or simply misjudging price).
3. Inside `dispatch`, `swapETHForExactTokens{value: X + Δ}(post.fee, path, address(this), block.timestamp)` is invoked; the Uniswap router uses `X` wei, and refunds `Δ` wei back to `msg.sender`, which is `EvmHost`.
4. `EvmHost.dispatch` never forwards this `Δ` refund to the user; it is added to `EvmHost`'s native balance with no accounting entry tying it to the user.
5. The user has no function to reclaim `Δ`; it is permanently lost to them.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L974-985)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L1031-1042)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L383-397)
```text
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
