### Title
Native token overpayment during fee-swap dispatch is permanently trapped in `EvmHost` instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` to pay dispatch fees by swapping native token for the exact required amount of `feeToken` via `swapETHForExactTokens`. Uniswap V2's `swapETHForExactTokens` refunds any unused `msg.value` to whoever called the router — in this case that is `EvmHost` itself, not the original transaction sender. Any native token sent in excess of the exact fee required is therefore absorbed into the `EvmHost` contract balance rather than returned to the user, mirroring the reported bug class of bridging/dispatch functions mishandling `msg.value` and causing native funds to be frozen on the contract.

### Finding Description
In all three payable entry points, the pattern is identical: [1](#0-0) 

```
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    } ...
```

The router call is made with `amountInMax = msg.value` and `amountOut = post.fee`. `swapETHForExactTokens` uses only as much ETH as needed to obtain `post.fee` tokens and refunds the remainder ETH to the *caller of the router*, which is `EvmHost` (`address(this)` inside `dispatch`), not the end-user who sent the transaction. The same overpayment leak exists in the GET dispatch path [2](#0-1)  and in `fundRequest()` [3](#0-2) .

There is no logic anywhere in these functions that computes the exact fee required off-chain-perfectly and reverts on overpayment, nor any code that forwards the router's ETH refund back to `_msgSender()`. Any user who sends more native token than strictly required for the Uniswap swap (which is expected in practice, since users generally cannot predict the exact optimal `amountIn` for an exact-output swap and typically pad `msg.value`) has the surplus captured by the `EvmHost` contract balance permanently, unless a governance-only sweep function exists — which does not participate in normal user recovery flows.

This is directly analogous to the referenced Li.Fi finding: an unprivileged caller invoking a legitimate, in-scope entry point (`dispatch`/`fundRequest`) with a normal, easily-triggered `msg.value` mismatch causes native funds to become stuck in the protocol contract instead of being returned to the sender.

### Impact Explanation
Any unprivileged user calling `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` with `msg.value` even slightly larger than the exact amount needed to purchase `post.fee`/`amount` fee tokens will have the difference permanently absorbed into `EvmHost`'s balance. Because these are the primary, most commonly used entry points for a relayer, application, or end-user paying dispatch/relayer fees in native token (as documented in `docs/content/developers/evm/messaging/post-requests.mdx` and `idispatcher.mdx`), this affects any message dispatcher on any EVM deployment of Hyperbridge that supports native-fee payment. This is a permanent freezing/loss of user funds.

### Likelihood Explanation
High likelihood: this is not an edge case requiring an attacker or malicious actor — normal usage patterns (client-side fee estimation with a safety buffer, slippage tolerance, gas price fluctuations between quote and execution) will routinely cause `msg.value` to exceed the exact router-computed `amountIn`. Every such call permanently locks the difference. The SDK/docs explicitly instruct users to send `msg.value` for native payment without guaranteeing exact-amount computation client-side.

### Recommendation
- Capture the actual amounts spent from `swapETHForExactTokens` (it returns a `uint[] memory amounts` where `amounts[0]` is the ETH actually spent) and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`) at the end of `dispatch`/`fundRequest`.
- Alternatively, require the caller to pre-quote the exact `amountIn` off-chain and revert if `msg.value != amounts[0]`, consistent with the referenced report's recommendation to revert on unexpected/excess native value rather than silently absorbing it.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch{value: 1 ether}(post)` where `post.fee` only requires 0.5 ETH worth of `feeToken` via the configured Uniswap V2 pool.
2. `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)` swaps only the needed ETH and refunds the unused ~0.5 ETH to `msg.sender` of the router call — which is the `EvmHost` contract address, not the original caller.
3. The dispatch continues normally, emitting `PostRequestEvent` and returning a commitment; the caller never gets their surplus ETH back.
4. The surplus ETH now sits in `EvmHost`'s balance permanently, with no code path that returns it to the original sender. [1](#0-0)

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
