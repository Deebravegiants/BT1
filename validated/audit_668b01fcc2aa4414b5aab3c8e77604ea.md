### Title
`EvmHost.dispatch`/`dispatch(GetRequest)` prices native-fee swaps against a single, un-vetted Uniswap V2 pool with no minimum-liquidity or TWAP protection - ([File: evm/src/core/EvmHost.sol])

### Summary
When a caller pays the relayer fee in native token, `EvmHost.dispatch` (both the `DispatchPost` and `DispatchGet` overloads) swaps the supplied native token for the exact `feeToken` amount using a single, direct `WETH -> feeToken` hop on the configured `UniswapV2Router02`, with no liquidity check, no TWAP, and no protocol-side slippage bound — mirroring the reported `uniswapPriceAdaptor` issue where a single-pair spot quote is trusted without regard to how liquid that specific pair actually is.

### Finding Description
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` both execute: [1](#0-0) [2](#0-1) 

Both call `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` where `path = [WETH, feeToken()]`. This is a single direct pair, single spot-price read with no on-chain check of the pool's reserves/liquidity depth, and no admin-configured maximum acceptable price impact — exactly the pattern the referenced report calls out: not all tokens (here, the `feeToken`, e.g. DAI/USDC/a custom stablecoin) are guaranteed to be deeply liquid against native WETH on every deployed chain, especially on the many non-Ethereum-mainnet EVM chains Hyperbridge deploys to (`StateMachine.evm(...)` for L2s/sidechains where WETH/feeToken pools can be thin or even single-LP pools). `HyperApp.quote()`/`quote()` (used by app developers to estimate `msg.value`) reads the same router via `getAmountsIn`, so the estimate and the on-chain execution both depend on the instantaneous reserve ratio of one pool: [3](#0-2) 

Because `swapETHForExactTokens` is bounded only by `msg.value` (used implicitly as `amountInMax`), an attacker can manipulate the WETH/feeToken pool's spot price within the same block (flash-loan sandwich) immediately before a victim's `dispatch{value: ...}` call:
- Push the price so the swap needs *more* ETH than `msg.value` provides → the dispatch reverts, denying/griefing that request (denial-of-service on message dispatch for any app relying on native payment).
- Alternatively, move the price favorably mid-block so the swap consumes less ETH than intended, refunding the difference to `address(this)` (the `EvmHost` contract) — not to `post.payer`/`msg.sender`. There is no code in `dispatch` that captures or forwards a refund from the router call, so any leftover native token from the swap (which callers routinely over-supply as slippage buffer per the SDK/documentation's "1% buffer" pattern) is silently absorbed by `EvmHost` with no accounting or withdrawal path tied to that native balance, unlike `feeToken` revenue which the `IHostManager.withdraw` flow explicitly handles.

### Impact Explanation
This is directly reachable by any unprivileged caller who dispatches a POST/GET request paying with native token (`msg.value > 0`), i.e., core dispatch functionality used by every `HyperApp` integrator. On chains where the configured `uniswapV2` router's WETH/feeToken pool is shallow:
- Users can be forced to overpay (their buffer ETH is trapped in `EvmHost` permanently, since the contract has no logic to track or return excess native token from this swap), a freezing-of-funds condition for legitimate dispatchers.
- Message dispatch (the fundamental cross-chain messaging primitive `EvmHost.dispatch`) can be reliably DoS'd for any pair with thin liquidity via a same-block sandwich, since the swap has no fallback and simply reverts if the manipulated price requires more input than provided.

This satisfies the "route unable to deliver messages" and "freezing of funds" criteria for a valid analog.

### Likelihood Explanation
Any account can call `dispatch{value}(...)` — no privileged role is required. Sandwiching a single-pool spot price via flash-loan-funded swaps is a well-established, low-cost MEV technique, and Hyperbridge is deployed across many EVM chains where WETH/feeToken (or native/feeToken) Uniswap V2 pools are not guaranteed to be deep (unlike a mature Ethereum-mainnet DAI/WETH pool). Given `swapETHForExactTokens` uses live reserves with no TWAP smoothing and the caller-supplied `msg.value` is the only slippage bound, exploitation likelihood is moderate-to-high on any chain/pool with modest liquidity.

### Recommendation
- Add a maximum acceptable price-impact / minimum liquidity check before executing the swap (e.g., compare current reserves against a stored liquidity floor, or use a TWAP oracle instead of the router's instantaneous `getAmountsIn`/spot price).
- Track and refund any leftover native token from `swapETHForExactTokens` back to `post.payer`/`_msgSender()` instead of leaving it stranded in `EvmHost`.
- Consider allowing the caller to pass an explicit `amountInMax`/deadline rather than implicitly binding it to `msg.value`, and emit an event or revert with a clear reason distinguishing "insufficient value" from "excess liquidity risk."

### Proof of Concept
1. Deploy/observe `EvmHost` on a chain where the configured `uniswapV2` router's `WETH -> feeToken` pool has shallow liquidity (a realistic scenario for smaller EVM chains Hyperbridge supports).
2. Attacker takes a flash loan and swaps a large amount of WETH into the pool right before the victim's pending `dispatch{value: X}(DispatchPost{fee: F, ...})` transaction lands (front-run in the same block/mempool).
3. The pool's spot price shifts unfavorably; `EvmHost.dispatch` calls `swapETHForExactTokens{value: X}(F, [WETH, feeToken], address(this), block.timestamp)`, which now requires more than `X` ETH input and reverts — the victim's message dispatch fails (DoS), or, conversely, the attacker reverses their trade after a favorable shift so the swap succeeds using less than `X` ETH, and the un-refunded difference remains stuck in `EvmHost` (fund-freezing) as demonstrated by the absence of any refund-handling code in: [1](#0-0)

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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L73-92)
```text
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
