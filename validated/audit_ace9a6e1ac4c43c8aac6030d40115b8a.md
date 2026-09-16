## Analog Found

### Title
Flash-loan-manipulable AMM spot price in `EvmHost.dispatch()` native fee swap causes fund loss / trapped ETH for message dispatchers - (File: `evm/src/core/EvmHost.sol`)

### Summary
Both `dispatch(DispatchPost)` and `dispatch(DispatchGet)` on `EvmHost` accept native token (`msg.value`) as payment for the relayer fee and internally swap it for an exact amount of `feeToken` via a **live, unguarded Uniswap V2 spot price**, with no TWAP, no reference-price bound, and no minimum-output/maximum-input protection beyond the implicit revert of the router call itself. This is the same class of bug as the Dot.Finance incident: an on-chain contract makes a fund-affecting decision using the instantaneous reserves of an AMM pair that can be distorted within a single attacker-controlled transaction (flash loan).

### Finding Description
`dispatch()` for both POST and GET requests contains: [1](#0-0) 

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
```

and identically for `DispatchGet` at [2](#0-1) .

`swapETHForExactTokens` computes the required input amount from the pool's **current reserves** (`getAmountsIn`) at call time — there is no oracle, TWAP, or `referencePrice`/`maxDeviationBps`-style guard like the one Hyperbridge's own Simplex solver uses elsewhere for exactly this reason (`checkPriceGuard` in `sdk/packages/simplex/src/strategies/fx.ts`, documented at `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:1-22`) [3](#0-2) . `EvmHost.dispatch()` has no such protection at all, even though it is a core, unprivileged, single-transaction entry point reachable by any message dispatcher paying in native token.

The Uniswap V2 router itself refunds unused ETH to `msg.sender` of the swap call — which here is `EvmHost`, not the original transaction sender — because `EvmHost` calls the router directly rather than forwarding the caller's context. Any ETH sent above the manipulated `amountIn` is therefore captured by `EvmHost` rather than the dispatcher, with no visible sweep/refund path back to the payer in the surrounding function.

### Impact Explanation
An attacker can, within a single transaction, flash-loan-manipulate the reserves of the configured `uniswapV2` WETH/`feeToken` pair immediately before or during a call to `dispatch()`:
- By skewing the price favorably before their own `dispatch()` call, an attacker pays far less native ETH than the fair-market cost of the relayer fee token, siphoning value from the pool/LPs that back the host's fee-swap route while still getting `post.fee` credited to `_requestCommitments` for message delivery — an economically unsound trade the protocol facilitates without any price sanity check.
- By skewing the price adversarially against another pending `dispatch()` transaction (sandwich), the router's `getAmountsIn` for `post.fee` can be inflated beyond the victim's calculated `msg.value`, causing either a revert (denial of service on message dispatch) or, if the caller sent a buffer of ETH, an overpayment whose refund lands in `EvmHost` itself instead of the payer, with no clear recovery mechanism — a permanent-loss condition for the dispatcher.

This directly maps to the report's bug class ("flash loan attack" manipulating a pool-derived price to extract value / cause fund loss) and is reachable from a single unprivileged, unsigned-message-dispatch transaction, matching the required Hyperbridge dispatch path.

### Likelihood Explanation
Any EVM chain where `_hostParams.uniswapV2` points to a pool with shallow liquidity for the `WETH`/`feeToken` pair is exploitable with a standard flash-loan sandwich; this requires no privileged role, governance action, or off-chain component — only a single `dispatch()` call with `msg.value > 0`, which is core, everyday user functionality (posting a cross-chain message paying fees in native token).

### Recommendation
- Do not let `dispatch()` derive the ETH→feeToken exchange rate from the live, single-block Uniswap V2 spot price. Use a TWAP oracle, or require the caller to pass an explicit `amountInMax`/reference price with a bounded deviation check (mirroring `checkPriceGuard`/`maxDeviationBps` already used in the Simplex solver).
- Route the router's leftover-ETH refund back to the original caller (`_msgSender()`), not to `address(this)`, or explicitly account for and expose any ETH accumulated in `EvmHost` with a recovery path.
- Consider adding a minimum/maximum bound check on `getAmountsIn(post.fee, path)` before performing the swap, reverting if it deviates materially from a configured reference price.

### Proof of Concept
1. Identify an EVM chain where `HostParams.uniswapV2` is set to a pool with limited depth for `WETH`/`feeToken`.
2. In a single transaction: flash-loan a large amount of `WETH` or `feeToken`, swap against the pool to push the price in the attacker's favor, call `EvmHost.dispatch(DispatchPost{...fee: post.fee...})` with `msg.value` sized to the manipulated price (far below fair value), then reverse the flash-loan swap to restore the pool and repay the loan.
3. The dispatch succeeds, crediting `post.fee` feeToken to `_requestCommitments` for the relayer, funded at a fraction of the token's real market cost — extracting value from the pool's liquidity providers/arbitrage path in one atomic transaction, exactly analogous to the Dot.Finance flash-loan price-manipulation exploit.

*Note:* I could not fully confirm within the available index whether `EvmHost` exposes any admin/withdraw function capable of recovering ETH trapped by the refund-to-`address(this)` behavior; the six `grep` matches for `receive()/withdraw/payable(` in `EvmHost.sol` were not resolved to specific line content in this session. If a Devin session is started, this should be verified against the full file contents.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-930)
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L1-15)
```markdown
# Venue pricing (Uniswap V4 funded pairs)

Verified 2026-08-19.

```
resolveLegRates(...)
  curveless pair && token0 is a USD stable
    -> venuePriceMemo() -> getVenueUsdPrice(chain, token1)
         -> UniswapV4FundingPlanner.getExoticTokenPrice
              picks the position with the largest pool liquidity
              -> computeDirectPoolPriceUsd -> sdkPool.token0Price / token1Price
    -> checkPriceGuard(...)   reject if outside maxDeviationBps of the static reference
    -> rate = 1 / venueUsd
  otherwise -> the pair's ask/bid curve at the leg's notional
```
```
