### Title
Excess native ETH sent to `EvmHost.dispatch()` / `fundRequest()` for fee-token swaps is not refunded and becomes permanently stuck in the contract - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` swap any `msg.value` sent by the caller into the exact fee-token amount required (`post.fee` / `get.fee` / `amount`) via `swapETHForExactTokens{value: msg.value}(...)`, but never capture the swap's actual spend or forward the unused leftover native ETH back to the caller, unlike the equivalent logic in `IntentGatewayV2.placeOrder()`. This is functionally the same bug class as the referenced Teller `repayLoan()` finding: a value transferred in excess of what is strictly owed is never returned to its payer and is permanently trapped in the contract.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

and in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

All three functions pass the caller's full `msg.value` into `swapETHForExactTokens(exactFeeAmount, path, address(this), block.timestamp)`, sending `address(this)` (i.e. `EvmHost`) as the recipient of the *output* tokens only. They discard the return value (`amounts`), so any ETH left over after the swap — refunded by the router to whoever called the router, which is `EvmHost` itself, not the original transaction sender — is simply added to `EvmHost`'s own balance. No logic exists afterward in these functions to compute a remainder and send it back to `_msgSender()`/`post.payer`.

This is directly contrasted by the correct pattern implemented in `IntentGatewayV2.placeOrder()`, which captures the swap's `amounts[0]` actually spent, decrements `msgValue` by that spent amount, and explicitly refunds any leftover native token to `msg.sender`: [4](#0-3) 

`EvmHost.dispatch`/`fundRequest` lack this final refund step entirely, so any native ETH provided above the amount consumed by the swap is stuck in `EvmHost` forever, exactly mirroring the audited pattern where "the excess amount ... will not be refunded to the borrower and permanently stuck in the contract" due to missing refund logic after a value-transferring operation.

### Impact Explanation
Any unprivileged user dispatching a POST/GET request or topping up a pending request's relayer fee with native token overpays whenever the token amount swapped costs less ETH than the `msg.value` supplied (which is the normal case, since users must estimate ETH input conservatively due to price slippage/quoting uncertainty and cannot know the exact router price at submission time). The excess ETH is not returned to the payer and becomes permanently locked inside `EvmHost`, with no user-facing withdrawal path shown for this balance. This is a direct, unbacked loss of user funds reachable from a single, ordinary `dispatch`/`fundRequest` transaction — a concrete permanent freezing of funds for any of `EvmHost`'s core dispatch entry points that are the primary way apps and end-users pay for cross-chain messages.

### Likelihood Explanation
Likelihood is high: every native-token payer of `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` who cannot supply the *exact* wei amount the AMM will consume (essentially all of them, given swap slippage and the impossibility of perfectly predicting on-chain price at tx-build time) will trigger this loss on every call. No special conditions, races, or privileged actors are needed — this occurs in the default, expected usage path documented for paying relayer/protocol fees with native tokens.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2.placeOrder()`: capture the `amounts` array returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, compute `msg.value - amounts[0]`, and explicitly send any remainder back to `_msgSender()` (or `post.payer` where applicable) at the end of each function, e.g.:
```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
uint256 refund = msg.value - amounts[0];
if (refund > 0) {
    (bool sent, ) = _msgSender().call{value: refund}("");
    require(sent);
}
```

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost)` (or `dispatch(DispatchGet)` / `fundRequest`) with `msg.value = 1 ether` intending to pay a `post.fee` of, say, 50 fee-token units.
2. `EvmHost` calls `IUniswapV2Router02.swapETHForExactTokens{value: 1 ether}(50, path, address(this), block.timestamp)`.
3. Suppose the actual ETH cost of 50 fee-token units is `0.3 ether`. The Uniswap V2 router refunds the unused `0.7 ether` — but to `msg.sender` of the router call, which is `EvmHost`, not the original user.
4. `EvmHost` never reads the swap's return value nor forwards any ETH back to the user; the `0.7 ether` remains as part of `EvmHost`'s balance indefinitely, with the user having no way to reclaim it, exactly analogous to the excess-repayment-stuck-forever pattern in the referenced Teller report.

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
