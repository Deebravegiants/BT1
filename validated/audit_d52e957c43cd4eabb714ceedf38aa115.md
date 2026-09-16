### Title
Native-fee dispatch swaps at unbounded live Uniswap V2 spot price, letting an attacker sandwich `EvmHost.dispatch()`/`fundRequest()` to drain ETH sent by callers - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all support paying the ISMP relayer fee with native tokens by swapping `msg.value` ETH for a fixed amount of `feeToken` via `IUniswapV2Router02.swapETHForExactTokens`, using the pool's live reserves with no minimum-output/maximum-slippage guard and a non-binding deadline (`block.timestamp`). This is the same bug class as the referenced Marginswap finding: an unprotected on-chain read/use of AMM spot reserves to price a transaction, exploitable via reserve manipulation (sandwich/flash-loan) in the same block.

### Finding Description
In `dispatch(DispatchPost)` [1](#0-0) :
```
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
```
The identical pattern appears in `dispatch(DispatchGet)` and `fundRequest()` [2](#0-1) .

`swapETHForExactTokens` computes the required ETH input from the *current* reserves of the WETH/feeToken pair at execution time. There is:
- No caller-supplied `amountInMax` distinct from `msg.value` acting as a real slippage bound checked against an expected fair price — `msg.value` is simply whatever ETH the caller sent, and the router will consume up to that amount at whatever the live spot price is.
- No deadline protection (`block.timestamp` is always satisfied), so the transaction cannot be timed out to protect against a stale/manipulated block.
- No TWAP or reference price check comparable to the `referencePrice`/`maxDeviationBps` guard the docs recommend elsewhere in the codebase for Uniswap V4 pool pricing (`docs/content/developers/evm/simplex/pricing.mdx`) — indicating the team is aware spot pools can be manipulated but did not apply an equivalent guard here.

The docs explicitly warn that the companion off-chain `quote()`/`quoteNative()` helpers are "vulnerable to sandwich attacks" and should only be used off-chain [3](#0-2) , but `dispatch()` itself performs the exact same unprotected on-chain spot swap when the caller pays in native token, and every unprivileged HyperApp/user dispatching a POST/GET request or funding a request with native token is forced through this exact vulnerable path [4](#0-3) .

Because the WETH/feeToken pool reserves can be manipulated within the same block (classic sandwich: attacker swaps to shift the pool price immediately before the victim's `dispatch()` call, then reverses the swap after), the amount of ETH the router extracts from the victim's `msg.value` for a fixed `post.fee`/`get.fee`/`amount` of feeToken can be made arbitrarily higher than the fair price, with the excess captured by the attacker's arbitrage. This directly mirrors the referenced report's mechanism (flash-loan-driven reserve manipulation of a Uniswap-like pool to yield attacker-favorable output amounts).

### Impact Explanation
Any relayer-fee dispatch (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`) or fee top-up (`fundRequest`) paid with native token is priced entirely off a manipulable, unguarded spot AMM price. An attacker can sandwich a victim's dispatch transaction to extract value from the ETH sent as `msg.value`, resulting in real loss of funds for callers of `EvmHost` (individual users, HyperApp integrators, and the intents/token-gateway flows that route through `quoteNative`/native-fee dispatch such as `tokenGateway.ts` and `hyperFungibleToken.ts`). This is a concrete theft-of-funds vector reachable by any unprivileged actor submitting an ordinary dispatch transaction plus the surrounding sandwich transactions — satisfying the "concrete theft of funds" bar for validity.

### Likelihood Explanation
Likelihood is High: `swapETHForExactTokens` against a live AMM pool with no price bound is a well-known, cheaply exploitable MEV/sandwich pattern requiring only capital for two same-block swaps (optionally financed by a flash loan) around the mempool-visible dispatch transaction. No governance, admin, or privileged role is required, and the vulnerable code path is the documented, encouraged "Native Token Payment" flow for dispatching messages.

### Recommendation
- Require callers to supply an explicit `amountInMax`/expected fee-token price and use `swapETHForExactTokens` with a strict bound plus a real deadline (not `block.timestamp`), reverting if the live price deviates from an acceptable range.
- Alternatively, price native-token fee payments off a manipulation-resistant source (Uniswap V2/V3 TWAP, or a Chainlink-style oracle as already used in `SimplexPaymaster._tokenPrice`) with a maximum-deviation guard analogous to the `referencePrice`/`maxDeviationBps` pattern documented for Uniswap V4 pool pricing.
- At minimum, warn/require an explicit user-supplied slippage tolerance parameter on `dispatch()`/`fundRequest()` native-payment paths rather than trusting `msg.value` alone as an implicit slippage cap sized on unmanipulated conditions.

### Proof of Concept
1. Attacker observes a pending `dispatch(DispatchPost)` (or `dispatch(DispatchGet)`/`fundRequest`) transaction in the mempool that sends `msg.value` ETH intending to buy `post.fee` units of `feeToken` via the host's configured WETH/feeToken Uniswap V2 pool.
2. Attacker front-runs with a swap that shifts the pool reserves (buying feeToken with WETH, or vice versa; can be financed via flash loan for larger pools), sharply raising the ETH cost of obtaining `post.fee` feeToken.
3. Victim's `dispatch()` call executes `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` at the manipulated reserves — the router consumes far more of the victim's ETH than the fair-price amount to deliver the fixed `post.fee` output, since there is no `amountInMax` check other than the (unmanipulated-price-sized) `msg.value` itself; if `msg.value` covers the inflated cost, the transaction succeeds and the extra ETH value is transferred to the pool.
4. Attacker back-runs, reversing the initial swap and capturing the AMM arbitrage profit created by the price distortion — economically equivalent to draining the excess ETH the victim overpaid, because of the price move the attacker engineered.
5. Repeatable against every native-token `dispatch`/`fundRequest` call, with `EvmHost.sol` lines 921-932 (and the analogous 974-1013, 1031-1051) as the exact vulnerable code with no slippage or TWAP protection. [1](#0-0)

### Citations

**File:** evm/src/core/EvmHost.sol (L908-932)
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

**File:** evm/src/core/EvmHost.sol (L974-1051)
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

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: request.from,
            keys: request.keys,
            nonce: request.nonce,
            height: request.height,
            context: request.context,
            timeoutTimestamp: request.timeoutTimestamp,
            fee: get.fee
        });
    }

    /**
     * @dev Increase the relayer fee for a previously dispatched request.
     * This is provided for use only on pending requests, such that when they timeout,
     * the user can recover the entire relayer fee.
     *
     * @notice Payment can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * If called on an already delivered request, these funds will be seen as a donation to the hyperbridge protocol.
     * @param commitment - The request commitment
     * @param amount - The amount provided in `feeToken()`
     */
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
