### Title
Unbounded `body`/`to`/`dest` size in `EvmHost.dispatch(DispatchPost)` allows resource-exhaustion payloads with no relayer-fee cost basis - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)` accepts arbitrary-length `dest`, `to`, and `body` byte arrays from any caller with no upper-bound check, mirroring the HAL-27 finding of "lack of data sanitization and validation of limits" on a relay-facing dispatch endpoint.

### Finding Description
`dispatch(DispatchPost memory post)` builds a `PostRequest` directly from caller-supplied `post.dest`, `post.to`, and `post.body` and commits it to storage/events with no length checks: [1](#0-0) 
Unlike `BandwidthManager.purchase`, which explicitly bounds `app.length` against `MAX_APP_LENGTH` before dispatching (`if (app.length == 0 || app.length > MAX_APP_LENGTH ...) revert InvalidPurchase();`), [2](#0-1)  `EvmHost.dispatch` performs no equivalent validation on `body`, `to`, or `dest`. The struct definition itself places no bound on these fields either: [3](#0-2) 

Because the request is committed to `_requestCommitments` and emitted via `PostRequestEvent` with the full unbounded `body`, any address can dispatch requests with arbitrarily large `body`/`to`/`dest` payloads. These oversized commitments must subsequently be picked up, proven, and relayed by relayers/tesseract components and any `IIsmpModule`/pallet handling the corresponding message on the destination (e.g., via `pallet-ismp`'s `handle_unsigned`/`Message::Request` decoding path), all of which have to process attacker-controlled, unbounded-size data before any application-level rejection occurs.

### Impact Explanation
Because the dispatch fee model only charges an optional relayer `fee` in `feeToken` (which the payer sets and can legitimately set to zero for self-relay), an attacker can dispatch a POST request with an oversized `body`/`to`/`dest` and zero relayer fee, imposing unbounded storage/event/calldata cost on the source chain and unbounded downstream decoding/proof-verification/relaying burden with no economic cost proportional to payload size — this is a resource-exhaustion vector against the relay pipeline consistent with the HAL-27 bug class (DoS via oversized, unvalidated payloads on a message-relay endpoint).

### Likelihood Explanation
Likelihood is high: `dispatch(DispatchPost)` is a public, unprivileged entry point (`external payable`) reachable by any EOA or contract, requiring no special permissions beyond `notFrozen`, and no compile-time or runtime bound exists on payload size before the request is committed and event-emitted.

### Recommendation
Add explicit maximum-length checks on `post.dest`, `post.to`, and `post.body` (and the analogous `get.dest`/`get.keys`/`get.context` fields in `dispatch(DispatchGet)`) inside `EvmHost.dispatch`, reverting with a clear error when limits are exceeded, following the same pattern already used in `BandwidthManager.purchase`'s `MAX_APP_LENGTH` check.

### Proof of Concept
Call `EvmHost.dispatch(DispatchPost({dest: <valid>, to: <valid>, body: <multi-megabyte bytes>, timeout: 0, fee: 0, payer: msg.sender}))` from any address; the function proceeds to compute `request.hash()`, store `_requestCommitments[commitment]`, and emit `PostRequestEvent` with the full oversized `body` with no revert, as shown at [4](#0-3) , whereas comparable application-level dispatch paths such as `BandwidthManager.purchase` do bound their payload before dispatching, as verified by its own test suite (`testRejectsOversizedApp`) [5](#0-4) .

### Citations

**File:** evm/src/core/EvmHost.sol (L921-958)
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

        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
        emit PostRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: _msgSender(),
            to: abi.encodePacked(request.to),
            nonce: request.nonce,
            timeoutTimestamp: request.timeoutTimestamp,
            body: request.body,
            fee: post.fee
        });
```

**File:** evm/src/apps/BandwidthManager.sol (L153-159)
```text
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
```

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L23-42)
```text
struct DispatchPost {
    /// @notice Destination chain identifier (e.g., "POLKADOT-1000", "EVM-1")
    /// @dev Must be a valid state machine identifier recognized by the protocol
    bytes dest;
    /// @notice Destination application address or identifier
    /// @dev The receiving application on the destination chain
    bytes to;
    /// @notice The request payload
    /// @dev Arbitrary bytes that will be delivered to the destination application
    bytes body;
    /// @notice Timeout duration in seconds from the current timestamp
    /// @dev Request will be considered timed out after this duration
    uint64 timeout;
    /// @notice Fee paid to relayers for delivery & execution
    /// @dev Paid in the fee token specified by IHost.feeToken()
    uint256 fee;
    /// @notice Account responsible for paying the fees
    /// @dev If different from msg.sender, must have approved the Host contract
    address payer;
}
```

**File:** evm/tests/foundry/BandwidthManagerTest.t.sol (L166-171)
```text
    function testRejectsOversizedApp() public {
        bytes memory oversized = new bytes(manager.MAX_APP_LENGTH() + 1);
        vm.expectRevert(BandwidthManager.InvalidPurchase.selector);
        vm.prank(BUYER);
        manager.purchase(oversized, TIER1, 1, APP_CHAIN);
    }
```
