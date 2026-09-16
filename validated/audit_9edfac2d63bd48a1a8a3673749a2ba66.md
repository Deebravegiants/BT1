### Title
Unprotected spot-AMM pricing in `EvmHost.dispatch()`/`fundRequest()` native-fee swaps enables sandwich attacks - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` convert a caller's native token into the exact fee-token amount required for a request by calling Uniswap V2's `swapETHForExactTokens` directly against the live pool reserves, with no independent slippage/price bound beyond the caller's own `msg.value`. The companion off-chain helper used to compute that `msg.value` (`HyperApp.quote()`/`quoteNative()`) is explicitly documented as reading the same manipulable spot price. This mirrors the reported `NomadFacet` issue: a dispatch-time price derived straight from a spot DEX quote, with no independent oracle or dedicated slippage guard, is sandwichable on every call.

### Finding Description
In `dispatch(DispatchPost)`:
```solidity
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) 

The identical pattern repeats for `dispatch(DispatchGet)` and `fundRequest()`. [2](#0-1) [3](#0-2) 

The exact-output amount (`post.fee`/`get.fee`/`amount`) is fixed, and the only bound on the ETH the Host is willing to spend is `msg.value` itself. Callers derive that `msg.value` from `HyperApp.quote()`, which reads the same pool's `getAmountsIn` on-chain:
```solidity
function quote(DispatchPost memory request) public returns (uint256) {
    address _host = host();
    address _uniswap = IDispatcher(_host).uniswapV2Router();
    address[] memory path = new address[](2);
    path[0] = IUniswapV2Router02(_uniswap).WETH();
    path[1] = IDispatcher(_host).feeToken();
    return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
}
``` [4](#0-3) 

The project's own documentation acknowledges this quote is sandwichable, but only warns against using it *inside a transaction* — it does not prevent the on-chain `dispatch()` swap itself from being sandwiched:
> "Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks." [5](#0-4) 

Because `dispatch()`'s internal swap always executes at whatever the live pool state is when the transaction lands — with no independent price oracle, TWAP check, or minimum-output enforcement beyond the attacker-influenced `msg.value` ceiling — an attacker can:
1. Observe a pending `dispatch{value: ...}(...)` call in the mempool.
2. Front-run it with a large buy of `feeToken` against WETH on the configured Uniswap V2 pair, pushing the WETH→feeToken price up.
3. Let the victim's `swapETHForExactTokens` execute, forcing the Host to spend a much larger fraction of `msg.value` in ETH to obtain the same fixed `post.fee` amount of `feeToken` (the price impact is realized as the attacker's arbitrage profit).
4. Back-run by selling the `feeToken` back, capturing the spread.

This is functionally the same root cause pattern as the report: a fixed target amount is filled by paying whatever a spot AMM quote demands, so the protocol/user absorbs the sandwiched slippage on every native-fee dispatch.

### Impact Explanation
Every unprivileged caller that dispatches a POST/GET request or funds a request using native-token payment (the documented, first-class payment path in `EvmHost`/`HyperApp`) is exposed to this on essentially every transaction, on every EVM chain running `EvmHost` with a Uniswap V2 router configured. Because dispatch volume is continuous and permissionless, an attacker running a bot can extract value from this path repeatedly across chains, similar in nature to the "millions in potential profit" scenario in the original report, transferring value from message senders/the protocol to the attacker with no privileged access required.

### Likelihood Explanation
High. No special permissions are needed — any address can dispatch a message with `msg.value`, and the swap parameters (fixed output, pool used, timestamp deadline) are fully predictable from the mempool, making this trivially sandwichable with standard MEV tooling on any chain where the configured Uniswap V2 pool for `WETH/feeToken` has thin liquidity relative to dispatch fee sizes.

### Recommendation
Do not settle native-token dispatch fees via an on-the-fly spot-price swap with only `msg.value` as a bound. Options: (a) remove automatic native→feeToken swapping from `dispatch()`/`fundRequest()` entirely and require callers to pre-acquire and approve the fee token (mirroring the report's resolution of removing automatic conversion and pushing responsibility to the caller/LP), or (b) require callers to pass an explicit `amountInMax`/`minAmountOut` slippage parameter validated against a manipulation-resistant reference price (e.g., a TWAP oracle) rather than relying purely on `msg.value` and the instantaneous pool state.

### Proof of Concept
1. Attacker monitors mempool for a `EvmHost.dispatch{value: v}(post)` call where `post.fee` is a fixed feeToken amount and `v` was computed off-chain via `HyperApp.quote()`.
2. Attacker front-runs with a swap on the same `uniswapV2` WETH/feeToken pair to move the price so that acquiring `post.fee` feeTokens now costs close to (but not more than) `v` ETH.
3. Victim's `dispatch()` executes `swapETHForExactTokens(post.fee, [WETH, feeToken], address(this), block.timestamp)` at the manipulated price [6](#0-5) , consuming far more ETH than the fair-price cost, with the excess captured by the attacker's position.
4. Attacker back-runs to close out the position, realizing profit equal to the price impact extracted from the Host's swap.

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

**File:** evm/src/core/EvmHost.sol (L1031-1040)
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
```

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L73-80)
```text
    function quote(DispatchPost memory request) public returns (uint256) {
        address _host = host();
        address _uniswap = IDispatcher(_host).uniswapV2Router();
        address[] memory path = new address[](2);
        path[0] = IUniswapV2Router02(_uniswap).WETH();
        path[1] = IDispatcher(_host).feeToken();
        return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
    }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
