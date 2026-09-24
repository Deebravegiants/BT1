### Title
Hostile pre-seed of the HyperSwap V2 pair skews the graduated LP's opening price by exploiting the `totalSupply() == 0` classification in `_seedUniswapV2Direct` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedUniswapV2Direct` picks between a naive "empty pair" direct mint (`_seedDirectMint`) and a hardened rebalancing path (`_seedRebalancing`) purely on the predicate `IUniswapV2Pair(pair).totalSupply() == 0` [1](#0-0) . An unprivileged address can keep `totalSupply()` at `0` while making the pair's *reserves* arbitrarily large and arbitrarily ratio-skewed simply by calling standard, permissionless HyperSwap V2 `transfer` + `sync()` against the pre-created pair (never calling `mint`). This routes a large, skewed pre-seed through `_seedDirectMint`, which was documented and designed only for a "pristine empty pair" or truly tiny "dust" pre-seed, not for an unbounded donation.

### Finding Description
`_seedUniswapV2Direct`'s own natspec describes Regime 1 as: "A pristine empty pair, or a dust pre-seed (`transfer(pair, dust) + sync()` leaves `reserves > 0` but `totalSupply == 0`)... the pool opens at the curve-close ratio and any dust becomes reserves with no LP claim." [2](#0-1) 

