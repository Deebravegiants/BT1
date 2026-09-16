## Title
`EvmHost.dispatch`/`fundRequest` swap the caller's full `msg.value` via Uniswap without refunding unspent native token, permanently trapping user funds in the Host - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all convert user-supplied native token into `feeToken` via `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)`, but they never capture the `amounts[]` return value or refund the unspent ETH to the caller, unlike the analogous flow in `IntentGatewayV2`.

### Finding Description
In `EvmHost.dispatch(DispatchPost)`: [1](#0-0) 

the entire `msg.value` is forwarded to `swapETHForExactTokens`, requesting exactly `post.fee` in the fee token. Uniswap's `swapETHForExactTokens` refunds any leftover ETH to the address that called the router — here, that is `address(this)` (the `EvmHost` contract), not the original external caller who sent `msg.value` into `dispatch()`. The function performs no follow-up step to send that refunded ETH back to `_msgSender()`.

The same pattern (swap-full-`msg.value`, no capture/refund) exists in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

This is directly reachable by any unprivileged caller: every app in the repo that dispatches native-token-funded ISMP requests simply forwards `msg.value` straight to the Host, expecting the Host to handle any excess correctly, e.g. `HyperApp`/`HyperFungibleToken`/`WrappedHyperFungibleToken` variants: [4](#0-3) 
and the LayerZero endpoint adapter: [5](#0-4) 

Contrast this with `IntentGatewayV2.placeOrder`, which correctly captures the swap output and refunds any leftover native token to the user: [6](#0-5) 

`EvmHost` has no equivalent capture/refund step, so the "excess native token" bug class from the report (`createPool` not refunding overpaid native token) is reproduced — and worse, here the leftover funds are not merely retained by the contract for later recovery by the user; they become indistinguishable Host balance with no code path returning them to the original depositor.

### Impact Explanation
Any amount of `msg.value` sent to `dispatch()`/`fundRequest()` beyond what is exactly consumed by the Uniswap swap (due to quote staleness, front-running slippage price movement, rounding, or a caller intentionally/mistakenly sending a buffer as many integrations do, e.g. the LZ endpoint's quote applies "a generous 2x buffer") is silently absorbed into the `EvmHost` contract and never returned to the payer. This is a permanent loss of user funds for every native-token-paid dispatch across the protocol (POST, GET, and fee top-ups), not merely a slippage/rounding-dust issue, since it is fully deterministic on any overpayment.

### Likelihood Explanation
High. `swapETHForExactTokens` requires an input amount ≥ the exact tokens needed and will almost never consume the input exactly to the wei; callers routinely send a slight/generous buffer to account for router price fluctuation (as documented for the LZ endpoint's 2x buffer, and general quote/dispatch guidance). Every dispatch call from any app (HyperApp-based tokens, LZ endpoint, etc.) is exposed to this loss without any special conditions or admin actions required.

### Recommendation
Capture the `amounts` returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, compute `msg.value - amounts[0]`, and refund the difference to `_msgSender()` (mirroring the pattern already implemented in `IntentGatewayV2._post`/`placeOrder`).

### Proof of Concept
1. User calls `EvmHost.dispatch{value: 2 ether}(post)` where `post.fee` only requires 1 ETH worth of `feeToken` at current router price.
2. `swapETHForExactTokens{value: 2 ether}(post.fee, path, address(this), block.timestamp)` executes, consuming ~1 ETH and refunding the remaining ~1 ETH to `address(this)` (the `EvmHost` contract), per Uniswap V2 semantics.
3. `dispatch()` returns without ever transferring that ~1 ETH back to the user; it now sits in the `EvmHost` contract's balance, permanently unrecoverable by the user through any exposed function.
4. Repeat for any dispatching app that forwards a buffer `msg.value` (e.g. `HyperbridgeLzEndpoint.send` which intentionally quotes with a 2x buffer) — each such call leaks native token into the Host.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L296-306)
```text
        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            // Fee tokens already transferred to this contract by OFT's _payLzToken.
            // The quoted lzTokenFee includes a buffer above the relayer fee so the
            // legacy deployed host's per-byte protocol fee can be paid out of it;
            // approve our full feeToken balance and let the host take what it needs.
            address feeToken = IDispatcher(_host).feeToken();
            IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
            IDispatcher(_host).dispatch(request);
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
