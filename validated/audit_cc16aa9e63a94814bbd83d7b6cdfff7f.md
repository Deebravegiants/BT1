### Title
Graduation LP-seeding fallback calls raw `pair.mint()` against a non-empty, attacker-controlled pool, donating curve-raised funds to a pre-seeded LP position - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedRebalancing` is supposed to guarantee that a raw, un-rebalanced `pair.mint()` (`_seedDirectMint`) is only ever used when the HyperSwap V2 pair is empty or holds economically negligible ("dust", ≤1 bps of target) reserves. In practice, the fallback that reuses `_seedDirectMint` is gated on whether `_pairRebalance`'s corrective swap sizes to zero — a *precision* condition, not the *dust* condition the surrounding natspec claims. An attacker can pre-seed the pair with reserves that are far above the 1 bps dust threshold but whose ratio deviates from the curve-close target by an amount small enough that `_noFeeSwapInput`'s integer `sqrt`/`mulDiv` floors the required swap to `0`. `_pairRebalance` then returns `false`, and `_seedRebalancing` falls back to `_seedDirectMint`, which calls the pair's real Uniswap-V2 `mint()` while `totalSupply() != 0` — invoking the standard `min(amount0·S/r0, amount1·S/r1)` formula against the attacker's pre-existing, large LP position, donating the off-ratio side of the curve's `tokensForLP`/`ltFromPair` deposit to that attacker-owned LP share.

### Finding Description
This is the same bug *class* as CVE-2024-39330 (Django `GHSA-9jmf-237g-qf46`): a security-critical validation ("only mint against an effectively empty pool") is enforced in the primary/intended call sites, but a secondary code path re-uses the same unguarded primitive function without re-verifying that the invariant the primitive relies on still holds — exactly like Django's `Storage.generate_filename()` override skipping the parent's path-safety check.

Concretely, in `packages/contracts/src/Bonding.sol`:

- `_seedUniswapV2Direct` (lines 1201-1234) branches on `IUniswapV2Pair(pair).totalSupply() == 0` to pick the safe empty-pair `_seedDirectMint` path (Regime 1) vs. the hostile-preseed `_seedRebalancing` path (Regime 3).
- `_seedRebalancing` (lines 1279-1354) first checks a **dust** band (`DIRECT_MINT_PRESEED_BPS = 1` bps, lines 1291-1302) to decide whether it's safe to call `_seedDirectMint` even though `totalSupply() != 0`. The natspec on `_seedDirectMint` (lines 1236-1244) explicitly justifies this only "against dust reserves… negligible".
- However, the *actual* second call to `_seedDirectMint` inside `_seedRebalancing` (lines 1301/1331/1347) is not gated by that dust check — it's gated by `_pairRebalance` returning `false`, i.e. by `_noFeeSwapInput` (lines 1507-1522) rounding the required corrective swap to `0`:
  ```
  uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
  uint256 newIn = Math.sqrt(product);
  if (newIn <= reserveIn) return 0;
  ```
  This condition is satisfied whenever the pool's current ratio is extremely close to (but not exactly equal to) the target ratio, independent of the absolute size of the reserves. An attacker fully controls both quantities — they can pre-seed the pair with reserves scaled arbitrarily large while keeping the ratio deviation from `(tokensForLP, ltFromPair)` (which are public via the `TokenGraduating` event fired at phase 1, `Bonding.sol:952`) below the integer-sqrt precision floor.
- When that fires, `_seedDirectMint` (lines 1245-1259) transfers the full `tokensForLP`/`ltFromPair` to the pair and calls `IUniswapV2Pair(pair).mint(_s().lpLock)` directly. Because `totalSupply() != 0` at this point, the real V2 pair computes `liquidity = min(amount0*S/r0, amount1*S/r1)`, and whichever side isn't the binding minimum is **donated as excess reserves to the existing LP supply** — which is entirely owned by the attacker who pre-seeded the pool.

Root cause: the safety condition documented for reusing `_seedDirectMint` under non-zero `totalSupply` ("dust-only") is not the condition actually enforced at the call site that matters; the real gate is a rounding artifact of `_noFeeSwapInput`, which can be true for arbitrarily large, attacker-chosen reserves.

### Impact Explanation
This is a **theft of curve-raised trader/creator funds at graduation and an LP seeded away from the curve-close price** — both impact categories explicitly in scope. The graduation deposit (`tokensForLP` tokens and `ltFromPair` LT, representing all curve-raised value for that launch) is partially donated to an attacker-controlled LP position instead of being deposited at the intended 1:1 curve-close ratio into `LPLock`. The attacker can withdraw/realize this value by holding (or later burning) the pre-existing LP they minted, effectively skimming protocol/creator/trader value at every graduation they choose to attack. Severity: High, matching the CVSS profile of the analog (unauthenticated, no privilege required, direct impact on protocol funds).

### Likelihood Explanation
Reachable by any unprivileged wallet:
1. Buy the launched token on the bonding curve via `Zap.buy` to obtain `TOKEN` balance, and acquire the paired LT (via `IBounceLeveragedToken.mint` or the open market).
2. Call the real HyperSwap V2 factory `createPair(token, lt)` (permissionless) before `Bonding.finalizeGraduation` does (`_ensureUniswapV2Pair`, line 1121, is itself permissionless and idempotent — it just calls `getPair`/`createPair`).
3. Transfer pre-calculated `(reserveToken, reserveLT)` amounts to the pair and call `pair.mint(attacker)` to set the pool's `totalSupply` and reserves to values that are (a) above `DIRECT_MINT_PRESEED_BPS` on both sides and (b) whose deviation from the known `(tokensForLP, ltFromPair)` target (read from the `TokenGraduating` event after phase 1 fires) makes `_noFeeSwapInput` round to zero in the relevant direction.
4. Allow/trigger `finalizeGraduation` (permissionless, phase 2) to run — it will hit the `_seedDirectMint` fallback and mint LP at the attacker's ratio, donating value to the attacker's pre-existing LP.

No special privileges, oracle manipulation, or race against the keeper's ~60s finalize window beyond ordinary front-running are required; the attacker fully controls the exact numeric edge case because all inputs (`tokensForLP`, `ltFromPair`) are public before phase 2 executes.

### Recommendation
Gate the reuse of `_seedDirectMint` inside `_seedRebalancing` on the same dust condition documented in its own natspec (i.e., only fall back to a raw `mint()` when the pre-existing reserves are within the `DIRECT_MINT_PRESEED_BPS` band), rather than on whether `_pairRebalance`'s corrective swap size rounds to zero. If `_pairRebalance` returns `false` outside the dust band, either (a) force a minimum non-zero swap large enough to move the ratio, or (b) route the remaining inventory through `_routerDepositAndDispose` (the `addLiquidity`-based, `min()`-donation-free deposit path) instead of a raw `pair.mint()` against non-zero `totalSupply`.

### Proof of Concept
Conceptual PoC (would need to be run against a HyperSwap V2 fork/mock and the deployed `Bonding`):
1. Launch a token via `Zap.createToken`, buy enough on the curve via `Zap.buy` to push it toward graduation, and call `Bonding.triggerGraduation` (or let a buy auto-trigger it) so `TokenGraduating(token, tokensForLP, ltFromPair, ...)` is emitted with known values `T = tokensForLP`, `L = ltFromPair`.
2. Off-chain, compute integer reserves `(rT, rL)` with `rT` a large multiple of `T` (well above the `DIRECT_MINT_PRESEED_BPS` dust bound) and `rL` chosen so that `rT*L != rL*T` (so a rebalance direction is picked) but `Math.sqrt(Math.mulDiv(rL*rT, T, L)) <= rL` (or the symmetric case), i.e. `_noFeeSwapInput` returns `0` for the resulting direction.
3. Call the real V2 factory `createPair(token, lt)`, transfer `rT` TOKEN and `rL` LT to the pair, call `pair.mint(attacker)` to seed `totalSupply != 0` at the crafted ratio.
4. Call `Bonding.finalizeGraduation(token)`. Observe that `_seedRebalancing` → `_pairRebalance` returns `false` → falls back to `_seedDirectMint`, which transfers the full `T`/`L` to the pair and calls `pair.mint(lpLock)`; verify via the pair's post-mint reserves/`liquidity` returned and the attacker's LP token balance that a portion of `T`/`L` was credited as excess reserves absorbed into the attacker's existing LP share rather than deposited at the curve-close ratio. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** packages/contracts/src/Bonding.sol (L1201-1234)
```text
    function _seedUniswapV2Direct(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));

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

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
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

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
```text
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

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

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
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
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1414-1429)
```text
    function _pairRebalance(
        RebalanceParams memory p
    ) internal returns (bool) {
        uint256 s = _noFeeSwapInput(p.reserveIn, p.reserveOut, p.targetN, p.targetD, p.maxSwap);
        if (s == 0) return false;

        // Quote from the pair so the output tracks its live fee; a value
        // derived from a stale fee rate would trip the pair's K-check.
        uint256 expectedOut = IUniswapV2Pair(p.pair).getAmountOut(s, p.tokenIn);
        if (expectedOut == 0) return false;

        IERC20(p.tokenIn).safeTransfer(p.pair, s);
        (uint256 amount0Out, uint256 amount1Out) = p.tokenInIs0 ? (uint256(0), expectedOut) : (expectedOut, uint256(0));
        IUniswapV2Pair(p.pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
        return true;
    }
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