This reasoning is only correct for the *LP-token count* minted, not for the *resulting pool price*. Standard UniswapV2 `mint()` semantics compute `liquidity` from `amount0/amount1` (i.e. `balance - reserve`, which correctly excludes the pre-seed since `sync()` already folded the donation into `reserve`), but the pair's new stored `reserve0/reserve1` after `_update()` are simply the post-transfer `balance0/balance1` — which *do* include the attacker's donation. `_seedDirectMint` unconditionally transfers `(tokensForLP, ltFromPair)` and calls `mint(lpLock)` with no reserve-size check at all: [3](#0-2) 

So if an attacker pre-seeds the pair with `(donationToken, donationLT)` in any ratio and any magnitude via `transfer` + `sync()` (both permissionless V2-pair calls, `mint` never invoked so `totalSupply()` stays `0`), the classification in `_seedUniswapV2Direct` still routes to `_seedDirectMint`. The resulting locked LP's reserves become `donationToken + tokensForLP` and `donationLT + ltFromPair`, whose ratio is skewed away from the intended curve-close price `tokensForLP / ltFromPair` by however much the attacker chose to donate — with no cap, unlike the analogous "dust" band (`DIRECT_MINT_PRESEED_BPS`) that *is* enforced inside `_seedRebalancing`'s Regime-3 handling for the same class of pre-seed [4](#0-3) .

The Regime-3 rebalancing path (`_pairRebalance` / `_routerDepositAndDispose`) is the actual "sandbox"/hardening mechanism the contract relies on to keep the LP price anchored to curve close in the presence of a pre-seed [5](#0-4) , but it is gated on `totalSupply() != 0`, so an attacker who never calls `mint()` (only `transfer` + `sync()`) never triggers it and escapes the defense entirely.

### Impact Explanation
`finalizeGraduation` is permissionless — anyone can call it once the token enters `Lifecycle.Graduating` [6](#0-5)  — and the LP it seeds is immediately handed to `LPLock.recordLock` with no rescue path [7](#0-6) . By pre-seeding the pair with a skewed ratio before calling/allowing `finalizeGraduation`, an attacker forces the permanently-locked LP to open at a price different from the curve-close price. Immediately after graduation the attacker (or any arbitrageur) can swap against the mispriced pool to extract value that was meant to back the locked liquidity — a direct value transfer out of the protocol's own locked LP, i.e. an "LP seeded away from the curve close price" with permanent freezing/misallocation of LP funds, matching the accepted impact class in the validation rules.

### Likelihood Explanation
Reachable by any unprivileged wallet: the HyperSwap V2 pair for `(token, lt)` is deterministically discoverable/creatable via `_ensureUniswapV2Pair` (the factory's `createPair` is itself typically callable by anyone on a standard V2 factory), and both `transfer` and `sync()` are standard permissionless functions on the pair. No special permission, timing precision, or capital efficiency beyond owning some of the token/LT is required, and the attack window is simply "before `finalizeGraduation` executes," which the protocol's own design keeps open for up to ~60 seconds under normal keeper operation and indefinitely if the keeper is delayed.

### Recommendation
Do not key the empty-pair/rebalance branch decision solely on `totalSupply() == 0`. Also check the pair's live reserves (`getReserves()`) before deciding: if reserves are non-negligible relative to `(tokensForLP, ltFromPair)` even when `totalSupply() == 0`, route through the same rebalancing/dispose logic used for Regime 3 (or apply the existing `DIRECT_MINT_PRESEED_BPS` band check unconditionally, not only inside `_seedRebalancing`), so that any economically meaningful pre-seed — minted or not — is rebalanced toward the curve-close ratio before the direct mint, rather than being silently absorbed into the locked LP's reserves.

### Proof of Concept
1. Token `T` reaches `canGraduate` and `triggerGraduation`/inline buy puts it into `Lifecycle.Graduating`, caching `(tokensForLP, ltFromPair)` in `pendingGraduation`.
2. Before anyone calls `finalizeGraduation`, attacker calls `Bonding._ensureUniswapV2Pair`-equivalent path is unnecessary if the pair doesn't exist yet — attacker can front-run: they cannot create the V2 pair before `_ensureUniswapV2Pair`, but if the pair already exists (e.g. from a previous failed/cancelled graduation attempt or is created for a different LT pair) they can directly:
   - `T.transfer(pair, largeTokenAmount)`
   - `LT.transfer(pair, largeLtAmountAtSkewedRatio)`
   - `IUniswapV2Pair(pair).sync()`
   leaving `totalSupply() == 0` but `getReserves()` non-zero and ratio-skewed away from `tokensForLP/ltFromPair`.
3. Anyone calls `Bonding.finalizeGraduation(T)`. `_seedUniswapV2Direct` sees `totalSupply() == 0` and calls `_seedDirectMint`, transferring `(tokensForLP, ltFromPair)` and calling `pair.mint(lpLock)`.
4. Post-mint pair reserves are `(largeTokenAmount + tokensForLP, largeLtAmountAtSkewedRatio + ltFromPair)` — priced off the attacker's donation ratio, not the curve-close ratio.
5. Attacker swaps against the now-mispriced, freshly-locked pool to arbitrage it back toward fair value, extracting value from the locked LP.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1002)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
```

**File:** packages/contracts/src/Bonding.sol (L1031-1031)
```text
        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);
```

**File:** packages/contracts/src/Bonding.sol (L1134-1143)
```text
    ///
    ///        1. **No LP minted yet — `totalSupply == 0` (~99% of
    ///           graduations).** A pristine empty pair, or a dust pre-seed
    ///           (`transfer(pair, dust) + sync()` leaves `reserves > 0` but
    ///           `totalSupply == 0`). Direct mint at exactly
    ///           `(tokensForLP, ltFromPair)` — V2's first-liquidity branch
    ///           makes those amounts the sole price input, so the pool opens
    ///           at the curve-close ratio and any dust becomes reserves with
    ///           no LP claim.
    ///        2. **Pure-donation pre-seed.** Attacker `transfer`'d to the
```

**File:** packages/contracts/src/Bonding.sol (L1155-1176)
```text
    ///        3. **Mint pre-seed.** Attacker called `pair.mint` against a
    ///           self-funded seed, baking a hostile (TOKEN, LT) ratio into
    ///           the pool. Without intervention `pair.mint(lpLock)`'s
    ///           `min(amount0·S/r0, amount1·S/r1)` formula would (a) open
    ///           the LP off curve-close-price and (b) donate the larger arm
    ///           to the attacker's pre-existing LP. We rebalance via a
    ///           direct `pair.swap` toward the curve-close ratio, then
    ///           deposit the remaining inventory via the router's
    ///           `quote()`-based `addLiquidity` — which only pulls the
    ///           optimal amounts at the post-swap ratio, so neither side
    ///           becomes a `min()` donation. Off-ratio TOKEN remainder is
    ///           burned; off-ratio LT remainder is auto-swept to the owner
    ///           by `finalizeGraduation`'s post-bookend (see its natspec).
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
```

**File:** packages/contracts/src/Bonding.sol (L1216-1226)
```text

        // Regime 1 — no LP minted yet (`totalSupply == 0`): a pristine empty
        // pair, or a dust pre-seed from `transfer(pair, dust) + sync()` that
        // leaves reserves non-zero while supply is still zero. Keying on
        // supply rather than reserves routes the dust shape here instead of
        // the rebalance path: with zero supply V2 mints from our amounts
        // alone, so the pool opens at the cached ratio and any dust becomes
        // reserves with no LP claim.
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1291-1302)
```text
        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }
```
