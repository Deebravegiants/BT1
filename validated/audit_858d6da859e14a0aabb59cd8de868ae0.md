Confirmed: this wrapper's `swapETHForExactTokens` correctly refunds `msg.value - spent` to `msg.sender` (line 143-149). Since `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` all call `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(...)` directly forwarding `msg.value`, `msg.sender` inside that router/wrapper call context is `EvmHost` itself — not the original transaction caller (`_msgSender()`). So when a canonical Uniswap V2 router (or this wrapper) refunds the leftover ETH, it sends it back to `EvmHost`, and `EvmHost` has no logic to forward that refund on to `_msgSender()`. There's no `receive()`/refund-forwarding code in `EvmHost.sol` around these calls.

### Title
Excess native `msg.value` sent to `EvmHost.dispatch`/`fundRequest` is permanently trapped instead of refunded to caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` accept native token payment and swap it via Uniswap V2 for the exact fee amount using `swapETHForExactTokens{value: msg.value}(...)`. Any ETH refunded by the swap for unspent value goes to `EvmHost` (the direct caller of the router), not to the original transaction sender, and `EvmHost` never forwards it back.

### Finding Description
In `dispatch(DispatchPost)` [1](#0-0) , `dispatch(DispatchGet)` [2](#0-1) , and `fundRequest` [3](#0-2) , the full `msg.value` supplied by any caller is forwarded to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. This function only needs to spend enough ETH to acquire `post.fee` (or `amount`) worth of `feeToken`; per the Uniswap V2 Router spec, any unspent ETH is refunded to the caller of the swap — which, from the router's perspective, is `EvmHost`, since `EvmHost` itself invoked the function with the value attached. `EvmHost` does not capture this refund and relay it to `_msgSender()`; there is no such logic in the function bodies, nor a `receive()`/fallback with forwarding logic in the contract. As confirmed by the analogous, correctly-implemented wrapper `UniV3UniswapV2Wrapper.swapETHForExactTokens`, a proper implementation must explicitly compute `msg.value - spent` and send it back to the original caller [4](#0-3)  — a step `EvmHost` omits entirely for its own callers.

This is directly analogous to the referenced bug class (Olas M-20): a `msg.value` is accepted for a variable, quote-dependent cost (`post.fee`/dynamic swap output), and the excess above the actual cost is not refunded to the transaction originator, leaving it stuck in the contract.

Any unprivileged caller dispatching a POST or GET request via `IDispatcher(host).dispatch{value: msg.value}(...)` — the exact pattern documented and recommended in the SDK/HyperApp usage guides [5](#0-4)  and used by `HyperApp.dispatchWithFeeToken`-adjacent flows — is affected whenever they overestimate the required native amount (which is common practice, since developers are told to estimate fees client-side and typically add margin).

### Impact Explanation
Any ETH sent above the exact amount needed to acquire `post.fee`/`get.fee`/`amount` worth of fee tokens is permanently locked in `EvmHost` with no recovery mechanism for the original caller. Given fee-token/ETH price volatility between quote-time (off-chain estimate) and execution-time, and the general recommendation to over-provision `msg.value` to avoid `LowerThan`/swap-revert failures, this will affect a large fraction of dispatch calls across all Hyperbridge EVM deployments, leading to a continuous, protocol-wide drain of user funds into `EvmHost`, unrecoverable without an admin sweep function (none is defined in the reviewed contract).

### Likelihood Explanation
High. Overpayment of `msg.value` relative to the actual swap cost is a natural and expected outcome any time a user or integrating contract (e.g., `HyperApp.sendMessageWithNative`) supplies native value for a POST/GET dispatch, since exact fee-token pricing is not knowable precisely off-chain and slippage/price movement is normal. This requires no attacker — it is triggered by every regular user interaction that sends slightly more ETH than the swap consumes.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, after calling `swapETHForExactTokens`, compare `msg.value` to the actual amount spent (returned by the swap call, e.g. `amounts[0]`) and refund the difference to `_msgSender()` (or `tx.origin`, matching upstream `payer`), mirroring the pattern already implemented correctly in `UniV3UniswapV2Wrapper.swapETHForExactTokens` [4](#0-3) .

### Proof of Concept
1. User calls `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` only requires `0.1 ether` worth of ETH to acquire via the Uniswap V2 pool at the moment of execution.
2. `EvmHost` forwards the full `1 ether` to `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)` [6](#0-5) .
3. The router (or wrapper) refunds `0.9 ether` back to `msg.sender` of that call, which is `EvmHost` — not the user.
4. `EvmHost.dispatch` proceeds to build/emit the request and returns, never forwarding the `0.9 ether` refund to the user; the ETH remains stuck in `EvmHost`'s balance with no withdraw path exposed to the user.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-188)
```text
### Native Token Payment

For native token payments, dispatch directly and let the Host handle the Uniswap swap:

```solidity lineNumbers title="MyApp.sol"
contract MyApp is HyperApp {
    function sendMessageWithNative(
        bytes memory message,
        bytes memory dest,
        uint64 timeout,
        address to,
        uint256 relayerFee
    ) public payable returns (bytes32) {
        DispatchPost memory post = DispatchPost({
            body: message,
            dest: dest,
            timeout: timeout,
            to: abi.encode(to),
            fee: relayerFee,
            payer: msg.sender
        });
        
        // User must send enough native tokens to cover fees
        // The Host will swap native -> feeToken via Uniswap
        return IDispatcher(host()).dispatch{value: msg.value}(post);
    }
}
```
