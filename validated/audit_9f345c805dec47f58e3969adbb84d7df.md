### Title
Excess native `msg.value` sent to `EvmHost.dispatch()` / `fundRequest()` is permanently stuck in the contract instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept payment in native token by forwarding the caller's entire `msg.value` into `IUniswapV2Router02.swapETHForExactTokens`. That router function only needs enough ETH to buy the exact `fee`/`amount` of fee-token requested; any unspent ETH is refunded by the router — but to `msg.sender` of the router call, which is `EvmHost` itself, not the original transaction sender. None of these three functions capture or forward that refunded leftover balance back to the caller, so any native token sent in excess of the actual fee is silently absorbed into the `EvmHost` contract's balance with no code path to reclaim it.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

and identically in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

In all three, when `msg.value > 0`, the code calls:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);
```
`swapETHForExactTokens` only consumes the ETH required to purchase the exact `fee`/`amount` output; per the Uniswap V2 Router spec, any leftover ETH is refunded to `msg.sender` of that call. Since `EvmHost` is the direct caller of the router (not the original externally-owned account or app), the leftover ETH lands back inside `EvmHost`'s own balance — it is never routed back to `_msgSender()`/the original dispatcher. There is no subsequent line in any of these three functions that checks `address(this).balance` and forwards it back to the caller.

This mirrors the FootiumAcademy pattern exactly: a fee is computed/consumed (`post.fee`, `get.fee`, `amount`), the function accepts a `msg.value` that can exceed the required amount, and the excess is never refunded — it is stuck.

This is reachable by any unprivileged caller, since `dispatch()` and `fundRequest()` are the primary, permissionless entry points for message dispatch used by apps, intent contracts, and adapters (e.g., `HyperbridgeLzEndpoint.send()` forwards its entire `msg.value` to `IDispatcher(_host).dispatch{value: msg.value}(request)` without itself checking for leftover, based on the documented assumption that "Excess native is refunded by the uniswap router" — an assumption that only holds if the router's `msg.sender` were the original caller, which it is not): [4](#0-3) 

By contrast, the newer `IntentsBase`/`IntentGatewayV2` app-layer contracts correctly track their own `msgValue` and explicitly refund any leftover native token to `msg.sender` after dispatch (e.g. `_sendValue(msg.sender, msgValue)` in `ExtrinsicIntents.sol`): [5](#0-4) 

This confirms the project is aware refunding overpaid native token is required, but the core `EvmHost` dispatch/fund paths lack this handling for the leftover produced *after* the Uniswap swap.

### Impact Explanation
Any user, app, or relayer/adapter that estimates its required native fee with a safety margin (a documented and encouraged practice, e.g. the LZ endpoint's "generous 2x buffer") and calls `dispatch()`, `dispatch(DispatchGet)`, or `fundRequest()` with native token will have the unspent portion permanently locked inside `EvmHost`. There is no owner/admin sweep function identified in the reviewed `EvmHost.sol` sections for reclaiming a stray native ETH balance, meaning these funds are frozen indefinitely. Given `EvmHost` is a core, high-traffic contract used by every dispatching app on the chain, this can affect a large volume of transactions and value over time — a permanent freezing-of-funds condition for any overpaying caller.

### Likelihood Explanation
High likelihood of accidental triggering: native-token dispatch fee payment inherently requires the caller to estimate an amount to send before the swap executes (since the exact ETH price of `fee`/`amount` tokens at execution time isn't known precisely by the caller), so callers routinely include a buffer, exactly as documented in the LZ endpoint adapter. Every such call leaves the buffer stuck. No malicious actor is even required — this is a routine usage pattern that leads to loss.

### Recommendation
In `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, after calling `swapETHForExactTokens`, check `address(this).balance` (or track balance before/after the swap) and refund any leftover native ETH to `_msgSender()`, e.g.:
```solidity
uint256 balanceBefore = address(this).balance - msg.value;
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);
uint256 leftover = address(this).balance - balanceBefore;
if (leftover > 0) {
    (bool sent, ) = _msgSender().call{value: leftover}("");
    require(sent, "refund failed");
}
```
Apply the same pattern consistently to all three native-payment entry points in `EvmHost.sol`.

### Proof of Concept
1. Caller wants to dispatch a `DispatchPost` requiring `post.fee = 100` fee-token units.
2. Caller estimates the ETH cost with a safety buffer and calls `EvmHost.dispatch{value: 1 ether}(post)`, expecting only ~0.3 ETH to actually be needed.
3. `dispatch()` forwards `msg.value` (1 ether) to `swapETHForExactTokens{value: 1 ether}(100, path, address(this), deadline)`.
4. The router consumes only ~0.3 ETH to acquire 100 fee-token units and refunds the remaining ~0.7 ETH — to `msg.sender` of the router call, i.e., `EvmHost`.
5. `dispatch()` returns normally with the commitment; the 0.7 ETH now sits in `EvmHost`'s balance.
6. No function in `EvmHost.sol` allows the original caller (or anyone) to reclaim this 0.7 ETH — it is permanently stuck, repeating on every overpaid dispatch/fundRequest call.

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L296-298)
```text
        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L214-217)
```text
        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
