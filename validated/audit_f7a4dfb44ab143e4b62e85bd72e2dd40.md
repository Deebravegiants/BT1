### Title
Missing `uint112` reserve-size validation before HyperSwap V2 LP seeding permanently bricks graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2018-20819's root cause is a missing check that a header-declared payload size could exceed the maximum representable/allocated size before it is consumed, causing an overflow. The analogous bug class in alt.fun is a missing check that the TOKEN/LT amounts credited to the HyperSwap V2 pair — under `Bonding`'s attacker-influenceable, permissionless two-phase graduation — cannot exceed `type(uint112).max`, the hard-coded reserve width real UniswapV2-style pairs use. Nothing in `_seedUniswapV2Direct` / `_seedRebalancing` / `_seedDirectMint` / `_routerDepositAndDispose` validates this bound before calling `pair.mint` / `router.addLiquidity`, so a sufficiently large pre-seed of the reserve LT can permanently overflow the real pair's reserve slot and brick `finalizeGraduation` for that token.

### Finding Description
`Bonding._deployAndSeed` bounds the **launch-time virtual LT reserve** against `type(uint112).max / 4` [1](#0-0) , reasoning that the curve's maximum raised LT (`3 × virtualLtReserve`, capped at `4 × virtualLtReserve` including the seed) can never exceed the pair's `uint112` reserve width. That check is scoped strictly to the **internal bonding-curve `Pair`** (`packages/contracts/src/Pair.sol`), whose `assetReserve`/`tokenReserve` are plain `uint256` and are never cast down — so the check is defensive, not load-bearing there.

The load-bearing spot is different: at graduation, `Bonding.finalizeGraduation` → `_seedUniswapV2Direct` deposits `tokensForLP` and `ltFromPair` into a **real HyperSwap V2 pair**, whose `reserve0`/`reserve1` ARE `uint112` (confirmed by `_seedRebalancing`'s own read: `(uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves()` [2](#0-1) ). The whole hostile-pre-seed defense (Regimes 1–3, `_pairRebalance`, `_routerDepositAndDispose`, `_seedDirectMint`) is engineered around ratio/price manipulation and dust seeds, and is explicitly documented as "MUST never revert under any pre-seed shape" [3](#0-2)  — but none of that logic validates that `reserveToken + tokensForLP` or `reserveLT + ltFromPair` stays under `type(uint112).max` before the direct `pair.mint`/`pair.swap`/`router.addLiquidity` calls fire.

The reserve asset is an externally-priced, rebasing BounceTech LT read live via `exchangeRate()`, `baseToLtAmount`, and `ltToBaseAmount` [4](#0-3) . When `exchangeRate()` is low (a devalued/highly-leveraged LT — the same "crashed exchange rate" state the test suite already models with `lt.setExchangeRate(0.0001 ether)` to isolate the supply-trigger/overflow-cap path [5](#0-4) ), `mint(baseAmount)` yields a proportionally enormous nominal LT amount for a modest USDC outlay, because `baseToLtAmount` scales with `1/exchangeRate` [6](#0-5) . An attacker who mints (or otherwise acquires) a very large nominal LT balance can `IERC20(lt).transfer` it directly to the freshly-created HyperSwap TOKEN/LT pair between phase 1 (`_enterGraduating`, which freezes the curve and caches `tokensForLP`/`ltFromPair`) and phase 2 (`finalizeGraduation`), inflating `reserveLT` toward `type(uint112).max`. When `finalizeGraduation` then adds `ltFromPair` (the curve-raised LT, parked and pending in `Bonding`) on top of that inflated balance via `pair.mint`/`addLiquidity`, the real HyperSwap pair's balance-to-reserve cast overflows `uint112`. A standard UniswapV2-derived pair reverts on this (`UniswapV2: OVERFLOW`), which — unlike the brick-resistance guarantees documented for ratio-skew and dust pre-seeds — is not defended against anywhere in `_seedUniswapV2Direct`'s three regimes.

### Impact Explanation
Because `finalizeGraduation` is the only path that can flip `lifecycle: Graduating → Graduated`, and phase 1 has already frozen trading and drained the curve-raised LT into `Bonding` via `Router.graduate` [7](#0-6) , a permanently-reverting `finalizeGraduation` call for a token leaves:
- All curve-raised LT (`ltFromPair`) and the 250M `lpReserve` tokens locked in `Bonding` forever, unreachable by any other function (`Router.graduate` is only ever called from `_prepareGraduationLiquidity`, which is unreachable once lifecycle has advanced past `Curve`) [8](#0-7) .
- Every trader/holder of that token permanently unable to trade (trading is frozen at `_enterGraduating` and never resumes since `Graduated` is never reached).

This is a permanent freeze of trader, creator, and protocol funds tied to that token — satisfying the "concrete... permanent freezing of trader, creator or LP funds" bar.

### Likelihood Explanation
Requires: (1) an LT whose `exchangeRate()` is low enough that nominal LT mintable-per-dollar is large (plausible for actively-leveraged/depreciated LTs, which the protocol's own test suite treats as a realistic state), and (2) enough attacker capital to mint/acquire and donate LT near `type(uint112).max` (≈5.19×10^33 raw units, i.e. ≈5.19×10^15 LT at 18dp) to the newly created pair before `finalizeGraduation` runs. This is a large but not obviously infeasible bar for a determined, capital-backed attacker especially against a low-exchange-rate LT, and the attack is purely permissionless (front-run `factory.createPair` + `transfer` + optional `pair.mint`, all already the documented threat model for this exact code path). I was not able to fully verify from the indexed contract sources whether any global cap exists on BounceTech LT mintable supply or whether `finalizeGraduation`/`_seedUniswapV2Direct` contains an as-yet-unindexed uint112 guard; this should be confirmed directly against `packages/contracts/src/Bonding.sol` lines ~1350-1470 and the real (non-mock) HyperSwap V2 pair behavior before treating this as fully proven.

### Recommendation
Before any `pair.mint` / `router.addLiquidity` call in `_seedUniswapV2Direct`'s regimes (and inside `_pairRebalance`/`_routerDepositAndDispose`), explicitly check that the resulting `balanceOf(pair)` for both TOKEN and LT will not exceed `type(uint112).max`, and define an explicit, non-reverting fallback (e.g., partial deposit, capped mint, or an admin/permissionless rescue path) for the case where a hostile or organic donation would overflow the real pair's reserve slot — mirroring the same "brick resistance MUST never revert" discipline already applied to ratio-skew and dust pre-seeds.

### Proof of Concept
Conceptual (constrained by the fact I could not execute code — this traces the reachable call sequence from the indexed sources):
1. Attacker (or market conditions) drives a BounceTech LT's `exchangeRate()` very low, as already modeled in `test_inv_overflowCap_refundsLt` via `lt.setExchangeRate(0.0001 ether)` [5](#0-4) .
2. Attacker mints or otherwise acquires a nominal LT balance close to `type(uint112).max` cheaply (low exchange rate ⇒ `baseToLtAmount` scales up for fixed USDC input).
3. A token's curve reaches the graduation trigger via normal `Zap.buy` traffic; `Bonding._enterGraduating` fires, freezing trading and caching `tokensForLP`/`ltFromPair`.
4. Before/while `finalizeGraduation` runs, attacker front-runs `factory.createPair(token, lt)` and `transfer`s their large LT balance directly to the pair (Regime 2/3 pre-seed, per `Bonding.sol` docs at lines 1132-1200).
5. `finalizeGraduation` → `_seedUniswapV2Direct` proceeds through its regime logic and eventually calls `pair.mint(lpLock)` / `router.addLiquidity` with the attacker's inflated LT balance plus `ltFromPair`, exceeding `type(uint112).max` on the real pair and reverting.
6. `lifecycle[token]` remains stuck at `Graduating` forever; `ltFromPair` and the 250M `lpReserve` tokens stay locked in `Bonding`; trading for that token never resumes.

### Citations

**File:** packages/contracts/src/Bonding.sol (L480-484)
```text
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
```

**File:** packages/contracts/src/Bonding.sol (L1287-1287)
```text
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
```

**File:** packages/contracts/AGENTS.md (L84-85)
```markdown
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
```

**File:** packages/contracts/AGENTS.md (L191-193)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L28-42)
```text
    /// @notice USDC per LT unit, 18-dp.
    function exchangeRate() external view returns (uint256);

    /// @notice Equals the LT amount that `mint(_, baseAmount, _)` will produce
    ///         at the current `exchangeRate()`.
    function baseToLtAmount(
        uint256 baseAmount
    ) external view returns (uint256);

    /// @notice Inverse of `baseToLtAmount`. The round-trip
    ///         `baseToLtAmount(ltToBaseAmount(x))` may differ from `x` by 1
    ///         wei due to integer-division rounding.
    function ltToBaseAmount(
        uint256 ltAmount
    ) external view returns (uint256);
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L330-351)
```text
    function test_inv_overflowCap_refundsLt() public {
        (address tokenAddr,) = _launchNoSeed();
        // Crash exchange rate so USD trigger never fires and we can isolate the supply
        // trigger & overflow-cap path.
        lt.setExchangeRate(0.0001 ether);

        uint256 balancePre = lt.balanceOf(trader2);
        // Grossly oversized buy that would attempt to absorb >1B tokens on the curve.
        // Real balance is 750M, so `Router.buy` must cap at 750M and back-calc the LT used.
        uint256 oversizedBuy = 1_000_000_000 ether;

        (uint256 tokensOut, uint256 amountInUsed) = _buy(tokenAddr, trader2, oversizedBuy);

        assertTrue(bonding.isGraduated(tokenAddr), "graduated on capped buy");
        assertTrue(amountInUsed < oversizedBuy, "buy must be capped below oversized request");
        assertEq(tokensOut, CURVE_SUPPLY, "tokensOut must equal remaining real supply");

        // `bonding.buy` pulls only `amountInUsed` from trader2 (via Router → pair + fees).
        uint256 balancePost = lt.balanceOf(trader2);
        uint256 ltConsumed = balancePre + oversizedBuy - balancePost;
        assertEq(ltConsumed, amountInUsed, "trader should only pay `amountInUsed`, not the requested amount");
    }
```

**File:** packages/contracts/src/Zap.sol (L324-324)
```text
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
```

**File:** packages/contracts/src/Router.sol (L184-202)
```text
    /// @notice Transfer exactly `amount` of LT out of the pair to the caller.
    ///         Called by `Bonding._prepareGraduationLiquidity` during graduation
    ///         with `amount = stored assetReserve - virtualLtReserve` (i.e. the
    ///         real LT raised by the curve, excluding the virtual seed).
    /// @dev    Donation-resistant: passing an explicit `amount` instead of
    ///         draining `assetBalance()` ensures any LT that was donated
    ///         directly to the pair via `IERC20.transfer` is left behind and
    ///         excluded from LP seeding.
    ///
    ///         "Locked" here is a trust-assumption claim, not an on-chain
    ///         guarantee. `Pair.transferAsset` is gated by `onlyRouter`, and
    ///         `Router` only exposes it via this function and `sell`. Both
    ///         require `BONDING_ROLE`, which only `Bonding` holds. `Bonding`
    ///         in turn only calls `graduate` from
    ///         `_prepareGraduationLiquidity` — which is unreachable once the
    ///         token's lifecycle has flipped past `Curve`. So the leftover
    ///         is unreachable as long as (a) `BONDING_ROLE` is not granted
    ///         to any other address, and (b) future `Bonding` upgrades
    ///         preserve the lifecycle gate.
```
