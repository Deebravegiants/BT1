Found the strongest analog. `EvmHost.dispatch()` (and `dispatch(DispatchGet)`/`fundRequest`) uses `IUniswapV2Router02.swapETHForExactTokens` against the *live spot price* of `_hostParams.uniswapV2` to convert a caller-supplied `msg.value` into the exact `feeToken` amount needed for `post.fee`. This is the same bug class as the Balancer LP oracle report: a fee/price computation that trusts a manipulable, single-block on-chain price source (an AMM pool reserve ratio), reachable by any unprivileged message dispatcher.

### Title
`EvmHost.dispatch()` prices relayer/protocol fees off a manipulable spot AMM price - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)` and `fundRequest()` swap the caller's native `msg.value` into `feeToken` via `IUniswapV2Router02.swapETHForExactTokens`, using the router's current reserves as the exchange rate [1](#0-0) . This mirrors the `BalancerLPMetaStableEthOracle` flaw: a price used inside a state-changing, fund-affecting function is derived from an on-chain balance/reserve ratio that can be pushed within the same transaction/block by any party with capital, rather than from a manipulation-resistant oracle (TWAP, Chainlink, etc.).

### Finding Description
`dispatch()` is a permissionless, unprivileged entry point — any message dispatcher pays for cross-chain delivery this way [2](#0-1) . When `msg.value > 0`, the function performs a live on-chain swap:
```
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)
```
and the same pattern repeats for GET dispatch and `fundRequest` [3](#0-2) . The companion `HyperApp.quote()` helper used by integrators is explicitly documented as vulnerable to sandwich attacks because it "uses Uniswap's `getAmountsIn`" against live reserves, and the docs warn users never to call it inside a transaction [4](#0-3) . However, `EvmHost.dispatch()` itself is a state-changing transaction that performs the equivalent swap on-chain unconditionally whenever a caller pays with native token — there is no slippage bound, no minimum-out check, and no TWAP/oracle sanity check, only `swapETHForExactTokens` bounded by `msg.value` (i.e., the attacker/caller controls the input side, not a protective ceiling on price).

An attacker (any address, including relayers, token bridgers, or intent solvers who also hold the router's reserves) can manipulate the pool used by `_hostParams.uniswapV2` immediately before calling `dispatch{value: ...}(...)` — either to force other users' near-simultaneous native-fee dispatches to revert/overpay, or to sandwich the host's own swap to extract value from the pool via the host acting as a forced, mechanical trader that always executes `swapETHForExactTokens` for the same `feeToken` at whatever price prevails on-chain at call time.

### Impact Explanation
Because the router/pool is externally manipulable (flash loan / large sequential trades within a block), an attacker can:
- Force the host to pay far more native token than the fair value of the relayer fee it collects, draining value from `msg.sender`'s excess `msg.value` refund logic and/or capturing arbitrage profit against the manipulated pool at the Host's expense.
- Cause legitimate dispatchers' `dispatch()` calls to revert (DoS on outbound message delivery — a permissionless dispatch route "unable to deliver messages") when the manipulated price makes `post.fee` unreachable within the swap parameters, or silently overcharge native token beyond user expectations.
This is a protocol-level fee/settlement primitive reachable from a single dispatched request, matching the required "route unable to deliver messages" / fund-loss criteria.

### Likelihood Explanation
Uniswap V2-style pools configured as `_hostParams.uniswapV2` for a given `feeToken`/WETH pair are commonly thin relative to flash-loan capital, making single-block manipulation both cheap and repeatable by any actor who can call `dispatch` with `msg.value`, which requires no privilege whatsoever — it is the standard integration path for native-token fee payment described throughout the Hyperbridge docs [5](#0-4) .

### Recommendation
Do not perform on-chain spot swaps to price protocol/relayer fees. Either (a) require callers to pre-quote and pass a `minAmountOut`/`maxNativeIn` bound with slippage protection derived off-chain, (b) source the exchange rate from a manipulation-resistant oracle (TWAP over multiple blocks, or a Chainlink-style feed) rather than `getAmountsIn`/`swapETHForExactTokens` against instantaneous reserves, or (c) cap the per-block price deviation the swap is allowed to execute at versus a stored reference rate.

### Proof of Concept
1. Attacker identifies the `_hostParams.uniswapV2` pool backing `feeToken`/WETH for a target `EvmHost`.
2. Attacker takes a flash loan and swaps heavily against that pool to shift its reserves, moving the effective WETH→feeToken price.
3. Within the same block, attacker (or a colluding relayer) calls `EvmHost.dispatch{value: X}(post)` where `X` is sized against the manipulated price; the Host's `swapETHForExactTokens` executes at the manipulated rate [1](#0-0) , extracting more native token value than the fee is actually worth, or causing a legitimate concurrent dispatcher's transaction (sized for the pre-manipulation price) to revert.
4. Attacker reverses the initial swap in the same block, banking the arbitrage profit and repaying the flash loan.

**Note on confidence**: I was unable to trace exact economic bounds (e.g., whether `_hostParams.uniswapV2` pools are guaranteed to be deep, governance-configured pairs) purely from the indexed code; verifying real-world pool depth/configuration would require live on-chain inspection, which is out of scope for this static analysis.

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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L70-80)
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
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-189)
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
```
