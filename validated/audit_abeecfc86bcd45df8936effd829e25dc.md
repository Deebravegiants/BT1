### Title
None found — no valid analog matching the required scope

### Summary
I searched for the bug class described in the report — an unprivileged/permissionless code path that mandatorily depends on an external protocol (Synthetix) that is missing on certain chains, with the alternative path also reverting, producing a permanent DOS with no fallback. I found the closest structural analog in `EvmHost.dispatch()` / `fundRequest()` / `HyperApp.dispatchWithFeeToken()`, which swap `msg.value` for `feeToken` via a configured `IUniswapV2Router02` [1](#0-0) , and the same pattern in `IntentGatewayV2.placeOrder()` [2](#0-1) .

### Finding Description
Not applicable — see below.

### Impact Explanation
Not applicable — see below.

### Likelihood Explanation
Not applicable — see below.

### Recommendation
Not applicable — see below.

### Proof of Concept
Not applicable — see below.

---

**Why this does not qualify as a valid analog:**

Unlike the MODE `liquidationType2` case — where the caller (admin/relayer) has *no choice* and is forced down a hard-coded, chain-incompatible path once `liquidationType1` reverts — every reachable Hyperbridge path I found that depends on Uniswap V2 gives the caller an explicit, working alternative that does not depend on the AMM at all:

- `EvmHost.dispatch(DispatchPost/DispatchGet)` and `fundRequest()` only invoke `IUniswapV2Router02` when `msg.value > 0`; if the caller instead pays with `post.fee`/`amount` in the `feeToken` (`msg.value == 0`), the function takes the `IERC20.safeTransferFrom` branch and never touches the router [1](#0-0) [3](#0-2) .
- `IntentGatewayV2.placeOrder()` follows the identical pattern: native `msgValue` triggers the swap, otherwise `feeToken` is pulled directly via `safeTransferFrom` [2](#0-1) .
- The SDK explicitly documents this dual-rail design and tells integrators to fall back to `payInFeeToken: true` / direct fee-token payment on chains without a Uniswap router, confirming the fee-token rail is a first-class, always-available alternative rather than a broken secondary path [4](#0-3) .
- `BandwidthManager.purchase()`, a fully permissionless entry point reachable by any unprivileged caller, has no Uniswap dependency at all — it only ever pulls the fee token via `safeTransferFrom` [5](#0-4) .

So the "choice between two mechanisms, one of which is chain-incompatible" structure exists, but there is no scenario I could find, within the required reachable-path scope (`EvmHost`/`HandlerV2` dispatch, message encoding, consensus verification, state proofs, `pallet-ismp` `handle_unsigned`, MMR, token bridge mint/burn, intents escrow/bids, relayer fee accounting), where an unprivileged actor is *forced* onto the Uniswap-dependent branch with no viable fee-token alternative, analogous to the MODE report's forced `liquidationType2` fallback. The native-payment branch reverting on a chain lacking a Uniswap V2 deployment is a documented, expected condition with a working non-native alternative, not an unavoidable DOS of a core protocol function like liquidation.

I was not able to fully verify every downstream consumer of `_hostParams.uniswapV2` (e.g., all `HandlerV2`/relayer-incentive code paths) due to search/tool budget limits, so I cannot rule out with certainty that some narrower reachable path exists where the fee-token rail is unavailable and only the Uniswap rail is offered. If further investigation is desired, a Devin session with full repository access could specifically audit every caller of `IHost.feeToken()`/`uniswapV2Router()` to confirm no forced-native-only path exists on chains without a Uniswap V2 deployment.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-389)
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
```

**File:** docs/content/developers/sdk/hyper-fungible-token.mdx (L84-88)
```text
The fee estimation pipeline estimates gas for delivering the message on the destination chain, converts the destination gas cost to the destination fee token via Uniswap, scales decimals between source and destination fee tokens, then calls the on-chain `quote()` and `quote()` methods to get the final cost.

<Callout type="info">
`totalNativeCost` may be `0n` on chains without a Uniswap router. In this case, use `payInFeeToken: true` when bridging.
</Callout>
```

**File:** evm/src/apps/BandwidthManager.sol (L153-188)
```text
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);

        BandwidthPurchaseMsg memory body = BandwidthPurchaseMsg({
            app: app,
            tier: tier,
            months: months,
            chain: chain
        });

        commitment = IDispatcher(_host).dispatch(
            DispatchPost({
                dest: IDispatcher(_host).hyperbridge(),
                to: PALLET_BANDWIDTH_MODULE_ID,
                body: abi.encode(body),
                timeout: 0,
                fee: 0,
                payer: address(this)
            })
        );
```
