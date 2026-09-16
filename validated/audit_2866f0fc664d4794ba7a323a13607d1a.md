## Title
Unprotected Uniswap V2 spot-price swap for fee payment in `EvmHost.dispatch`/`fundRequest` enables price-manipulation and permanent loss of overpaid native token — (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all convert user-supplied native token into the fee token by calling directly into an external, permissionless AMM (`IUniswapV2Router02.swapETHForExactTokens`), exactly as Rari Capital's ETH pool trusted the external Alpha Finance integration and was drained when that external protocol's economics were manipulated. Here the manipulable external dependency is a Uniswap V2 pool used with no slippage bound tied to a fair price and no real deadline protection, and any unprivileged transaction — a single `dispatch()`/`fundRequest()` call by any dispatcher — reaches this code path. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Each of these three entry points, when called with `msg.value > 0`, builds a two-hop swap path `[WETH, feeToken]` and calls `swapETHForExactTokens{value: msg.value}(feeAmount, path, address(this), block.timestamp)`: [4](#0-3) 

Three compounding defects mirror the "integration of an external protocol" root cause from the Rari incident:

1. **Spot-price dependency with no fair-value bound**: the router pulls its exchange rate from live Uniswap V2 reserves at execution time. There is no oracle, TWAP, or user-supplied `amountInMax`/minimum-output check independent of `msg.value` — the only bound on ETH spent is the full `msg.value` itself, so an attacker can manipulate the pool (e.g., via a flash-loan-funded sandwich) immediately around the victim's transaction to shift the ETH/feeToken exchange rate and extract the difference as arbitrage profit at the victim's expense.
2. **Non-functional deadline**: `deadline` is passed as `block.timestamp`, which is always satisfied at execution time regardless of how the transaction is ordered or delayed in the mempool by a relayer/MEV actor — this removes the one parameter Uniswap provides specifically to bound exposure to price movement between signing and execution.
3. **Unrecoverable dust**: `swapETHForExactTokens` refunds any unspent ETH (when the required input is less than `msg.value`) to the caller of the router, which is `address(this)` (`EvmHost`), not `_msgSender()`. `EvmHost` has no accounting or withdrawal path that returns this native-token dust to the original sender, so overpaid ETH becomes permanently stranded in the contract.

Because `dispatch()` and `fundRequest()` are the exact functions used to pay for POST/GET message dispatch and to top up relayer fees on pending requests — the core "unprivileged message dispatcher" path the scope explicitly calls out — this is directly reachable by any single transaction, not by a privileged actor.

### Impact Explanation
- Value extracted via price manipulation of the AMM leg used for fee payment is a direct, quantifiable loss to whichever account supplies `msg.value` to `dispatch`/`fundRequest`, funneled to whoever manipulates the pool around the transaction — analogous to the Rari loss caused by relying on a manipulable external protocol.
- The stranded-dust defect is a permanent freezing of funds: any caller who supplies more native token than the router's exact-output swap consumes loses that excess irretrievably, since `EvmHost` neither tracks nor refunds it.
- Both effects sit inside the message-fee-payment path, so they degrade the guarantee that dispatching a cross-chain message costs a bounded, predictable amount, which can also be leveraged to grief relayer fee funding (`fundRequest`) on pending requests.

### Likelihood Explanation
Every `dispatch()` or `fundRequest()` call that pays with native token (`msg.value > 0`) — the standard, encouraged UX path per the function's own docstring "swap under the hood using the local uniswap router" — exercises this code unconditionally. No special permissions, timing luck, or admin cooperation is required; only ordinary Uniswap V2 sandwiching capability (well within reach of any MEV searcher) is needed to profit from case (1), and simple imprecision in supplying `msg.value` guarantees dust loss in case (3) on essentially every such call.

### Recommendation
- Require callers to pass an explicit `amountInMax` (or minimum-output equivalent) derived off-chain, rather than implicitly bounding spend by the entire `msg.value`, so slippage/manipulation exposure is caller-controlled and bounded to a known tolerance.
- Replace `deadline: block.timestamp` with a caller-supplied deadline parameter so stale/delayed transactions revert instead of executing at an attacker-favorable block.
- After the swap, compute and refund any leftover native token (`address(this).balance` delta, or the router's returned `amounts[0]` vs `msg.value`) back to `_msgSender()` instead of letting it accumulate unaccounted in `EvmHost`.
- Consider using a TWAP-based or externally verified price feed to size the swap input, rather than relying solely on the instantaneous Uniswap V2 spot reserves.

### Proof of Concept
1. Attacker observes a pending `dispatch(DispatchPost)` (or `fundRequest`) transaction in the mempool that pays with native token.
2. Attacker front-runs with a large swap on the same Uniswap V2 `WETH/feeToken` pool used by `_hostParams.uniswapV2`, shifting the spot price so that acquiring `post.fee` feeToken units temporarily costs less ETH than fair value.
3. Victim's transaction executes: `swapETHForExactTokens{value: msg.value}(post.fee, [WETH, feeToken], address(this), block.timestamp)` succeeds using the manipulated rate; the difference between the fair price and the manipulated price is extracted by the attacker's back-run trade that restores the pool price and captures the arbitrage.
4. Independently, whenever `msg.value` exceeds the ETH actually required for the exact-output swap, the router refunds the excess to `address(this)`; since `EvmHost` has no bookkeeping or user-facing sweep for this balance (see the two `dispatch` and `fundRequest` implementations above), that excess is permanently unrecoverable by the original sender. [3](#0-2)

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
