### Title
Permanent DoS of `finalizeGraduation` via `Math.mulDiv` overflow in the hostile-pre-seed rebalance math, triggered by an attacker-seeded HyperSwap V2 pair against a tiny cached `ltFromPair` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding._noFeeSwapInput`, called from the mandatory hostile-pre-seed rebalance path of `finalizeGraduation`, computes `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` on inputs that a pre-seeding attacker fully controls (`reserveIn`/`reserveOut`, the HyperSwap V2 pair reserves) combined with a protocol-derived divisor (`targetD = ltFromPair`) that can be driven to a tiny, near-zero value by any token launched against a BounceTech LT with a very high `exchangeRate()`. When the divisor is tiny and the numerator terms are moderate, the mulDiv quotient exceeds `type(uint256).max` and OpenZeppelin's `Math.mulDiv` reverts. Because `finalizeGraduation` has no fallback for this revert and the cached `PendingGraduation` values plus the attacker's on-chain V2 pool state are both immutable/persistent, every retry of `finalizeGraduation` fails identically — permanently freezing that token in `Lifecycle.Graduating` with all curve-raised LT and the reserved 250M LP tokens stuck inside `Bonding`.

### Finding Description
`_prepareGraduationLiquidity` caches `tokensForLP` (up to `LP_RESERVE = 250_000_000e18`, see [1](#0-0) ) and `ltFromPair` at phase-1 (`_enterGraduating`), computed as `assetReserve - _launchTimeVirtualLtReserve(...)` [2](#0-1) . Neither value is re-derived at phase 2; they are fixed forever once cached, by design (documented in `finalizeGraduation`'s natspec) [3](#0-2) .

`ltFromPair` is denominated in raw LT wei and is only bounded from below by the USD graduation threshold divided by the LT's live `exchangeRate()`: [4](#0-3) 
`_deployAndSeed` only rejects a launch when `virtualLtReserve` is too **large** (`exchangeRate` too low) via `ExchangeRateTooLow`: [5](#0-4) 
There is no floor on `exchangeRate` (or ceiling on it), so a token can be permissionlessly launched against an LT whose `exchangeRate()` is extremely high, in which case even the full $9,000 USD graduation threshold corresponds to a `realLtRaised`/`ltFromPair` of only a few wei.

At phase 2, if an attacker has already minted LP into the HyperSwap V2 TOKEN/LT pair before `finalizeGraduation` runs (explicitly a reachable, permissionless action per the analog rules — anyone can create/seed the V2 pair), `_seedUniswapV2Direct` routes into the rebalancing branch: [6](#0-5) 
`_seedRebalancing` reads the attacker's live V2 reserves and, when the pool is "LT-rich" relative to the cached target ratio (`reserveToken * ltFromPair < reserveLT * tokensForLP` — trivially satisfied when `ltFromPair` is tiny), calls `_pairRebalance` with `targetN = tokensForLP`, `targetD = ltFromPair`: [7](#0-6) 
`_pairRebalance` then calls `_noFeeSwapInput`: [8](#0-7) 
which computes `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)`. With `targetD` (`ltFromPair`) at or near 1 wei and `targetN` (`tokensForLP`) up to `2.5e26`, even modest attacker-controlled `reserveIn`/`reserveOut` (well below the `uint112` cap) make `reserveIn * reserveOut * targetN` exceed `2^256`, causing `Math.mulDiv` to revert with its overflow error. The contract's own comment on `_noFeeSwapInput` acknowledges this exact possibility but assumes it's out of the "safe envelope" without enforcing it on-chain: [9](#0-8) 

This is the same bug *class* as ALPINE-CVE-2022-27381: a specially crafted input (there, a crafted SQL statement into `Field::set_default`; here, a crafted V2-pool pre-seed ratio against a cheaply-obtainable low-`ltFromPair` token) drives an internal computation into an unhandled failure (there, a MariaDB crash; here, a Solidity revert) that a legitimate caller cannot avoid by retrying, causing a persistent Denial of Service.

### Impact Explanation
Once triggered, `finalizeGraduation` reverts unconditionally on every call for that token because:
- `pendingGraduation.tokensForLP` / `ltFromPair` are fixed and never recomputed,
- the attacker's hostile V2 pair reserves are permanent on-chain state that nothing in `Bonding` can reset,
- there is no owner/admin override, retry-with-different-parameters path, or emergency withdrawal for a `Graduating` token.

The token is permanently stuck in `Lifecycle.Graduating`. All curve-raised LT (the real value that crossed the $9,000+ graduation threshold) and the up to 250M reserved tokens sit frozen inside `Bonding` forever, and `LPLock.recordLock`'s one-shot lock for this token can never fire. This is a permanent freezing of trader/creator/LP funds — meeting the High-severity bar.

### Likelihood Explanation
Reachable entirely with unprivileged transactions: (1) launch or pick a token paired to a BounceTech LT with a very high `exchangeRate()` (permissionless via `Zap.createToken`), (2) buy tokens on the curve to accumulate TOKEN inventory and push the token toward graduation, (3) permissionlessly create the HyperSwap V2 TOKEN/LT pair and mint LP into it with any nonzero, disproportionate reserves before `finalizeGraduation` is called. Because `ltFromPair` can be driven down to just a few wei by the LT's exchange rate (a factor the attacker doesn't need to control, only needs to pick a token that already has one), the reserve sizes needed to blow the `mulDiv` quotient past `2^256` are modest relative to `uint112`'s range, making the attack practical rather than requiring maximal `uint112` values.

### Recommendation
- Enforce a minimum bound on `ltFromPair` (or on `tokensForLP / ltFromPair`) at phase-1 caching, or reject/graduate-guard tokens whose `ltFromPair` rounds to a dust amount.
- Replace the direct `Math.mulDiv` overflow-revert with a guarded computation (e.g., detect when the quotient would exceed `type(uint256).max` and fall back to `_seedDirectMint`, exactly as already done for the `s == 0` / `expectedOut == 0` dust cases) so that no attacker-reachable input combination can make `finalizeGraduation` permanently unrecoverable.
- Alternatively, cap the `exchangeRate()` accepted at launch (`_deployAndSeed`) with both an upper and lower bound so `ltFromPair` cannot become pathologically small relative to `tokensForLP`.

### Proof of Concept
1. Launch token `T` against LT `L` where `L.exchangeRate()` is very high (e.g., attacker deploys/selects an LT such that `graduationThresholdUsd * 1e18 / exchangeRate()` rounds down to `1` wei of LT).
2. Buy on the curve until `canGraduate(T)` is true; `_enterGraduating` caches `pendingGraduation[T] = {tokensForLP: X (up to 2.5e26), ltFromPair: 1, ...}`.
3. Before anyone calls `finalizeGraduation(T)`, attacker calls `IUniswapV2Factory.createPair(T, L)` and mints LP directly into that pair with reserves e.g. `reserveToken = reserveLT = 1e25` (self-funded, satisfying `reserveToken * 1 < reserveLT * X`).
4. Anyone calls `Bonding.finalizeGraduation(T)`. Execution reaches `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`, computing `Math.mulDiv(1e25 * 1e25, X, 1)` — the quotient exceeds `2^256` and the call reverts.
5. Every subsequent call to `finalizeGraduation(T)` reverts identically because `pendingGraduation[T]` and the attacker's V2 pair reserves are unchanged, permanently freezing `T`'s curve-raised LT and reserved tokens in `Bonding`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-485)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();

```

