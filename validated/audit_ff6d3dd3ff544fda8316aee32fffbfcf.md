Found the strongest analog: `EvmHost.dispatch()` (and `fundRequest`) swap native token for the `feeToken` via a live Uniswap V2 spot-price call (`swapETHForExactTokens`) with **no staleness check, no TWAP, and no slippage/deviation bound relative to any reference price** — this is executed atomically inside a single user transaction and is directly analogous to the reported `_calculateTroveRedemption` issue (using an unvalidated, manipulable spot price to value a cross-asset conversion that moves real funds). [1](#0-0) 

### Title
Fee-token swap in `EvmHost.dispatch()`/`fundRequest()` uses unvalidated Uniswap V2 spot price, enabling sandwich/price-manipulation arbitrage - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all convert a caller-supplied native-token payment into the host's `feeToken` by calling the local Uniswap V2 router's `swapETHForExactTokens` directly inside the dispatch transaction, using whatever spot price the pool currently reports, with `block.timestamp` as the swap deadline and no minimum/maximum bound derived from an external reference price.

### Finding Description
In `dispatch(DispatchPost memory post)`:
```solidity
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) 

The identical pattern repeats in `dispatch(DispatchGet memory get)` and `fundRequest()`: [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` prices the trade exclusively from the pool's current reserves (the router's on-chain spot price) — this is the same class of unvalidated price source the external report flags for `_calculateTroveRedemption`, which likewise consults a price feed without staleness/consistency checks before converting one asset's value into another. Here, the "price feed" is a live, atomically-manipulable AMM pool rather than an oracle, which is strictly weaker: any caller can move the pool price within the same transaction (flash loan or same-block sandwich) immediately before invoking `dispatch{value: ...}`, causing the router to require far more or return far less ETH than the fair-market cost of `post.fee`/`get.fee` feeToken units. The docs themselves acknowledge the underlying `quote()` helper is "vulnerable to sandwich attacks" and should never be called on-chain, yet the *actual* fee-paying swap executed unconditionally inside `dispatch()`/`fundRequest()` has exactly the same unmitigated exposure — with no oracle cross-check, no TWAP, and no caller-supplied `amountInMax`/slippage bound (the router will pull however much ETH the manipulated pool demands, up to `msg.value`). [4](#0-3) 

Any unprivileged account that dispatches a POST/GET request with `msg.value > 0` (a normal, permissionless entry point reachable from any application built on `HyperApp`, e.g. via `sendMessageWithNative`) exercises this vulnerable code path. Because it is triggered per-dispatch and pool state can be perturbed transaction-locally (e.g., a large swap in the same router pool immediately preceding the `dispatch` call, then reversed after), an attacker can force `EvmHost` to either (a) overpay in ETH for a fixed `feeToken` amount, extracting value from the contract/caller's excess ETH refund logic, or (b) manipulate the price so that a *victim's* dispatch consumes far more of the victim's supplied ETH than the fair-value fee, with the difference captured by the attacker's LP position via the sandwich.

### Impact Explanation
This directly threatens permanent loss of user funds during a core, universally-used dispatch entry point (every native-token-paying POST/GET message and `fundRequest` top-up passes through it). Because it is a router-priced spot swap with no slippage cap tied to a trusted reference and no staleness/TWAP defense, an attacker can sandwich any native-token dispatch to extract value from the swap, or force excess ETH consumption relative to fair market rate — satisfying "concrete theft ... of funds" via manipulated pricing on a message-dispatch path reachable by any single transaction.

### Likelihood Explanation
Likelihood is high: dispatching with native token payment is a normal, permissionless, frequently-used operation (it is the documented, recommended flow for apps that don't hold `feeToken`), the Uniswap V2 pools used are typically shallow relative to a well-funded attacker, and sandwiching a public mempool transaction against a known pool is a standard, low-cost MEV technique requiring no special privilege.

### Recommendation
Do not perform an unbounded spot-price swap atomically inside `dispatch()`/`fundRequest()`. Either (a) require callers to supply an explicit `amountInMax` bound checked against a TWAP or external price oracle before allowing `swapETHForExactTokens` to execute, (b) route the swap through a time-weighted price mechanism (e.g., Uniswap V3 TWAP oracle) with a maximum allowed deviation, or (c) require callers to pre-swap off-chain/via a dedicated slippage-protected transaction and dispatch only with the exact `feeToken` amount, removing the native-token convenience path from the trust-critical dispatch flow.

### Proof of Concept
1. Attacker identifies the `_hostParams.uniswapV2` pool pairing WETH and `feeToken()` used by `EvmHost`.
2. Attacker front-runs a pending `dispatch{value: X}(post)` call (or their own call) by swapping a large amount of WETH into the pool, moving the spot price so `feeToken` becomes artificially expensive in ETH terms.
3. The dispatch's internal `swapETHForExactTokens(post.fee, path, address(this), block.timestamp)` executes at the manipulated price, consuming much more of `msg.value` in ETH than fair value to obtain `post.fee` units of `feeToken`; any refund logic (or the victim's excess ETH) is captured relative to the true price once the attacker reverses their swap in the same block.
4. Repeated against low-liquidity `uniswapV2` deployments (per-chain configured in `HostParams`), this yields extractable value each time a native-token dispatch occurs, with no staleness or deviation check anywhere in `EvmHost.sol` to prevent it.

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

**File:** evm/src/core/EvmHost.sol (L1031-1039)
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
```

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L509-511)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
