### Title
Attacker-controlled HyperSwap V2 pre-seed can overpower `_seedRebalancing`'s budget-capped swap, permanently locking graduation LP at an off-curve price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The AI-Arena report's root cause is that a favorable, precomputable output could be manipulated by choosing *when*/with what inputs to act, letting the attacker force a state that benefits them despite an attempted mitigation. The closest reachable analog in this codebase is `Bonding._seedRebalancing` / `_pairRebalance` / `_noFeeSwapInput`, which try to neutralize a hostile HyperSwap V2 pre-seed by swapping the pool back toward the curve-close ratio, but the corrective swap is capped at 99% of `Bonding`'s *own* graduation inventory rather than scaled to however large the attacker's pre-seed is. A sufficiently large pre-seed overwhelms that cap, so the pool is deposited into and locked at a price far from the curve's true close price.

### Finding Description
`finalizeGraduation` (`packages/contracts/src/Bonding.sol:1000-1034`) calls `_seedUniswapV2Direct`, which for a non-empty pool (`totalSupply != 0`) falls into `_seedRebalancing` (`Bonding.sol:1279-1354`). This function computes a corrective swap via `_pairRebalance`/`_noFeeSwapInput` (`Bonding.sol:1414-1522`), but the swap is bounded by `_swapBudget`, which is 99% of `Bonding`'s **own** LT/Token inventory for this graduation (`Bonding.sol:1374-1378`), not of the pool's reserves: [1](#0-0) 

If an attacker pre-creates the HyperSwap V2 pair for `(token, lt)` — both addresses are knowable ahead of graduation via `predictTokenAddress` and the creator-chosen `ltAddress` — and mints an initial liquidity position whose reserves are an order of magnitude larger than the protocol's own bounded graduation inventory (`tokensForLP ≤ LP_RESERVE = 250M`, `ltFromPair ≤` the curve's raised LT), then `_noFeeSwapInput`'s computed `s` (`Bonding.sol:1507-1522`) will exceed `maxSwap` and get clamped. The swap then cannot move the pool anywhere near the target ratio, yet `_routerDepositAndDispose` (`Bonding.sol:1449-1486`) unconditionally deposits the remaining inventory at whatever post-swap (still attacker-skewed) ratio results, using `addLiquidity(..., 1, 1, ...)`: [2](#0-1) 

There is no check comparing the resulting pool price to the cached curve-close ratio and no abort path — the deposit always proceeds, and the resulting LP tokens are immediately handed to the one-shot, non-recoverable `LPLock.recordLock` (`Bonding.sol:1031`), which "cannot skip" per the rules and has "no rescue path" per the contract's own natspec.

### Impact Explanation
This freezes/misallocates the protocol's entire curve-raised liquidity (LT and the LP-bound token allocation) into a HyperSwap V2 pool priced far from the curve's fair close price, permanently locked via `LPLock`. The attacker's own pre-existing, dominant LP share captures a disproportionate share of the arbitrage/trading-fee flow that subsequently corrects the pool toward fair value, effectively extracting value from the community-owned locked LP position that was funded by the curve's real traders and the creator's raised LT. This is a concrete "LP seeded away from the curve close price" outcome explicitly called out as in-scope impact.

### Likelihood Explanation
Reachable entirely by an unprivileged actor: pre-creating and pre-seeding a HyperSwap V2 pair for a not-yet-graduated (or even not-yet-launched, once the deterministic token/LT addresses are known) token requires no special privilege, and `finalizeGraduation` is explicitly permissionless (`packages/contracts/src/Bonding.sol:981-999`). The only capital requirement is exceeding the protocol's own bounded per-graduation inventory (`LP_RESERVE` tokens and the raised LT, both bounded and often modest relative to a capital-equipped attacker), which is achievable for high-value or highly appreciated LT/token pairs.

### Recommendation
Bound the acceptable post-rebalance deviation explicitly: after the swap, verify the resulting pool ratio is within a tight tolerance of the cached curve-close ratio (`tokensForLP / ltFromPair`) before calling `addLiquidity`; if the deviation exceeds tolerance (i.e., the pre-seed exceeds what the budgeted swap can correct), revert or route to a governance/keeper-mediated recovery path rather than silently depositing and locking at an uncorrected price.

### Proof of Concept
1. Before (or shortly after) `token` is launched, attacker computes the deterministic `token` address (`Bonding.predictTokenAddress`) and reads the creator-chosen `ltAddress` from `TokenInfo`.
2. Attacker calls the HyperSwap V2 `Factory.createPair(token, lt)` and `pair.mint(attacker)` with reserves sized to dwarf `LP_RESERVE` (250M tokens) and the maximum possible `ltFromPair`, at a ratio favorable to the attacker (e.g., under-pricing `lt` relative to `token`).
3. The token graduates normally via curve buys; `_enterGraduating` caches `(tokensForLP, ltFromPair)` at the true curve-close ratio.
4. Anyone calls `finalizeGraduation(token)`. `_seedRebalancing` computes the corrective swap size via `_noFeeSwapInput`, but it is clamped to 99% of `Bonding`'s own (much smaller) inventory (`_swapBudget`), so the swap barely moves the pool's ratio.
5. `_routerDepositAndDispose` deposits the remaining inventory at the still attacker-skewed ratio, minting LP tokens locked forever in `LPLock` at a price far from the curve's close price — the attacker's pre-existing majority LP share now captures disproportionate value as the market arbitrages the pool back toward fair value.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1316-1349)
```text
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
```

**File:** packages/contracts/src/Bonding.sol (L1466-1473)
```text
        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
            IERC20(tokenAddress).forceApprove(routerAddr, 0);
            IERC20(lt).forceApprove(routerAddr, 0);
        }
```
