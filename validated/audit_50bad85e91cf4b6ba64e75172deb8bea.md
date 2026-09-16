### Title
`EvmHost.dispatch` credits `post.fee`/`get.fee` to `_requestCommitments` without verifying the fee token was actually received from the swap - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept native token payment and swap it for the exact fee amount via `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`, then unconditionally record `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})` using the requested `post.fee`/`get.fee` value — never checking `IERC20(feeToken()).balanceOf(address(this))` before and after the swap to confirm that amount was actually credited to the host.

### Finding Description
In `EvmHost.sol`: [1](#0-0) 
and the analogous GET path: [2](#0-1) 

Both branches call `swapETHForExactTokens` on an external router (`_hostParams.uniswapV2`) and then, regardless of what the router actually delivered, stamp the fee metadata with the requested `post.fee` / `get.fee` value: [3](#0-2) 

This is the same root-cause pattern as the referenced Knox report: the credited amount is taken from the caller-specified/expected value rather than the measured `balanceOf` delta of the token actually received from the swap. `_hostParams.uniswapV2` is a configurable external contract (any contract satisfying `IUniswapV2Router02`, as seen with the custom `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper`/`GnosisUniswapV2Wrapper` adapters in this same codebase used to bridge V3/V4/Gnosis-style routers into the V2 interface) rather than a hardcoded, battle-tested Uniswap V2 pool. Any deviation between the interface's assumed guarantee ("swapETHForExactTokens delivers exactly amountOut or reverts") and the actual behavior of the configured router/adapter — e.g., a bug in one of the custom wrapper contracts, a router that returns success while delivering less than `amountOut` to `recipient`, or a `feeToken()` with non-standard transfer semantics — results in the host crediting a `FeeMetadata.fee` that is larger than what it actually holds.

This credited fee is later paid out from the host's own feeToken balance to relayers/payers in multiple places that trust `_requestCommitments`/`meta.fee` at face value: [4](#0-3) [5](#0-4) [6](#0-5) 

If the fee actually received from the swap is less than the amount recorded, the host will eventually pay out more feeToken than it received for that dispatch, using other users' escrowed feeToken balances — a shortfall/insolvency in the host's fee accounting, mirroring exactly the class of bug described in the report ("Credited amount can be calculated wrong... relies on Exchange contract" instead of checking the token balance before/after).

### Impact Explanation
If the configured router/adapter under-delivers relative to the requested `amountOut` (due to a bug in a custom adapter, non-conforming router, or unusual feeToken behavior) while still returning success, `EvmHost` will over-credit its own fee-token-denominated obligations (`_requestCommitments[commitment].fee`). These are unconditionally paid out later to relayers/payers on request completion or timeout, draining the host's feeToken reserves beyond what was actually deposited for that specific dispatch — a fund-accounting/insolvency issue that can cascade into other users being unable to redeem their rightfully escrowed fees. This satisfies "concrete theft or permanent freezing of funds" via unbacked fee crediting in the core dispatch path reachable by any unprivileged caller submitting a message dispatch.

### Likelihood Explanation
Every call to `dispatch(DispatchPost)`/`dispatch(DispatchGet)` paid with native token goes through this unchecked swap-and-credit path, so the vulnerable code is on the hot path for ordinary message dispatch (not an edge case). The severity is bounded by the correctness of the configured router: with a standard, unmodified Uniswap V2 router this is largely safe because `swapETHForExactTokens` is guaranteed by the AMM to deliver exactly `amountOut` or revert. However, the codebase already deploys and wires in multiple non-standard "V2-compatible" adapter contracts (`UniV3UniswapV2Wrapper`, `UniV4UniswapV2Wrapper`, `GnosisUniswapV2Wrapper`) behind the same `IUniswapV2Router02` interface used by `_hostParams.uniswapV2`, any of which could contain a bug (or interact with unusual fee-token behavior) that breaks the "exact output" guarantee the host implicitly relies on without verifying via balance check. Likelihood is Medium: it requires either a bug in the configured swap adapter or an edge-case token/router interaction, not a compromise of governance/keys.

### Recommendation
In `EvmHost.dispatch(DispatchPost)` and `dispatch(DispatchGet)`, snapshot `IERC20(feeToken()).balanceOf(address(this))` before performing the `swapETHForExactTokens` call, and after the swap compute the actual `received = balanceAfter - balanceBefore`. Use `received` (or require `received >= post.fee`/`get.fee`) when populating `_requestCommitments[commitment].fee`, instead of trusting the router-requested `post.fee`/`get.fee` value directly. This ensures fee accounting always reflects tokens actually held by the host, consistent with the balance-based approach already used elsewhere in this codebase (e.g., `IntentGatewayV2`'s fee-on-transfer handling and `SimplexPaymaster.swapAndDeposit`, which measures `address(this).balance` after the swap rather than trusting the router's return value alone).

### Proof of Concept
1. Governance/deployer configures `_hostParams.uniswapV2` to point at a custom router-compatible adapter (as the codebase already does for `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper`/`GnosisUniswapV2Wrapper`) that contains a bug causing it to return without actually delivering the full `amountOut` of `feeToken` to `recipient` (`address(this)` = the host) under some edge condition (e.g., partial-fill logic error, rounding, or a non-standard token in the path).
2. A user calls `EvmHost.dispatch(DispatchPost)` with `msg.value` and `post.fee = X`, triggering `swapETHForExactTokens(X, path, address(this), deadline)`. Due to the adapter bug, the host actually receives `Y < X` of `feeToken`.
3. `EvmHost` still records `_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: X})` — i.e., `X`, not the actually-received `Y`.
4. When the request is later handled/timed out, the host transfers `X` (not `Y`) of `feeToken` to the relayer/payer via `IERC20(feeToken()).safeTransfer(relayer, fee)`, paying out `X - Y` more than it received for this specific dispatch, drawn from the host's pooled feeToken balance (i.e., from other users' deposited fees) — an accounting shortfall that can be repeated to drain the host's fee token reserves.

### Citations

**File:** evm/src/core/EvmHost.sol (L841-847)
```text
        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L872-876)
```text
        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
```

**File:** evm/src/core/EvmHost.sol (L901-904)
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

**File:** evm/src/core/EvmHost.sol (L946-958)
```text
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
