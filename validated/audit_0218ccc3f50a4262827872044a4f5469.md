Confirmed: `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all use `IUniswapV2Router02.swapETHForExactTokens` against a live, unprotected pool spot price — no TWAP, no slippage/price-deviation guard, no minimum-output/maximum-input bound beyond `msg.value` itself.

### Title
Native-fee dispatch relies on manipulable Uniswap V2 spot price with no oracle/TWAP guard, enabling fee-swap DoS and mispriced protocol fee collection - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert native-token payment into the protocol `feeToken` by calling `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` directly against the configured Uniswap V2 pool's live reserves, with no TWAP, no Chainlink/decentralized price reference, and no price-deviation bound.

### Finding Description
Any unprivileged caller can dispatch a `PostRequest`/`GetRequest` with native token value, or fund an existing request, and the exact ETH cost is priced entirely off the instantaneous spot price of the WETH/`feeToken` Uniswap V2 pair: [1](#0-0) [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` requests an *exact* output (`post.fee`/`amount` units of `feeToken`) and determines the ETH input from the pool's current reserves at execution time. Because a Uniswap V2 pool's reserves can be moved arbitrarily within a single transaction/block via a flash swap or a large same-block swap (the exact "manipulation via flash loans" concern the underlying report describes for `UniswapV2PoolTokenPrice.sol`), an attacker who controls or can influence the configured `uniswapV2` pair for the host's `feeToken` can:

1. Move the pool price against a pending/target `dispatch()`/`fundRequest()` call so the required ETH input exceeds `msg.value`, causing `swapETHForExactTokens` to revert — a griefing/DoS vector that can block message dispatch or block funding a request whose timeout refund depends on this fee metadata.
2. Move the pool price transiently favorable, then immediately reverse it, to make a same-block/same-transaction dispatch consume far less real ETH than the pool's fair value for the same `feeToken` output, degrading the fee actually collected by the protocol/relayer relative to what the relayer fee model assumes (`feeToken` ≈ USD-pegged value), because the `feeToken` amount delivered on-chain (`post.fee`) is fixed but the true economic cost paid by the attacker is manipulated downward.

There is no fallback to a decentralized price oracle, no TWAP sampling, and no bound comparing the live quote to any reference price — the documentation itself only warns against calling the *view* `quote()` off-chain due to sandwich risk, but the on-chain `dispatch()`/`fundRequest()` swap path has the identical exposure and is unavoidable for any native-token payer: [4](#0-3) 

### Impact Explanation
This is reachable by any unprivileged transaction sender dispatching a POST/GET request or funding one — no special privilege required. Manipulation of the swap path can (a) deny message dispatch/funding through reverts timed against manipulated reserves, disrupting the relayer-fee-funded delivery pipeline that outbound relaying depends on, or (b) let an attacker acquire the exact `feeToken` fee amount the protocol/relayer expects while paying less real value than the fee model assumes, undermining the fee-token-as-USD-proxy invariant the relayer economic model in `docs/content/developers/explore/relayers.mdx` relies on. This falls under manipulation of an unbacked/mispriced value transfer and a potential denial-of-message-delivery route, matching the Medium-severity bug class from the source report (spot-price manipulation instead of a decentralized oracle).

### Likelihood Explanation
Uniswap V2 spot-price manipulation within a single block/transaction (via flash swaps or large same-block trades) is a well-established, low-cost attack technique, and `EvmHost`'s configured `uniswapV2` router/pair for the `feeToken` is typically a low-liquidity, protocol-specific pair rather than a deep blue-chip market, making manipulation cheaper and more practical than on major pairs.

### Recommendation
Do not size native-token fee swaps directly off the live Uniswap V2 spot price. Either (1) restrict native-token dispatch to a pre-quoted maximum-input bound plus a price-deviation check against a TWAP or Chainlink feed for the `feeToken`/native pair, rejecting the swap if the live quote deviates beyond a configured tolerance, or (2) require pre-swapped `feeToken` payment (as already recommended for `dispatchWithFeeToken`) and treat native-token dispatch as a convenience path gated by an explicit maximum acceptable ETH price, refunding/reverting safely rather than trusting the instantaneous AMM price unconditionally.

### Proof of Concept
1. Attacker identifies (or deploys) the low-liquidity Uniswap V2 pool set as `_hostParams.uniswapV2`'s WETH/`feeToken` pair.
2. Within the same block as a victim's `dispatch(DispatchPost)` call (or via a preceding transaction in the same block), attacker executes a large swap against that pool to shift reserves, changing the ETH required for `swapETHForExactTokens(post.fee, ...)` to satisfy the exact `feeToken` output.
3a. If shifted unfavorably: victim's `msg.value` is now insufficient, `swapETHForExactTokens` reverts, and the victim's `dispatch()` transaction reverts — denying message submission with wasted gas.
3b. If shifted favorably (attacker as the dispatcher): attacker's own `dispatch()` call obtains the required `post.fee` `feeToken` amount while spending less ETH than the pool's fair-value price, then reverses the pool state in the same or next transaction — the protocol records the same `post.fee` in `FeeMetadata` as if fairly priced, while the attacker paid below fair value in real terms.

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

**File:** evm/src/core/EvmHost.sol (L974-982)
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