**File:** packages/contracts/src/Bonding.sol (L691-695)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L986-999)
```text
    /// @dev Exchange-rate drift between phase 1 and phase 2 is accepted by
    ///      design. The cached `(tokensForLP, ltFromPair)` are pure pair-
    ///      state arithmetic — see `_prepareGraduationLiquidity`, which
    ///      never reads `exchangeRate()` — so the LP opens at the exact
    ///      LT-per-token ratio the curve closed at, regardless of how long
    ///      phase 2 takes. What drifts is only the USD denomination of the
    ///      LT side, which is inherent to using a leveraged token as the
    ///      curve reserve: holders accept that exposure when they buy in.
    ///      A keeper Worker drives finalize within ~60s of `TokenGraduating`,
    ///      so the practical drift window is single-digit seconds. No
    ///      freshness timestamp / staleness gate: a recompute would return
    ///      byte-identical values (inputs are frozen while
    ///      `Lifecycle.Graduating`), and re-pricing the LP at the live
    ///      `exchangeRate()` would break the zero-gap-in-LT-units invariant.
```

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1089-1092)
```text
        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
```

**File:** packages/contracts/src/Bonding.sol (L1224-1234)
```text
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1333-1349)
```text
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

**File:** packages/contracts/src/Bonding.sol (L1498-1506)
```text
    ///      `Math.mulDiv` keeps the intermediate product
    ///      `reserveIn * reserveOut * targetN` inside its 512-bit working
    ///      space, but the final result `... / targetD` must still fit in
    ///      uint256. Call sites must keep that invariant — in practice
    ///      both the V2 uint112 reserve cap and the bound that
    ///      `tokensForLP` ≤ `LP_RESERVE` and `ltFromPair` ≤ raised LT
    ///      are well inside the safe envelope. Constructed adversarial
    ///      inputs that violate this would `revert` rather than silently
    ///      truncate, which is the correct failure mode.
```

**File:** packages/contracts/src/Bonding.sol (L1507-1522)
```text
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```
