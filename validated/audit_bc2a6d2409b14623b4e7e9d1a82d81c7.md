### Title
Excess native ETH sent for fee-swap in `dispatch`/`fundRequest` is refunded to `EvmHost` itself and never forwarded to the caller, permanently trapping user funds - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all forward the entire `msg.value` to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)` to buy an exact amount of `feeToken()`. The standard Uniswap V2 router behavior is to refund any leftover/unspent ETH to `msg.sender` of that call — which, since `EvmHost` itself calls the router, is `EvmHost`, not the original transaction sender. `EvmHost` never measures or forwards this residual native ETH back to the caller/payer, so any overpayment is permanently stuck in the contract. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
This is the direct analog of the Notional H-3 bug class: a downstream external call refunds excess native ETH to the *calling contract* rather than the end user, and the calling contract's wrapper logic never accounts for or forwards that residual balance.

In `dispatch(DispatchPost memory post)`:
```solidity
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    }
    ...
}
``` [1](#0-0) 

The caller can (and, per the docs example, often will) send more ETH than the fee actually costs, because callers don't know the exact swap rate in advance — the SDK/docs example even instructs applications to forward the full `msg.value`:
```solidity
return IDispatcher(_host).dispatch{value: msg.value}(post);
``` [4](#0-3) 

`swapETHForExactTokens` on Uniswap V2 routers only spends up to `post.fee` worth of ETH and refunds the unspent remainder to `msg.sender` — i.e., to `EvmHost`. `EvmHost`'s `dispatch` function does not read `address(this).balance` before/after the swap, nor does it forward any leftover ETH back to `_msgSender()`/`post.payer`. The same pattern repeats in `dispatch(DispatchGet)` and `fundRequest`:
```solidity
function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            get.fee, path, address(this), block.timestamp
        );
    }
    ...
}
``` [2](#0-1) 
```solidity
function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            amount, path, address(this), block.timestamp
        );
    }
    ...
}
``` [3](#0-2) 

Notably, other parts of this same codebase (e.g. `IntentGatewayV2`/`ExtrinsicIntents` and the `UniV4UniswapV2Wrapper`) explicitly implement the balance-snapshot-and-refund pattern that is missing here:
```solidity
uint256 refundETH = address(this).balance - balanceBefore;
if (refundETH > 0) {
    (bool success,) = msg.sender.call{value: refundETH}("");
    require(success, "ETH refund failed");
}
``` [5](#0-4) 
```solidity
// Refund any unspent native tokens to the user.
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
``` [6](#0-5) 

This confirms the project's own convention is to refund excess native token, but `EvmHost.dispatch`/`dispatch(DispatchGet)`/`fundRequest` do not follow it — the exact root cause described in the Notional report (residual native ETH returned to the wrapping contract but the wrapper's forwarding logic doesn't account for it).

### Impact Explanation
Any unprivileged caller (application contract, relayer, or end user) dispatching a POST/GET request or funding a request with native ETH who sends `msg.value` greater than what is exactly required to purchase `post.fee`/`get.fee`/`amount` of fee tokens will have the difference permanently stuck inside `EvmHost`. Because `EvmHost` has no mechanism found in this function set to sweep or return this stray ETH to the depositor, this constitutes a permanent loss/freezing of user funds — a direct asset loss exactly matching the reported bug class's impact ("Loss of assets as the residual ETH is not sent to the users").

### Likelihood Explanation
High likelihood: this triggers on the ordinary, documented usage path. The project's own developer docs instruct applications to send `msg.value` for fee payment without requiring an exact quote match, and Uniswap V2 exchange rates fluctuate between quote time and execution time, making overpayment routine rather than an edge case. Every `dispatch`/`fundRequest` call using native-token payment is exposed.

### Recommendation
In `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, snapshot `address(this).balance` (excluding the incoming `msg.value`) before calling `swapETHForExactTokens`, and after the call, compute the delta and forward any residual native ETH back to `_msgSender()` (or the designated payer), following the same pattern already used in `IntentGatewayV2`/`ExtrinsicIntents` (`_sendValue`) and `UniV4UniswapV2Wrapper`.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` only costs `0.1 ETH` worth of `feeToken` at current pool price.
2. `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)` spends only `~0.1 ETH` and the Uniswap V2 router refunds the remaining `~0.9 ETH` to `msg.sender` of the call, i.e. `EvmHost`.
3. `dispatch` proceeds to emit `PostRequestEvent` and returns; no code path reads `address(this).balance` or transfers ETH back to the caller.
4. The `~0.9 ETH` overpayment remains permanently locked in `EvmHost`'s balance, unrecoverable by the caller through this function set.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L59-69)
```text
    DispatchPost memory post = DispatchPost({
        body: message,
        dest: StateMachine.evm(1),
        timeout: timeout,
        to: abi.encode(to),
        fee: relayerFee,
        payer: msg.sender
    });

    return IDispatcher(_host).dispatch{value: msg.value}(post);
}
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L83-96)
```text
        // Snapshot standing balance (excluding inbound msg.value) so the refund is the swap-call delta only,
        // immune to any ETH that lands on the wrapper from outside the router (e.g., selfdestruct, coinbase).
        uint256 balanceBefore = address(this).balance - msg.value;

        IUniversalRouter(_params.universalRouter).execute{value: msg.value}(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
