## Analog Found

### Title
Excess native ETH sent to `EvmHost.dispatch()` / `fundRequest()` is trapped in the host with no refund path to the depositor - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` and swap it for an exact amount of fee tokens via Uniswap, but never validate that `msg.value` equals the amount actually needed, and never refund any leftover ETH to the caller. This mirrors the reported Notional bug class: a function that silently accepts excess native value with no strict-equality check and no mechanism to return the surplus to the depositor.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 

the full `msg.value` is forwarded to `swapETHForExactTokens{value: msg.value}(post.fee, ...)`. This call only needs to spend enough ETH to buy `post.fee` fee tokens; any unused ETH is refunded by the router/wrapper — but to `msg.sender` as seen by the router, which is `EvmHost` itself (the direct caller), not the original end user (`_msgSender()`). The same pattern exists in `dispatch(DispatchGet memory get)` and `fundRequest(bytes32 commitment, uint256 amount)`: [2](#0-1) [3](#0-2) 

None of these three functions checks `msg.value` against the amount required, and none refunds the unspent remainder back to `_msgSender()`. Confirming that unswapped ETH is returned to the direct caller (not the transaction originator) can be seen in the project's own Uniswap wrapper implementation, which refunds to `msg.sender` of the swap call: [4](#0-3) 

Because `EvmHost` is the caller of the router in all three dispatch paths, any leftover ETH accumulates as native balance sitting in `EvmHost`, never credited back to the user who overpaid. This is exactly the reported bug class from the external report: no `require(amount == msg.value)` check, and no mechanism analogous to `returnExcessWrapped` to let the user reclaim their excess native token.

By contrast, the codebase demonstrates the correct pattern elsewhere — `IntentGatewayV2._post`/`placeOrder` explicitly tracks `msgValue` after the swap and refunds any remainder to `msg.sender`: [5](#0-4) 

`EvmHost.dispatch`/`fundRequest` lack this refund step entirely.

### Impact Explanation
Any application or user calling `IDispatcher(host).dispatch{value: msg.value}(post)` (as explicitly instructed in the protocol's own documentation) with a `msg.value` larger than what the Uniswap swap consumes permanently loses the difference — it is not returned to them. The only way to recover it is `EvmHost.withdraw()`, which is `restrict(_hostParams.hostManager)`-gated and pays out to an arbitrary `beneficiary` chosen by cross-chain governance: [6](#0-5) 
— i.e. governance, not the original depositor, controls where that stranded ETH goes. This is a real loss-of-funds vector for any integrator/user who over-estimates the native fee (a common occurrence since fee estimation off-chain can only approximate the on-chain Uniswap execution price at call time).

### Likelihood Explanation
High likelihood: dispatch fee estimation is inherently imprecise (AMM price can move between quote and execution, and the documentation explicitly instructs callers to send `msg.value` to cover fees), so overpayment is a routine, not edge-case, occurrence for any app using native-token payment for POST/GET dispatch or `fundRequest`. No malicious actor is required — this affects every honest caller who slightly overestimates the required native amount.

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the actual amount spent (or the returned `amounts[0]`) and refund `msg.value - amountSpent` back to `_msgSender()`, mirroring the pattern already used in `IntentGatewayV2`/`ExtrinsicIntents` (`_sendValue(msg.sender, msgValue)`).

### Proof of Concept
1. A caller estimates the ETH needed for a `post.fee` of X fee-tokens off-chain and calls `IDispatcher(host).dispatch{value: msg.value}(post)` with `msg.value` slightly higher than needed to account for slippage.
2. Inside `dispatch`, `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` only consumes enough ETH to buy exactly `post.fee` tokens; the router refunds the unused ETH to `msg.sender`, which from the router's perspective is `EvmHost`.
3. `EvmHost`'s ETH balance increases by the unspent amount; the caller's transaction completes normally with no refund event or transfer back to them.
4. The excess ETH is now indistinguishable from other host balance and can only be recovered via a cross-chain governance `Withdraw` action to a beneficiary address chosen by governance, not the original overpaying caller.

### Citations

**File:** evm/src/core/EvmHost.sol (L651-660)
```text
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

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

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L87-96)
```text
        IUniversalRouter(_params.universalRouter).execute{value: msg.value}(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
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
