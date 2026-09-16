Based on the investigation, I found a concrete analog to the Vault.claimTokens sandwich vulnerability in `EvmHost.dispatch()`'s native-token fee payment path.

### Title
Unprotected on-chain Uniswap swap in `EvmHost.dispatch()` native-fee path is sandwichable, forcing dispatchers to overpay ETH or have their message dispatch reverted/DoS'd - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `dispatch(DispatchGet)` allow any unprivileged caller to pay the relayer fee in native token, which triggers an on-chain `swapETHForExactTokens` call against the host-configured `uniswapV2` router/wrapper with no manipulation-resistant price check, exactly the missing-protection pattern described in the reference report.

### Finding Description
When a caller dispatches a POST or GET request with `msg.value > 0`, `EvmHost` swaps native ETH for exactly `post.fee` (or `get.fee`) units of the fee token via the configured router: [1](#0-0) [2](#0-1) 

The caller supplies `msg.value` as the implicit `amountInMaximum`, typically computed off-chain by calling the companion helper `HyperApp.quote()`, which itself is explicitly documented as unsafe on-chain because it reads the manipulable spot price from the same AMM: [3](#0-2) 

The project's own docs acknowledge this exact class of bug for `quote()`: "Do not call `quote()` in smart contract transactions. It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks." [4](#0-3) 

When the host's `uniswapV2` slot is configured to point at the `UniV3UniswapV2Wrapper` adapter (as documented for mainnet deployments), the swap is executed through Uniswap V3's `exactOutputSingle`, again bounded only by `amountInMaximum: msg.value`: [5](#0-4) 

Because the caller's `msg.value` is fixed from an off-chain quote taken before the transaction lands, an attacker who observes the pending `dispatch()` call in the mempool can sandwich the pool: buy the fee token pre-transaction to inflate its price relative to native token, forcing the swap's required input above the provided `msg.value` (causing it to revert), or manipulate price the other direction to extract MEV from the swap itself, then unwind after. Unlike the underlying report's exact scenario, the router's own `amountInMaximum` check prevents outright loss of extra ETH beyond what the caller sent, but this is the direct architectural analog: **an unchecked, at-transaction-time AMM price read feeding directly into a swap executed as part of a single unprivileged dispatch call**, with no TWAP/oracle deviation check as recommended in the reference report.

### Impact Explanation
A griefing/DoS vector against message dispatch: any unprivileged relayer/dispatcher paying fees in native token can have their `dispatch()` calls reliably front-run/sandwiched to revert, disrupting message delivery for that route, or forced to overpay via MEV extraction on the swap itself (the excess ETH beyond the fee-equivalent amount going to the sandwiching attacker rather than being refunded exactly). This does not rise to unbacked mint or direct escrow theft, but it is a concrete, reachable manipulation of a core dispatch primitive by any transaction submitter.

### Likelihood Explanation
High reachability — `dispatch()` is a permissionless, frequently-invoked entry point on every EvmHost deployment, and any app using `IDispatcher(host).dispatch{value}(...)` (the documented "Native Token Payment" pattern) is exposed. No privileged role is required to trigger or exploit the sandwich.

### Recommendation
Do not perform token swaps priced entirely within the same transaction as a bound derived from spot AMM state. Either:
- require an explicit caller-supplied `amountInMax`/slippage tolerance validated against a TWAP oracle deviation check, or
- restrict native-token fee payment to a pre-quoted, time-boxed commitment, or
- deprecate the native-payment swap path in favor of `dispatchWithFeeToken`, which the docs already recommend as the safe, non-slippage alternative.

### Proof of Concept
Not applicable as a fund-theft PoC — the router's own `amountInMaximum = msg.value` bound prevents the pool manipulation from directly draining more than the caller's supplied ETH; the concrete, provable effect is transaction revert/DoS or MEV extraction on the swap when the pool is sandwiched immediately before a pending `dispatch()` call, mirroring the "no manipulation check on same-block AMM price" root cause from the reference report.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-930)
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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L70-92)
```text
    /**
     * @dev returns the quoted fee in the native token for dispatching a POST request
     */
    function quote(DispatchPost memory request) public returns (uint256) {
        address _host = host();
        address _uniswap = IDispatcher(_host).uniswapV2Router();
        address[] memory path = new address[](2);
        path[0] = IUniswapV2Router02(_uniswap).WETH();
        path[1] = IDispatcher(_host).feeToken();
        return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
    }

    /**
     * @dev returns the quoted fee in the native token for dispatching a GET request
     */
    function quote(DispatchGet memory request) public returns (uint256) {
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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L125-149)
```text
        IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
            tokenIn: weth,
            tokenOut: path[1],
            fee: _params.maxFee,
            recipient: recipient,
            amountOut: amountOut,
            amountInMaximum: msg.value,
            sqrtPriceLimitX96: 0
        });

        bytes memory swapCall = abi.encodeWithSelector(IV3SwapRouter.exactOutputSingle.selector, params);

        bytes[] memory data = new bytes[](1);
        data[0] = swapCall;

        bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
        uint256 spent = abi.decode(results[0], (uint256));

        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```
