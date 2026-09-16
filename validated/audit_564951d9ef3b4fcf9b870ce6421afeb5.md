### Title
Excess native token payment in `EvmHost.dispatch()`/`fundRequest()` is refunded to the host contract instead of the caller, permanently trapping user funds - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and swap it for the exact `feeToken` amount via `IUniswapV2Router02.swapETHForExactTokens`. When the caller sends more native token than the swap actually consumes, the Uniswap V2 router refunds the unused ETH to `msg.sender` of the swap call — which is `EvmHost` itself, not the original transaction sender. `EvmHost` never forwards or accounts for this leftover balance back to the user, so any overpayment is permanently absorbed into the contract with no recovery mechanism.

### Finding Description
In `EvmHost.dispatch(DispatchPost)`: [1](#0-0) 

and identically in `dispatch(DispatchGet)` and `fundRequest`: [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` is called with the caller's entire `msg.value`, but only `post.fee` (or `get.fee`/`amount`) worth of fee token is required. Standard Uniswap V2 router semantics refund any unspent ETH to the address that invoked the swap — here, `EvmHost` — not to `_msgSender()` (the original dispatcher of the request). Unlike the sibling contract `IntentGatewayV2.placeOrder`, which explicitly tracks `msgValue -= amounts[0]` and calls `_sendValue(msg.sender, msgValue)` to refund the caller: [4](#0-3) 

`EvmHost.dispatch()`/`fundRequest()` contain no equivalent refund step after the swap. `EvmHost.sol` also has no `withdraw`/`sweep` function to later recover stray ETH, so the leftover balance is permanently stuck in the contract.

This is the exact bug-class analog described in the report: a refund of unused value/gas is misdirected to the contract (`payable(this)`) instead of the user who supplied it, and there is no mechanism to reclaim it.

### Impact Explanation
Any unprivileged caller — an app contract or EOA (via `HyperApp.dispatchWithFeeToken`/native dispatch helpers, `IDispatcher.dispatch{value: ...}`) — that pays with native token and slightly overestimates the required amount (which is expected behavior, since callers typically supply a buffer to guard against price slippage, as documented in `HyperbridgeLzEndpoint.quote()`'s "generous 2x buffer" comment) will have the excess silently absorbed by `EvmHost` with no path to recovery. This is a direct, permanent loss of user funds triggered by ordinary usage of the primary message-dispatch entry point of the protocol (`dispatch(DispatchPost)`/`dispatch(DispatchGet)`), which is the most heavily used function in the entire system, since virtually every cross-chain message (POST/GET) that pays in native token goes through it.

### Likelihood Explanation
Very high. Overpayment is the normal/documented case for native payments here — callers cannot know the exact Uniswap V2 quote in advance and are expected to over-supply value that gets swapped for an exact fee-token amount (see `sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol` quoting a 2x buffer). Every such call loses the unused remainder to the contract permanently.

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the `amounts[0]` actually spent (as `IntentGatewayV2` already does) and refund `msg.value - amounts[0]` back to `_msgSender()` via a low-level call, reverting on failure. Alternatively, add an authorized sweep/refund path, though refunding the exact caller in the same transaction is the correct fix, mirroring the existing `IntentGatewayV2._sendValue` pattern.

### Proof of Concept
1. Caller calls `EvmHost.dispatch{value: 2 ether}(post)` where `post.fee` only requires 0.1 ETH worth of `feeToken`.
2. `swapETHForExactTokens{value: 2 ether}(post.fee, path, address(this), ...)` executes; the router consumes ~0.1 ETH equivalent and refunds ~1.9 ETH back to `msg.sender`, which is `EvmHost`.
3. `EvmHost`'s native balance increases by ~1.9 ETH with no accounting entry crediting the caller.
4. There is no `withdraw`, `sweep`, or `receive`-triggered forwarding logic in `EvmHost.sol` to return this value to the caller or any party; the ETH is permanently stuck in the contract.

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
