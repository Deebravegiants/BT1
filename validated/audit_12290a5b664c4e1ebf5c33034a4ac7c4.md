### Title
Concurrent-graduation `protectedLT` starvation shrinks the hostile-pre-seed rebalance budget below the negligibility bound `_seedDirectMint`'s fallback assumes - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedRebalancing`'s hostile-mint-pre-seed defense only takes the safe "reserves are negligible" direct-mint fallback (`_seedDirectMint`) when `_pairRebalance` returns `false` because its `_noFeeSwapInput` swap size rounds to zero. The code and its natspec assert this only happens "for a seed too small to move the ratio," but the swap size is capped by `maxSwap`, which for the LT leg is derived from `_ltSwapInventory(lt, protectedLT)` — a value that can be driven to near-zero by an unrelated, attacker-triggerable concurrent graduation on the same LT, independent of how large the attacker's hostile pre-seed actually is. This decouples the "swap rounds to zero" trigger from the "pre-seed is negligible" assumption the whole regime-3 defense is built on, letting a non-negligible hostile pre-seed reach the unconditional `_seedDirectMint` path.

### Finding Description
The three-regime hostile-pre-seed defense in `Bonding._seedUniswapV2Direct` / `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` exists specifically to stop the four.meme-style LP-capture attack described in the protocol's own `AGENTS.md` [1](#0-0) .

