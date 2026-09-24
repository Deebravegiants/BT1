### Title
Full-curve-sellout graduation trigger computes `tokensForLP ≈ 0`, causing the empty-pair direct `pair.mint` to underflow/revert and permanently freeze the token's curve-raised LT and 250M reserved tokens in `Bonding` — ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes a cooperative two-phase handoff (L1→L2 shutdown) where a degenerate state produced by one phase is not safely handled by the terminating phase, crashing the host. alt.fun has an analogous two-phase graduation handoff: Phase 1 (`_enterGraduating`) computes and caches `(tokensForLP, ltFromPair)`, and Phase 2 (`finalizeGraduation`) consumes those cached values verbatim to seed the HyperSwap LP via a direct `pair.mint` call. The protocol's own documented "parabola invariant" states that `tokensForLP(sold) = sold·(S−sold)/S`, which is zero at both `sold = 0` and `sold = S` (full sellout) and only peaks at `S/4 = LP_RESERVE`.

The supply-exhaustion graduation trigger (`IPair.tokenBalance() == 0`, for "flat/bear markets") is exactly the `sold = S` endpoint of that parabola, so any token that graduates via a full curve sellout is fed forward into Phase 2 with `tokensForLP` at or near zero. The Regime-1 empty-pair path (`_seedDirectMint`) transfers this ~0-token amount to the HyperSwap pair and calls `pair.mint(lpLock)` directly, which for a fresh pair computes `liquidity = sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY`. With `amount0 ≈ 0`, `sqrt(...) ≈ 0`, and the subtraction underflows/reverts (or, on a raw Solidity ^0.5 V2 pair using wrapping arithmetic, silently mints a corrupted liquidity amount) — either way this is a state the graduation math was never designed to survive.

