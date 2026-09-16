### Title
Excess native fee on `EvmHost.dispatch`/`fundRequest` is refunded to the Host contract instead of the paying user - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert overpaid native token (`msg.value`) into `feeToken` via `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. Just like the Tapioca report where the LayerZero `refundAddress` was set to the wrong `msg.sender` because an intermediate contract called the LZ helper, here the "refund recipient" of the leftover native ETH from the swap is implicitly whatever address the router treats as its caller — which is `EvmHost` itself, not the original transaction sender who overpaid.

### Finding Description
In `dispatch(DispatchPost)`:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
``` [1](#0-0) 

The same pattern repeats for GET dispatch and `fundRequest`: [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` is a swap-for-exact-output call: if the caller sends more ETH than needed to obtain `post.fee`/`get.fee`/`amount` tokens, the Uniswap V2 Router refunds the *unused* ETH back to `msg.sender` of that router call. Since `EvmHost` itself is the direct caller of the router (not the original end user), any leftover ETH is refunded to `EvmHost`'s own balance, not the account that originally called `dispatch`/`fundRequest` and sent the excess `msg.value`.

This mirrors the Tapioca finding precisely: the code relies on an implicit "refund goes to caller" mechanic in an external dependency (the LayerZero endpoint in Tapioca's case, the Uniswap V2 Router here), but the *direct* caller in that external call is an intermediate contract (`Magnetar`/`EvmHost`) rather than the original human user who is entitled to the refund.

Other parts of the codebase demonstrate awareness of this exact problem and handle it correctly by capturing the actual amount spent and explicitly sending back the difference to `msg.sender`, e.g. `IntentGatewayV2._fillCrossChain` / `IntentGatewayV2.placeOrder`: [4](#0-3) 
and the custom AMM wrappers (`UniV3UniswapV2Wrapper.sol`, `UniV4UniswapV2Wrapper.sol`) which explicitly compute the unspent amount and forward it back to `msg.sender`: [5](#0-4) [6](#0-5) 

However, `EvmHost.dispatch`/`fundRequest` never capture or forward any leftover ETH after the swap call — they simply pass `recipient = address(this)` to the router and never check for/redistribute a refund, unlike `IntentGatewayV2`'s consistent pattern of tracking `msgValue` and calling `_sendValue(msg.sender, msgValue)` for leftovers.

### Impact Explanation
Any user or application dispatching a POST/GET request or funding a request via `EvmHost.dispatch{value: ...}` / `fundRequest{value: ...}` who supplies slightly more native token than the exact swap requires (which is the normal/expected case, since users must estimate gas/price slippage and typically overpay to ensure the swap doesn't revert) will have the excess silently retained by the `EvmHost` contract instead of being returned to them. Over many dispatches this constitutes a direct, permanent loss of user funds — functionally identical in effect to the Tapioca refund-address bug, just realized through Uniswap's implicit-caller-refund model instead of a LayerZero `refundAddress` field. The retained ETH is not tracked anywhere as belonging to users; it becomes indistinguishable protocol/host balance, meaning affected users have no recourse to reclaim it.

### Likelihood Explanation
High. Overpaying `msg.value` for a "swap to exact output" call is the standard/expected way to call this function safely (since callers cannot know the exact ETH price of `feeToken` at execution time), so nearly every native-token dispatch/fundRequest call that doesn't hit the exact price will leak funds. This is a systemic issue affecting the primary entrypoint used to pay Hyperbridge's dispatch fee in native token, as documented in the public API docs (`dispatch()` "Native token (msg.value): Automatically swapped to fee token via Uniswap").

### Recommendation
Track the ETH balance of `EvmHost` before and after the `swapETHForExactTokens` call (or read the returned `amounts[0]` actually spent) and forward the difference back to `_msgSender()` (or an explicit user-supplied refund address), following the same pattern already used in `IntentGatewayV2` and the AMM wrapper contracts. E.g.:
```solidity
uint256 balanceBefore = address(this).balance - msg.value;
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);
uint256 refund = address(this).balance - balanceBefore;
if (refund > 0) {
    (bool ok,) = _msgSender().call{value: refund}("");
    require(ok, "refund failed");
}
```

### Proof of Concept
1. User calls `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` only requires 0.6 ETH worth of swap input to obtain the exact `feeToken` amount.
2. `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)` executes; the router consumes ~0.6 ETH and refunds the remaining ~0.4 ETH to `msg.sender` of the router call, which is `EvmHost`.
3. `EvmHost`'s function returns without forwarding any leftover ETH to the original caller; the 0.4 ETH remains permanently in `EvmHost`'s balance, unaccounted for and unclaimable by the user who sent it, exactly as in the referenced Tapioca `Magnetar`/`TapiocaOmnichainEngineHelper` `msg.sender` confusion bug.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L91-96)
```text
        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
        }
```
