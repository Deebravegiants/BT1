### Title
Attacker-crafted HyperSwap V2 pre-seed reserves overflow `Math.mulDiv` in `_noFeeSwapInput`, permanently bricking `finalizeGraduation` - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2024-55195 is an "allocation-size-too-big" DoS: an attacker-influenced size parameter drives an internal computation past its representable bound, causing an unconditional failure. The analog on `alt.fun` is in `Bonding._noFeeSwapInput` (`packages/contracts/src/Bonding.sol:1507-1522`), used by the mint-pre-seed rebalance branch of graduation. An unprivileged attacker who pre-seeds the HyperSwap V2 `TOKEN`/`LT` pair with `pair.mint` before graduation can size the pool's reserves so that `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` (`packages/contracts/src/Bonding.sol:1517`) produces a quotient that exceeds `uint256`, causing `Math.mulDiv` to revert. Because this call sits on the only rebalance path `finalizeGraduation` can take once a pre-seed exceeds the tiny `DIRECT_MINT_PRESEED_BPS` safety band, the revert is unconditional and permanent for that token — `finalizeGraduation` can never succeed, freezing the curve-raised LT and the LP-reserved tokens parked in `Bonding` forever.

### Finding Description
`finalizeGraduation` (`packages/contracts/src/Bonding.sol:1000-1034`) calls `_seedUniswapV2Direct` → `_seedRebalancing` (`packages/contracts/src/Bonding.sol:1201-1354`) whenever the HyperSwap V2 `TOKEN`/`LT` pair already has `totalSupply() > 0` — i.e., whenever *anyone* has already called `pair.mint` on that pair. Nothing gates who can create/mint that pair first: `_ensureUniswapV2Pair` (`packages/contracts/src/Bonding.sol:1121-1130`) will happily use a pre-existing pair, and V2 `mint` is permissionless once the pair exists.

`_seedRebalancing` only takes the "safe" direct-mint fallback (`_seedDirectMint`) when **both** pre-seeded reserves are below `DIRECT_MINT_PRESEED_BPS` (1 bps) of the cached graduation targets (`packages/contracts/src/Bonding.sol:1297-1302`). Any pre-seed above that band on either side falls into `_pairRebalance` → `_noFeeSwapInput`:

```
uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
uint256 newIn = Math.sqrt(product);
``` [1](#0-0) 

The function's own natspec concedes the risk: *"the final result `... / targetD` must still fit in uint256... Constructed adversarial inputs that violate this would revert rather than silently truncate."* [2](#0-1) 

`reserveIn`/`reserveOut` come straight from the attacker-controlled V2 pair's `uint112` reserves (`packages/contracts/src/Bonding.sol:1287-1289`), so `reserveIn * reserveOut` can be driven up to ~2^224. `targetN`/`targetD` are `tokensForLP`/`ltFromPair` (or vice versa), which are fixed by the curve's own state at graduation and can legitimately be very small — e.g. a token that graduates via the supply-sellout trigger (`IPair.tokenBalance() == 0`, `packages/contracts/src/Bonding.sol:689`) with a thin `ltFromPair` denominator. By sizing a self-funded `pair.mint` pre-seed to sit just above the `DIRECT_MINT_PRESEED_BPS` band (so the safe fallback is skipped) while keeping the reserve product large relative to `targetD`, the attacker forces `Math.mulDiv`'s internal fit-check to fail and revert. There is no `try/catch` around this call anywhere in `_seedRebalancing`/`_seedUniswapV2Direct`/`finalizeGraduation`, so the revert propagates all the way up and `finalizeGraduation` can never complete for that token.

This is fully reachable by a single unrelated, unprivileged wallet:
1. Buy/acquire some `TOKEN` and `LT` (any amount, via `Zap.buy`/BounceTech `mint`).
2. Call HyperSwap V2 factory `createPair(TOKEN, LT)` and `pair.mint(attacker)` with self-supplied `TOKEN`/`LT` sized to breach the `DIRECT_MINT_PRESEED_BPS` band on at least one side, before the token graduates.
3. Wait for/trigger graduation phase 1 (`triggerGraduation` or the threshold-crossing buy), then call the permissionless `finalizeGraduation(tokenAddress)`.
4. `finalizeGraduation` reverts unconditionally inside `_noFeeSwapInput`'s `Math.mulDiv`, forever.

### Impact Explanation
Once `finalizeGraduation` reverts unconditionally, the token is permanently stuck in `Lifecycle.Graduating`: `Bonding` continues to hold the entire curve-raised LT (moved there via `Router.graduate` inside `_prepareGraduationLiquidity`, `packages/contracts/src/Bonding.sol:1084-1087`) and the LP-reserved token allocation (`tokensForLP`, capped at `LP_RESERVE` = 250M tokens, `packages/contracts/src/Bonding.sol:1090`). No LP is ever seeded, no `LPLock.recordLock` ever fires, and trading cannot resume (the token is neither `Curve` nor `Graduated`). This is a permanent freeze of real trader/creator funds (the LT raised by every buyer on the curve) and of the protocol's LP allocation, satisfying the "permanent freezing of trader, creator or LP funds" bar. Severity is High given the attack requires no privilege and permanently disables an entire token's economic finality.

### Likelihood Explanation
The attack requires only ordinary permissionless actions (acquire tokens/LT, create/mint a V2 pair, wait for graduation, call `finalizeGraduation`) — no admin role, no upgrade, no off-chain dependency. The only constraint is sizing the pre-seed to cross the `DIRECT_MINT_PRESEED_BPS` (1 bps) safety threshold while the token's own `tokensForLP`/`ltFromPair` ratio is skewed enough for the `Math.mulDiv` fit-check to fail; this is attacker-choosable ahead of time by picking which token to target and how large a pre-seed to fund, making the likelihood substantial for any attacker willing to front the seed capital (which is not necessarily large, since a thin `ltFromPair` denominator amplifies the effective ratio).

### Recommendation
Bound `_noFeeSwapInput`'s inputs defensively instead of relying on an unhandled revert as the failure mode: cap `reserveIn`, `reserveOut` against the graduation targets before computing `Math.mulDiv`, or wrap the rebalance computation so any overflow/failure falls back to `_seedDirectMint` (the same fallback already used when the fee-charging quote rounds to zero). This preserves the "brick resistance" guarantee the code's own natspec claims to provide but currently does not enforce for the extreme-ratio case.

### Proof of Concept
Conceptual PoC (illustrative, not exact numbers):
1. Launch a token via `Zap.createToken`, buy just enough to reach the supply-sellout graduation trigger (`IPair.tokenBalance() == 0`) with a minimal `ltFromPair` (small `targetD`).
2. Front-run/anticipate graduation: before `finalizeGraduation` is called, create the HyperSwap V2 `TOKEN`/`LT` pair and self-fund `pair.mint` with reserves whose product `reserveIn * reserveOut`, multiplied by `targetN` and divided by the small `targetD`, exceeds `type(uint256).max`.
3. Call `Bonding.triggerGraduation(token)` (if not already triggered) then `Bonding.finalizeGraduation(token)`.
4. Observe `finalizeGraduation` revert inside `Math.mulDiv` (`_noFeeSwapInput`) on every subsequent call — the token can never graduate, and the curve-raised LT plus `tokensForLP` remain permanently locked in `Bonding`.

### Citations

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
