## Title
Excess native-token dispatch fees sent to EvmHost.dispatch()/fundRequest() are permanently stuck due to Uniswap swapETHForExactTokens refunding to the Host, not the user - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native-token payment via `msg.value` and swap it for the exact `feeToken` amount required using Uniswap V2's `swapETHForExactTokens`. This router function only spends as much ETH as needed and refunds any leftover ETH — but the refund goes to `msg.sender` of the router call, which is `EvmHost` itself, not the original caller who supplied the excess `msg.value`. Any leftover native token from over-funding a dispatch is thus trapped inside the `EvmHost` contract.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 

the contract calls:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
```
Uniswap V2's `swapETHForExactTokens` guarantees exactly `amountOut` (`post.fee`) tokens are bought, spending at most `msg.value` worth of ETH; any unused ETH is refunded to the caller of the router — which, here, is `EvmHost`, not the end user who called `dispatch{value: msg.value}(...)`. Because every real-world quote for `post.fee` is subject to price movement between off-chain estimation and on-chain execution, users are essentially forced to over-supply ETH as slippage buffer (as also documented: "Use the `quote()` view function from your frontend to estimate how much native token users need to send" — an off-chain, imprecise estimate) [2](#0-1) . The identical pattern exists in the GET-request dispatch path: [3](#0-2) 

and in `fundRequest`, used to top-up relayer fees on pending requests: [4](#0-3) 

None of these three functions compute or refund the ETH difference back to `_msgSender()`/`post.payer` after the swap. This is directly analogous to the reported Allo issue: any time a user (an unprivileged dispatcher of a POST/GET request, or anyone increasing a relayer fee) sends more native token than is strictly consumed by the swap, the surplus accumulates in the protocol contract and cannot be reclaimed by the user, since there is no mechanism in `EvmHost` that tracks or repays per-user native-token overpayment (only ERC20 `feeToken` refunds exist for timeouts, e.g. `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` [5](#0-4) ).

### Impact Explanation
This causes a permanent, protocol-wide freezing of user funds: every single native-token-funded `dispatch()` call or `fundRequest()` call that isn't an exact ETH match for the swap output leaves a residue of ETH stuck in `EvmHost`, with no way for the payer to retrieve it. Because virtually all callers (HyperApp-based apps, `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`, the LayerZero endpoint adapter, etc.) route native fee payments through this exact call pattern [6](#0-5) [7](#0-6) , this is a systemic loss vector affecting the entire native-token fee payment surface of Hyperbridge, not a one-off edge case.

### Likelihood Explanation
High likelihood: overpaying `msg.value` beyond the exact swap requirement is the normal, expected user behavior, since fees are estimated off-chain via `quote()` before the transaction and actual on-chain swap rates can shift due to AMM price movement between estimation and execution (explicitly warned about in the docs regarding sandwich-attack risk on `quote()`) [2](#0-1) . Any user or integrating dApp that adds a safety buffer to `msg.value` — a standard defensive practice — will trigger the loss on every transaction.

### Recommendation
After calling `swapETHForExactTokens`, compute the ETH actually consumed (or use the router's return value / `address(this).balance` delta) and refund any leftover native token to `_msgSender()` (for `dispatch`) or the appropriate payer (for `fundRequest`) before the function returns.

### Proof of Concept
1. A HyperApp calls `IDispatcher(host).dispatch{value: X}(post)` where `X` is intentionally larger than the current market-rate ETH cost of `post.fee` feeTokens (to buffer against slippage), e.g., `post.fee` requires 0.9 ETH but the caller sends `X = 1 ETH`.
2. Inside `EvmHost.dispatch`, `swapETHForExactTokens{value: 1 ETH}(post.fee, path, address(this), ...)` executes, spending only ~0.9 ETH and refunding ~0.1 ETH — to `EvmHost`, since `EvmHost` is `msg.sender` of the router call.
3. `EvmHost`'s native balance permanently increases by ~0.1 ETH with no corresponding accounting entry crediting the original caller.
4. Repeating this on every dispatch across all Hyperbridge-integrated apps continually accumulates unrecoverable ETH in `EvmHost`, matching the reported bug class of "excess native token constantly added to the protocol contract and stuck."

### Citations

**File:** evm/src/core/EvmHost.sol (L872-875)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
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

**File:** evm/src/core/EvmHost.sol (L974-986)
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L579-586)
```text
            // dispatch storage query request
            if (msg.value > 0) {
                // there's some native tokens left to pay for request dispatch
                IDispatcher(hostAddr).dispatch{value: msg.value}(request);
            } else {
                // try to pay for dispatch with fee token
                dispatchWithFeeToken(request);
            }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-273)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```