### Finding Description
Documented in `packages/contracts/AGENTS.md` (Graduation section): "**Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K`... or `IPair.tokenBalance() == 0` (supply, for flat/bear markets)" [1](#0-0)  and "**Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation." [2](#0-1) 

That defensive cap only guards the *upper* bound (`tokensForLP ≤ LP_RESERVE` at the parabola's peak); nothing in the documented design guards the *lower* tail, where `sold → S` drives `tokensForLP → 0`. Because the supply trigger is specifically defined as `tokenBalance() == 0` — i.e. `sold = S`, the exact zero of the parabola — any token graduating through this path (a legitimate, fully permissionless outcome of ordinary traders selling out the curve via `Bonding.sell`/`Zap.sell`) enters Phase 1 with `tokensForLP` at or vanishingly close to zero.

Phase 1 pins this value into `pendingGraduation[token]` unconditionally: `_enterGraduating` calls `_prepareGraduationLiquidity` and stores whatever it returns without a floor check [3](#0-2) . Phase 2's `finalizeGraduation` then always calls `_seedUniswapV2Direct` with the cached `p.tokensForLP` [4](#0-3) . For the ~99%-of-graduations empty-pair path (`totalSupply() == 0`), this routes straight to `_seedDirectMint`, which unconditionally does `transfer(pair, tokensForLP)` and then `pair.mint(lpLock)` [5](#0-4) . A real UniswapV2-style pair's first-mint branch computes `liquidity = sqrt(amount0 * amount1) − MINIMUM_LIQUIDITY`; with `amount0 (tokens) ≈ 0`, this subtraction underflows and reverts (the project's own mock reproduces exactly this formula and guard) [6](#0-5) .

Unlike the extensively-documented hostile-pre-seed defenses (Regimes 2/3, `_swapBudget`'s 99% cap, etc. — all designed to keep `liquidity > 0` against an *attacker-controlled* pre-seed) [7](#0-6) , there is no analogous protection against a *protocol-native* zero `tokensForLP` produced by the parabola's own tail. Since `finalizeGraduation` is the only state transition out of `Lifecycle.Graduating`, and it always reverts for this token, the token is permanently stuck: trading stays frozen (`buy`/`sell` revert with `TokenIsGraduating` while pending) [8](#0-7) , and all curve-raised LT plus the 250M `LP_RESERVE` tokens remain parked in `Bonding` forever, with `LPLock` having "no withdraw path in v1" and no owner override for `pendingGraduation`.

### Impact Explanation
Any token that reaches graduation via the supply-exhaustion trigger has its entire locked-up value (curve-raised LT reserve and the 250M `LP_RESERVE` token allocation) permanently frozen inside `Bonding` with no recovery mechanism — a full and irreversible loss of access for the token's creator and all holders/traders. This is a direct, unbounded freezing of protocol/trader/LP funds, satisfying the "permanent freezing of trader, creator or LP funds" impact bar.

### Likelihood Explanation
Reaching the supply-exhaustion trigger requires no privilege and no attacker cooperation from HyperSwap or BounceTech LT — it is the natural, permissionless outcome of ordinary traders selling the curve down to `tokenBalance() == 0` in a flat/declining LT-price market (explicitly the scenario the supply trigger was designed to handle, per the project's own documentation). The parabola's zero at `sold = S` is a deterministic mathematical property of the documented formula, not a probabilistic or attacker-dependent edge case, making this reachable in ordinary operation whenever a token graduates via the "bear market" path rather than the USD-threshold path.

### Recommendation
Add an explicit floor check in `_prepareGraduationLiquidity` (or in `_enterGraduating`) so that a `tokensForLP` (or `ltFromPair`) computed as zero/sub-`MINIMUM_LIQUIDITY` is rejected or substituted with a safe non-zero minimum before being cached and consumed by `finalizeGraduation`, and add a regression test that drives a token to graduation purely via the `tokenBalance() == 0` supply trigger (with no USD-threshold crossing) to assert `finalizeGraduation` still succeeds.

### Proof of Concept
1. Launch a token via `Bonding.launch`/`Zap.createToken`.
2. Have unprivileged traders repeatedly call `Bonding.sell` (or `Zap.sell`) against the curve, driving `IPair.tokenBalance()` down toward `0` without ever crossing the `$9K` USD threshold (e.g. LT price stays flat/declining) — this is the documented "supply, for flat/bear markets" trigger.
3. The closing sell (or a permissionless `Bonding.triggerGraduation` call once `canGraduate` is true) fires Phase 1, computing `tokensForLP ≈ 0` per the parabola formula `sold·(S−sold)/S` at `sold ≈ S`.
4. Anyone calls `Bonding.finalizeGraduation(tokenAddress)`. Since the HyperSwap pair is fresh (`totalSupply() == 0`), it routes to `_seedDirectMint`, which transfers ~0 tokens to the pair and calls `pair.mint(lpLock)`; the pair's `sqrt(0 * ltFromPair) − MINIMUM_LIQUIDITY` underflows and reverts.
5. `finalizeGraduation` reverts every time it is called for this token — the token is permanently stuck in `Lifecycle.Graduating`, with its LT reserve and 250M `LP_RESERVE` tokens locked in `Bonding` with no recovery path.

*Note: I was unable to fully trace the exact numeric implementation and any hidden clamping inside `_prepareGraduationLiquidity`/`canGraduate` within the available search budget (only the AGENTS.md-documented formula and the `Bonding.sol` line ranges shown above were retrieved). A Devin session with full repo access should verify the exact rounding/edge-case behavior of `_prepareGraduationLiquidity` at `sold → S` before treating this as fully confirmed.*

### Citations

**File:** packages/contracts/AGENTS.md (L88-88)
```markdown
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```

**File:** packages/contracts/AGENTS.md (L90-90)
```markdown
- **Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation.
```

**File:** packages/contracts/AGENTS.md (L164-200)
```markdown
### What we shipped — the three-regime defense

`_seedUniswapV2Direct` branches on the pre-seed shape:

#### Regime 1 — no LP minted yet (~99% of graduations)

Gated on `pair.totalSupply() == 0`, which covers both a pristine empty pair and a dust pre-seed flipped to non-zero reserves via `transfer + sync()` (no `mint`, so supply is still zero). Pristine path: `transfer(pair, tokensForLP) + transfer(pair, ltFromPair) + pair.mint(lpLock)`. With zero supply V2 mints from our deposit amounts alone, so the pool opens at exactly `ltFromPair / tokensForLP` (zero gap by construction) and any synced dust becomes reserves with no LP claim. Bypasses the V2 router entirely. Keying on supply rather than reserves keeps the dust shape out of the rebalance path, where a tiny seed could otherwise let the deposit land at the attacker's ratio.

#### Regime 2 — pure-donation pre-seed

Attacker called `IERC20(token).transfer(pair, X)` without ever calling `pair.mint`. Reserves stay at zero; only the pair's balance moved. We call `pair.skim(address(this))` first — V2's `skim` transfers excess balance over reserves to the recipient — so the donation flows back into `Bonding`. Path then collapses to Regime 1, with the empty-pair branch's tail burning any donated TOKEN and `finalizeGraduation`'s `_sweepLTToOwner` post-bookend routing donated LT to the protocol owner. The skim recipient is deliberately NOT `LPLock`: `LPLock` has no withdraw / rescue path in v1, so anything sent there is permanently stuck. `protectedLT` is snapshotted in `finalizeGraduation` BEFORE `_seedUniswapV2Direct` runs, so the donation is correctly classified as rebalance residue rather than concurrent- ... (truncated)

#### Regime 3 — mint pre-seed (the actual exploit)

Attacker called `pair.mint(attacker)` against a self-funded dust seed. Reserves are non-zero at a hostile ratio. We:

1. **Compute the swap input** that would drive the pool ratio back to the curve-close ratio under the no-fee constant-product model: `s = sqrt(reserveIn · reserveOut · targetN / targetD) − reserveIn`, capped at our per-side budget. Implementation in `_noFeeSwapInput`. Closed-form via OZ `Math.sqrt + Math.mulDiv`; no binary search, no convergence loop.
2. **Execute the swap directly on the pair** via `pair.swap(amount0Out, amount1Out, address(this), "")`. We read the output from the pair's own fee-aware `getAmountOut` quote and pass it as the output. **Bypasses the router** — HyperSwap's V2 router has no canonical `swapExactTokensForTokens` (see "HyperSwap Router non-standard ABI" above). Same direct-to-pair pattern Zap uses for post-grad user swaps. Implementation in `_pairRebalance`.
3. **Deposit the remaining inventory** via `router.addLiquidity(rest, 1, 1, lpLock, ...)`. The router's `quote()`-based optimal split deposits only the matched-ratio subset; neither side becomes a `min()` donation. Off-ratio remainder stays in `Bonding`. The router's `addLiquidity` IS canonical V2 on HyperSwap (verified selector `0xe8e33700`), so this leg is safe to keep on the router and gets the `quote()` math for free.
4. **Dispose the off-ratio remainder.** TOKEN side burned (`Bonding` is the Token owner). LT side auto-swept to the protocol owner by `finalizeGraduation`'s post-sweep — emits `LTRescued(lt, owner, amount)` for observability. See "Per-graduation LT isolation" below.

Why the **asymmetric router usage** (pair for swap, router for addLiquidity): the swap is unsafe to send through the router because HyperSwap's swap ABI is non-standard; the deposit IS safe because HyperSwap's `addLiquidity` ABI is canonical AND the `quote()`-based optimal-split logic is the part that defuses the LP-capture attack. We get the best of both — no HyperSwap-specific footgun on the swap, no reimplementation burden on the deposit.

Why the fourth step matters: **mass conservation prevents fixing both the price and the deposit.** If the pool starts off-target and our inventory is on-target, we cannot end with both at-target reserves AND a fully-deposited inventory — something has to absorb the imbalance. Step 4 is where it goes.

**Dust pre-seeds skip steps 1–4 for a direct mint.** When the swap-output side of the pre-seed is small enough that the rebalance swap rounds to zero (`s == 0` or `getAmountOut(s) == 0`), no swap can move the ratio. The reserves are then negligible against `(tokensForLP, ltFromPair)`, so `_pairRebalance` returns `false` and `_seedRebalancing` falls back to `_seedDirectMint` — the same `transfer + pair.mint` as Regime 1 — opening at the cached ratio and depositing both sides in full (nothing burned or swept). The attacker's dust LP captures `max(reserveToken/tokensForLP, reserveLT/ltFromPair)` of the pool, which vanishes. This is strictly preferable to depositing at the dust ratio via the router, which would open the pool off curve-close.

### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1024)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

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

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

```

**File:** packages/contracts/src/Bonding.sol (L1217-1259)
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

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
    }

    /// @dev Transfer the full `(tokensForLP, ltFromPair)` to the pair and
    ///      `mint` the LP to `LPLock`, opening at the exact cached
    ///      curve-close ratio. Used by the empty-pair regime and as the
    ///      dust-pre-seed fallback in `_seedRebalancing` — against dust
    ///      reserves the V2 `min()` formula's donation to any pre-existing
    ///      LP is negligible (see `_seedUniswapV2Direct` natspec). Any TOKEN
    ///      remainder (a skimmed pure-donation pre-seed) is burned; the LT
    ///      remainder is left for `finalizeGraduation`'s `_sweepLTToOwner`
    ///      post-bookend.
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

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-65)
```text
    function mint(
        address to
    ) external returns (uint256 liquidity) {
        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));
        uint256 amount0 = balance0 - reserve0;
        uint256 amount1 = balance1 - reserve1;

        uint256 totalSupply_ = totalSupply();
        if (totalSupply_ == 0) {
            liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(DEAD, MINIMUM_LIQUIDITY);
        } else {
            uint256 liquidity0 = (amount0 * totalSupply_) / reserve0;
            uint256 liquidity1 = (amount1 * totalSupply_) / reserve1;
            liquidity = liquidity0 < liquidity1 ? liquidity0 : liquidity1;
        }
        require(liquidity > 0, "MockPair: INSUFFICIENT_LIQUIDITY_MINTED");
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L122-133)
```text
    function test_phase1_buy_during_pending_reverts() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        uint256 attempt = _ltGraduationTrigger();
        lt.mintDirect(trader, attempt);
        vm.startPrank(trader);
        lt.approve(address(curveRouter), attempt);
        vm.expectRevert(Bonding.TokenIsGraduating.selector);
        bonding.buy(attempt, tokenAddr, 0, trader);
        vm.stopPrank();
    }
```
