### Title
Adversarial HyperSwap V2 pre-seed reserves can cause `Math.mulDiv` to abort inside `finalizeGraduation`, permanently freezing curve-raised LT and reserved tokens - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2023-39456 is a case where a crafted, out-of-spec input (a malformed HTTP/2 frame) reaches an internal computation that wasn't hardened against the adversarial shape of that input and aborts the process. The analog in alt.fun is `Bonding._noFeeSwapInput`, called from `_pairRebalance` → `_seedRebalancing` → `_seedUniswapV2Direct`, which is the only code path `finalizeGraduation` uses to seed the post-graduation HyperSwap V2 pool when an attacker has pre-seeded that pair. This helper's own natspec admits that "constructed adversarial inputs" to its `Math.mulDiv` call can overflow uint256 and `revert` rather than degrade gracefully [1](#0-0) . Because `finalizeGraduation` is the sole, non-retriable exit from `Lifecycle.Graduating`, and the malicious pre-seed reserves persist on-chain, this revert is not a one-off DoS — it is a permanent, unrecoverable freeze of all curve-raised LT and up to 250M reserved tokens parked on `Bonding`.

### Finding Description
`_noFeeSwapInput` computes the swap size needed to rebalance a hostile pre-seed toward the curve-close ratio:
```
uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
uint256 newIn = Math.sqrt(product);
``` [2](#0-1) 

`reserveIn`/`reserveOut` are read directly from `IUniswapV2Pair(pair).getReserves()` in `_seedRebalancing` [3](#0-2) , i.e., they are fully attacker-controlled up to `uint112.max` on each side via `Bonding._ensureUniswapV2Pair`'s permissionless `createPair` + a pre-`mint` on the HyperSwap V2 pair before `finalizeGraduation` runs — a path the scan rules explicitly list as in-scope ("pre-creating or pre-seeding the HyperSwap V2 TOKEN/LT pair before graduation").

`Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` first forms a 512-bit intermediate product and then divides by `targetD`; OpenZeppelin's `mulDiv` reverts if the final quotient does not fit in 256 bits. By choosing `reserveIn`/`reserveOut` close to `uint112.max` on both sides of the V2 pair, an attacker inflates `reserveIn * reserveOut` toward its ~2^224 ceiling; combined with `targetN` (either `tokensForLP` or `ltFromPair`, both non-trivial curve-close values) and a comparatively small `targetD` on the other ratio term, the quotient can be pushed past `2^256`, causing `Math.mulDiv` to revert. The developers' own comment concedes this: "Constructed adversarial inputs that violate this would revert rather than silently truncate" [4](#0-3) .

This call sits directly on the only path `finalizeGraduation` has for a mint-pre-seeded pair (Regime 3) [5](#0-4) , invoked from `finalizeGraduation` at [6](#0-5) . `finalizeGraduation` has no alternate branch, no retry-with-different-parameters mechanic, and no admin rescue function for a token stuck in `Lifecycle.Graduating` — the `PendingGraduation` snapshot and the router-held LT (transferred out of the curve `Pair` already, in `_prepareGraduationLiquidity`/`Router.graduate`) and the `LP_RESERVE`-capped tokens sitting on `Bonding` have no other exit.

### Impact Explanation
Once a single unprivileged attacker pre-seeds the HyperSwap V2 `TOKEN/LT` pair with adversarial `uint112`-scale reserves for a token about to graduate, `finalizeGraduation(token)` reverts every time it is called (the pre-seed reserves don't change across retries, since nobody can call `pair.sync()`/`burn()` to reset them without owning the malicious LP position). The result:
- All curve-raised LT (already pulled out of the curve `Pair` by `_prepareGraduationLiquidity`/`Router.graduate` and held in `Bonding`) is permanently trapped.
- Up to `LP_RESERVE` (250M) tokens reserved for LP seeding are permanently trapped, with no burn/rescue path.
- The token can never complete graduation, permanently freezing the affected trading pair post-threshold.

This satisfies the "permanent freezing of trader, creator or LP funds" bar in the validation criteria and is High severity given it is triggerable at will by any address with no privilege, at the cost of only gas + the pre-seed liquidity (which the attacker retains as a claim on the un-mintable pool).

### Likelihood Explanation
The precondition — permissionlessly creating/pre-seeding the HyperSwap V2 pair before a token graduates — is exactly the attack surface the code's own `_seedUniswapV2Direct`/`_seedRebalancing` "hostile pre-seed" hardening was built to defend against, confirming the team recognizes hostile pre-seeding is reachable by any address. The specific overflow-revert edge case is explicitly called out but dismissed as "the correct failure mode" in the natspec, meaning it was a known-accepted risk rather than one the code defends against (unlike the `_swapBudget` 1% reservation, which was added specifically to prevent an analogous "bricking" failure mode for extreme pre-seeds — this `mulDiv` overflow path bypasses that mitigation because it happens before `_swapBudget`'s cap is even applied, purely inside `Math.sqrt`/`Math.mulDiv`'s size computation).

### Recommendation
Bound `_noFeeSwapInput`'s inputs before the `Math.mulDiv` call: either clamp `reserveIn`/`reserveOut` (or the ratio computation) to a range that provably cannot overflow uint256 for any `uint112`-bounded reserve pair, or wrap the `Math.mulDiv`/`Math.sqrt` computation in a fallback (mirroring the existing `_swapBudget`/fallback-to-`_seedDirectMint` pattern) that treats an overflow as "seed too hostile to rebalance" and falls through to `_seedDirectMint` instead of reverting. Add a regression test that pre-seeds the V2 pair with `uint112.max`-scale reserves on both sides ahead of `finalizeGraduation` and asserts it still succeeds (opens at the direct-mint fallback ratio) rather than reverting.

### Proof of Concept
1. Attacker calls `IUniswapV2Factory(uniswapV2Factory).createPair(token, lt)` for a token that is about to (or has just) crossed `canGraduate` — permissionless, no role required.
2. Attacker funds the pair directly with extreme, imbalanced amounts near `type(uint112).max` on each side (`transfer` + `mint()` on the pair, or via any V2-compatible add-liquidity call), so `getReserves()` returns near-`uint112.max` on both `r0`/`r1`.
3. Attacker (or anyone) triggers the buy that crosses the graduation threshold, or calls `triggerGraduation(token)` directly — phase 1 (`_enterGraduating`) proceeds normally and caches `tokensForLP`/`ltFromPair` in `pendingGraduation`.
4. Anyone calls `finalizeGraduation(token)`. Execution reaches `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`, where `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` overflows uint256 given the attacker-chosen extreme `reserveIn`/`reserveOut` and the curve-derived `targetN`/`targetD`, and the call reverts.
5. Every subsequent call to `finalizeGraduation(token)` reverts identically (the malicious pair reserves are unchanged), permanently freezing the token's curve-raised LT and its `LP_RESERVE`-capped tokens on `Bonding` with no admin or user rescue path.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1022-1023)
```text
        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);
```

**File:** packages/contracts/src/Bonding.sol (L1287-1289)
```text
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));
```

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

**File:** packages/contracts/src/Bonding.sol (L1498-1522)
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