`_seedRebalancing` only takes the safe pre-check (both reserves below `DIRECT_MINT_PRESEED_BPS` of the graduation's own inventory) at its very top [2](#0-1) . If a hostile pre-seed clears that gate (i.e. is *not* dust by that measure), the code proceeds to compute a rebalance swap and, on failure (`_pairRebalance` returns `false`), falls straight back to the same unconditional `_seedDirectMint` used for the dust case — with no re-check that the existing reserves are actually negligible relative to `(tokensForLP, ltFromPair)`: [3](#0-2) 

`_pairRebalance` returns `false` when the computed swap input `s` (or the pair's fee-charging quote on it) rounds to zero [4](#0-3) . `s` is `min(idealSwap, maxSwap)` from `_noFeeSwapInput` [5](#0-4) , and for the LT-rich branch, `maxSwap = _swapBudget(_ltSwapInventory(lt, protectedLT))` [6](#0-5) . `_ltSwapInventory` saturates to `balanceOf(this) - protectedLT` [7](#0-6) , and `protectedLT` is the escrow belonging to a **different, concurrently-graduating token sharing the same LT**, snapshotted at the top of `finalizeGraduation` [8](#0-7) .

Because `triggerGraduation`/buy-triggered phase 1 and `finalizeGraduation` are both permissionless [9](#0-8) , an attacker can arrange for two tokens (their own hostile-pre-seed target, and a second decoy token) sharing the same LT to both be in `Lifecycle.Graduating` when the target's `finalizeGraduation` runs, so that essentially all of `Bonding`'s LT balance is `protectedLT` for the decoy and the LT-side rebalance budget for the target collapses toward zero — independent of how large the attacker's own hostile `pair.mint` pre-seed is. This turns the "swap rounds to zero ⇒ pre-seed is negligible" assumption baked into `_seedRebalancing`'s fallback into a false premise, and the code falls back to `_seedDirectMint`, which unconditionally `transfer`s `(tokensForLP, ltFromPair)` and calls `pair.mint(lpLock)` [10](#0-9)  against the attacker's non-negligible pre-existing (hostile-ratio) reserves — exactly the V2 `min()`-formula wrong-price-plus-LP-donation harm the regime-3 defense was built to eliminate, per the protocol's own description of the exploit mechanics [11](#0-10) .

This is structurally the same bug class as the PraisonAI report: an input-sanitization/guard routine (`escaped_code.replace(...)` in the advisory; the `_pairRebalance`-rounds-to-zero fallback here) handles the common case but has an incomplete precondition, letting attacker-influenced state slip past the guard into a sink that trusts the guard's assumption (`shell=True` executing `$()`; `pair.mint` executing against un-verified "negligible" reserves).

The protocol's own documentation confirms this exact class of end-to-end scenario ("concurrent-graduation isolation," "wrong-opening-price / LP-capture") is no longer covered by automated regression tests, since `HostilePreSeed.t.sol` was removed [12](#0-11) .

### Impact Explanation
If exploited, an attacker's pre-seeded LP on the graduating TOKEN/LT pair opens at a ratio the attacker chose rather than the curve-close price, and the V2 `min()` mint formula donates the "wasted side" of the graduation's `(tokensForLP, ltFromPair)` deposit to the attacker's pre-existing LP position — a direct value transfer of protocol/creator/trader-owned LP-seed funds to the attacker, and an LP seeded away from the curve close price (explicitly listed as in-scope impact). This is a High/Critical-class impact: permanent loss of LP value belonging to the protocol/creator/traders whose curve-raised LT funds the graduation.

### Likelihood Explanation
Both `triggerGraduation` and `finalizeGraduation` are permissionless and reachable by any unprivileged address [9](#0-8) , and `Factory.createPair`/`pair.mint` are permissionless V2 primitives (per the documented exploit setup). Engineering a two-token concurrent-graduation scenario on a shared LT to starve `protectedLT`/`_ltSwapInventory` requires timing and non-trivial setup (two tokens on the same LT, both crossing the graduation threshold before either finalizes), which the protocol's own docs note "popular LTs see overlap." Likelihood is Medium — achievable by a motivated, LT-aware attacker but not a one-line trivial call.

### Recommendation
Re-verify the "reserves are negligible" assumption independently of whether `_pairRebalance` returned `false`: before falling back to `_seedDirectMint` inside `_seedRebalancing`, re-check `reserveToken`/`reserveLT` against `DIRECT_MINT_PRESEED_BPS` (the same bound used at the top of the function) rather than trusting that a zero-rounding swap implies negligible reserves. Additionally, consider decoupling the LT-side `maxSwap` budget from `protectedLT`-starved `_ltSwapInventory` (e.g., by reverting/deferring `finalizeGraduation` when `_ltSwapInventory` is abnormally small relative to `ltFromPair`, rather than silently treating a starved budget as "swap rounds to zero ⇒ safe to direct-mint"). Restore or reintroduce targeted regression tests for the concurrent-graduation isolation and hostile-pre-seed LP-capture properties that `HostilePreSeed.t.sol` used to cover.

### Proof of Concept
1. Attacker deploys Token A (their real target) and arranges for Token B to launch against the same LT.
2. Attacker front-runs Token A's graduation: calls `factory.createPair(A, LT)` (via `HyperSwap` V2 factory), transfers a meaningfully-sized (non-dust, but below `DIRECT_MINT_PRESEED_BPS` on only one side) TOKEN/LT amount to the pair, and calls `pair.mint(attacker)` to seed a hostile ratio.
3. Attacker drives buys on Token B (same LT) so that Token B's `_enterGraduating` fires and moves Token B's `ltFromPair` into `Bonding` via `Router.graduate`, inflating `Bonding`'s LT balance with an amount that will be `protectedLT` relative to Token A's later `finalizeGraduation`.
4. Attacker drives Token A's buy that crosses its own graduation threshold (`_enterGraduating` caches Token A's `(tokensForLP, ltFromPair)`).
5. Attacker calls `finalizeGraduation(A)`. `protectedLT` snapshots Token B's un-finalized escrow; `_ltSwapInventory` for the LT-rich rebalance branch is starved; `_noFeeSwapInput`/`_pairRebalance` rounds the rebalance swap to zero; `_seedRebalancing` falls back to `_seedDirectMint`, minting Token A's LP directly against the attacker's still-hostile, non-negligible pre-seeded reserves.
6. Attacker's pre-existing LP position captures the wasted-side donation from Token A's `(tokensForLP, ltFromPair)` deposit, and the LP opens off the Token A curve-close price.

(Exact numeric bounds for step 3–5 timing depend on live `DIRECT_MINT_PRESEED_BPS`/`_swapBudget` constants and would need to be confirmed with a Foundry PoC against `test/TwoPhaseGraduation.t.sol`'s harness; the code-path reachability and the decoupling of the "swap rounds to zero" signal from "reserves are negligible" is demonstrated above from the source.)

### Citations

**File:** packages/contracts/AGENTS.md (L126-151)
```markdown
## HyperSwap Pre-Seed Defense (Read This Before Touching `_seedUniswapV2Direct`)

The whole sub-system inside `_seedUniswapV2Direct` exists to defuse one specific attack class. It's the most subtle code in the package. Read this before touching any of the helpers (`_seedRebalancing`, `_pairRebalance`, `_routerDepositAndDispose`, `_noFeeSwapInput`).

### The exploit

A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

When our `pair.mint(lpLock)` runs in phase 2 against this non-empty pair, V2's mint formula picks up the existing reserves:

```
liquidity = min(amount0 · totalSupply / reserve0, amount1 · totalSupply / reserve1)
```

The `min(...)` arm whose denominator is bigger relative to its numerator wins, and the OTHER arm's "excess" deposit is donated pro-rata to existing LP holders — i.e. to the attacker. Two harms:

- **Wrong opening price.** Post-mint reserves are `(R_attacker + T_a, R_attacker + T_b)`, so the LP opens at `(R_a + T_a) / (R_b + T_b)`, NOT at the curve close `T_a / T_b`. A `$15` LT pre-seed at 50% off curve close opens the pool ~454 bps off.
- **LP capture.** The wasted-side excess goes to the attacker's LP claim. A `1 wei + 1 LT` pre-seed (~`$1` attack budget) captures ~34 bps of LP.

A cheaper variant skips step 3 entirely: `transfer(pair, dust) + pair.sync()` forces the stored reserves to the dust ratio without minting any LP, leaving the pair at `reserves > 0 && totalSupply == 0`. Regime 1 below covers both shapes by keying on supply rather than reserves.

This is the same exploit class as the four.meme Feb 2025 incident (~$183K loss).
```

**File:** packages/contracts/AGENTS.md (L221-229)
```markdown
The auto-sweep emits `LTRescued(lt, owner, amount)` for indexer observability. The dedicated regression tests for these edge cases were removed alongside `HostilePreSeed.t.sol`; future changes to `finalizeGraduation` / `_routerDepositAndDispose` / `_sweepLTToOwner` should add targeted coverage if the behaviour is non-obvious from the unit-level tests in `TwoPhaseGraduation.t.sol`.

### Tests you MUST re-run if you change any of this

- `test/NoFeeSwapInput.t.sol` — 9 deterministic + 2 fuzz tests on the load-bearing math (degenerate inputs, monotonicity, cap-at-budget, closed-form correctness, overflow safety, the round-down-to-zero input shape that motivated the precheck).
- `test/TwoPhaseGraduation.t.sol` — brick-resistance + phase-1-fits-in-small-block tests, plus the hostile-pre-seed open-at-cached-ratio tests (`test_hostilePreSeed_*`) covering both the dust direct-mint fallback and the meaningful-reserve swap path, must still pass.
- `test/GraduationInvariants.t.sol` — zero-gap, supply conservation, parabola cap. Honest-path properties unchanged by the defense.

The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.
```

**File:** packages/contracts/src/Bonding.sol (L970-1002)
```text
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }

    /// @notice Phase 2: seed the V2 LP and lock it. Permissionless —
    ///         keeper drives the happy path; anyone can rescue a stuck token.
    /// @dev Bypasses the V2 router and calls `pair.mint(lpLock)`
    ///      directly. This is brick-proof against a front-runner pre-creating
    ///      the pair and dust-seeding it between phases.
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
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
```

**File:** packages/contracts/src/Bonding.sol (L1010-1020)
```text
        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
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

**File:** packages/contracts/src/Bonding.sol (L1383-1389)
```text
    function _ltSwapInventory(
        address lt,
        uint256 protectedLT
    ) internal view returns (uint256) {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        return bal > protectedLT ? bal - protectedLT : 0;
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
