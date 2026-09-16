### Title
Unprotected spot-price Uniswap V2 swap in `EvmHost.dispatch`/`dispatch(GetRequest)`/`fundRequest` lets a sandwiching attacker DoS message dispatch and drain excess ETH into the Host - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch`, `dispatch(DispatchGet)` and `fundRequest` — all callable by any unprivileged message dispatcher paying in native token — convert `msg.value` into the exact `feeToken` amount owed by calling `IUniswapV2Router02.swapETHForExactTokens` directly against the live, spot reserves of a single local Uniswap V2 pool, with no TWAP, no minimum-price bound, and no slippage/oracle sanity check beyond the caller's own `msg.value`. [1](#0-0) 

### Finding Description
The report's core defect is "an unbounded/manipulable AMM-derived price used directly to gate a protocol-critical action, with no TWAP/oracle protection." `EvmHost` reproduces exactly this pattern for fee collection instead of price validation: on every native-token-funded `dispatch`, `dispatch(GetRequest)`, and `fundRequest` call, the contract reads the *current* reserves of the configured `uniswapV2` pool (`WETH -> feeToken`) via `swapETHForExactTokens`, with `deadline = block.timestamp` (i.e., effectively no deadline protection) and no `amountInMax` other than whatever `msg.value` the caller happened to send: [2](#0-1) [3](#0-2) [4](#0-3) 

The same unguarded pattern is duplicated in `IntentGatewayV2`'s fee-escrow path, which also swaps native value for `feeToken` via the host's configured Uniswap V2 router at spot price with no protection: [5](#0-4) 

The project's own documentation flags this exact class of risk for the *off-chain* `quote()` helper ("uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks... only use it off-chain"), but the on-chain `dispatch`/`fundRequest` code paths that actually move value have no equivalent protection built in: [6](#0-5) 

Because there is no bound on the acceptable native/feeToken exchange rate (no reference price, no TWAP, no max-deviation check comparable to what `SimplexPaymaster`/Simplex's Uniswap V4 venue pricing implement elsewhere in this codebase via `referencePrice`/`maxDeviationBps`): [7](#0-6) 
an attacker can manipulate the pool's instantaneous price in the same block as a victim's `dispatch`/`fundRequest` transaction (classic sandwich, or via flash-loan swap) to move the required `amountIn` of native token for the exact fee-token output above what the victim supplied as `msg.value`, causing `swapETHForExactTokens` to revert with `EXCESSIVE_INPUT_AMOUNT`. This is directly reachable by anyone dispatching an ISMP message — the most fundamental unprivileged action in the protocol.

### Impact Explanation
This maps to the "route unable to deliver messages" acceptance criterion: an attacker can reliably grief message dispatch for any application relying on `EvmHost.dispatch`/`fundRequest` native-token payment by sandwiching the pool immediately before the target's transaction, forcing legitimate dispatches to revert (denial of service on cross-chain messaging), and can repeat this cheaply/profitably using flash loans against a thin native/feeToken pool. Additionally, because `swapETHForExactTokens`'s router refunds any *unused* ETH to the caller of the router — which here is `EvmHost` itself, not the original `_msgSender()` who funded the call — price manipulation that shifts the swap in the attacker's favor around block boundaries can leave leftover ETH permanently stranded in `EvmHost` rather than returned to the original payer, a value-loss vector for message dispatchers.

### Likelihood Explanation
High likelihood: this affects the primary entry point of the protocol (`dispatch`) and requires no privileged access — only capital to manipulate a single AMM pool's reserves for one block, which is a well-understood, cheap MEV/sandwich pattern, especially for Uniswap V2 pools that are typically shallow relative to flash-loan liquidity.

### Recommendation
Do not rely on the instantaneous Uniswap V2 spot price for a value-bearing swap with no bound. Add an `amountInMax` derived from a manipulation-resistant reference (e.g., a short TWAP over the pool, a governance-configured max native/feeToken rate, or an external price oracle) and enforce it in `dispatch`/`dispatch(GetRequest)`/`fundRequest`, reject the swap if it deviates beyond an acceptable band (mirroring the `referencePrice`/`maxDeviationBps` pattern already used in Simplex's Uniswap V4 venue pricing), refund any unspent native token back to `_msgSender()` rather than leaving it in the Host, and set a real deadline rather than `block.timestamp`.

### Proof of Concept
1. Attacker observes a pending `dispatch(DispatchPost{...})` transaction in the mempool that will send `msg.value = X` ETH, expecting `swapETHForExactTokens` to convert it to `post.fee` units of `feeToken` at the pool's current price.
2. Attacker front-runs with a large `WETH -> feeToken` swap (or flash-loan-funded swap) on the same `uniswapV2` pool configured in `_hostParams.uniswapV2`, sharply raising the ETH price of `feeToken`.
3. The victim's `dispatch` call now requires `amountIn > X` ETH to obtain `post.fee` feeToken units; `swapETHForExactTokens` reverts with `UniswapV2Router: EXCESSIVE_INPUT_AMOUNT`, and the victim's message dispatch fails.
4. Attacker back-runs to restore the pool and can repeat this against every native-funded `dispatch`/`fundRequest` call, effectively creating a persistent DoS on that Host's ability to accept native-token-funded message dispatches, or forcing every application relying on native payment to over-provision `msg.value` with unpredictable safety margins. [1](#0-0)

### Citations

**File:** evm/src/core/EvmHost.sol (L908-933)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param post - post request
     * @return commitment - the request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L961-985)
```text
    /**
     * @dev Dispatch a GET request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param get - get request
     * @return commitment - the request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L1031-1051)
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

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-480)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-84)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.

```toml lineNumbers
[vault.uniswapV4]
# referencePrice is the expected cNGN per USD;
# reject if the quote is more than 2% off.
# The two go together — one without the other is rejected.
[[vault.uniswapV4.positions]]
chain           = "EVM-8453"
tokenId         = "2087350"
referencePrice  = "1575"
maxDeviationBps = 200
```
```
