This confirms the mechanism I need. Here is the analog.

### Title
Graduation permanently bricks when a rate-pump triggers the USD threshold with a dust `realLtRaised`, driving `tokensForLP`/`ltFromPair` below the HyperSwap V2 `MINIMUM_LIQUIDITY` floor - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.canGraduate` / `triggerGraduation` allow the USD-value graduation trigger to fire the instant `realLtRaised × exchangeRate() ≥ graduationThresholdUsd` [1](#0-0) . Because `exchangeRate()` can be arbitrarily large relative to the launch-time rate baked into the curve's virtual reserve, the `realLtRaised` needed to cross the threshold can be driven to a dust amount. `_prepareGraduationLiquidity` derives `tokensForLP` and `ltFromPair` purely from that dust `realLtRaised` and the pair's reserve ratio [2](#0-1) , so both LP-seeding amounts can be driven arbitrarily small. `finalizeGraduation`'s fast path (`_seedDirectMint`, taken on ~99% of graduations, the pristine-pair regime) unconditionally calls `pair.mint(lpLock)` with no floor check or fallback [3](#0-2) . Any real UniswapV2-family pair (HyperSwap V2 included, and faithfully mirrored by the test mock) reverts the very first `mint` on a virgin pair when `sqrt(amount0 · amount1) ≤ MINIMUM_LIQUIDITY (1000)` [4](#0-3) .

### Finding Description
`triggerGraduation` is fully permissionless and unprivileged [5](#0-4) . An attacker (or an ordinary trader) can:

1. Buy a small, deliberately-sized amount of curve tokens so `realLtRaised` sits just under the USD threshold at the current `exchangeRate()`.
2. Wait for (or simply time the call to coincide with) the LT's `exchangeRate()` rising sharply — the LT is an externally-priced, market-driven leveraged token, so large moves are an expected, non-privileged event, not a bug in the LT itself.
3. Call `Bonding.triggerGraduation(token)` (or let the next tiny buy trip the inline check in `_executeBuy`) the moment the elevated rate makes the *already-staged* dust `realLtRaised` satisfy `realLtRaised × exchangeRate() ≥ $9K`.

Because `virtualLtReserve` is fixed at launch time (`Pair.k() / TOTAL_SUPPLY()`, never re-derived from the live rate) [6](#0-5) , a large post-launch rate pump lets an arbitrarily small `realLtRaised` satisfy the USD leg. `_prepareGraduationLiquidity` then computes:

- `ltFromPair = assetReserve - virtualLtReserve` = the dust `realLtRaised`
- `tokensForLP = ltFromPair × tokenReserve / assetReserve`

Both scale down proportionally to the dust raise, and `_seedDirectMint` deposits exactly these amounts into a fresh pair via a bare `pair.mint(lpLock)` call with zero floor check [7](#0-6) . If `sqrt(tokensForLP × ltFromPair) ≤ 1000`, the underlying V2 pair's first-mint invariant reverts every single call to `finalizeGraduation` for that token, forever — `pendingGraduation[token]` is only ever cleared on a *successful* finalize [8](#0-7) , and `Lifecycle.Graduating` freezes `buy`/`sell` unconditionally with no way back to `Curve` (`triggerGraduation` itself reverts once already `Graduating`) [9](#0-8) .

The protocol's own `AGENTS.md` documents an extensive three-regime brick-resistance design against *hostile pre-seeds* of the post-graduation pair [10](#0-9) , but that hardening is entirely orthogonal to this bug class: it defends the pair's *reserve ratio* against attacker donations, not the *absolute magnitude* of `(tokensForLP, ltFromPair)` against V2's `MINIMUM_LIQUIDITY` floor on a pristine pair. `_seedDirectMint` (the pristine/empty-pair fast path, taken on ~99% of graduations) has no minimum-liquidity precheck or fallback of any kind.

### Impact Explanation
Once `finalizeGraduation` becomes permanently unmintable:
- The token is stuck forever in `Lifecycle.Graduating` — trading (buy/sell) is frozen with no recovery path.
- All curve-raised real LT (`ltFromPair`) has already been drained out of the `Pair` into `Bonding` via `Router.graduate` inside phase 1 (`_enterGraduating` → `_prepareGraduationLiquidity`) [11](#0-10) , and the unsold curve tokens plus the excess of `LP_RESERVE` have already been burned [12](#0-11)  — all before `finalizeGraduation` ever runs. That LT sits in `Bonding` with no `LPLock`/`Router` withdrawal path back to holders.
- This is a permanent freeze of trader and creator funds (curve-raised LT, unsold/LP-reserved tokens) meeting the "permanent freezing of trader, creator, or LP funds" bar, directly analogous to CVE-2019-2785's "hang" DoS impact — the operation never completes and no privileged recovery exists in v1 (`LPLock` explicitly has no rescue/withdraw path).

### Likelihood Explanation
Reachable purely through `Zap.buy`/`Bonding.buy` and the permissionless `Bonding.triggerGraduation` — no privileged role, upgrade, or off-chain action required. Leveraged tokens (LT) are, by protocol design, high-volatility rebasing-priced instruments (3-5x leverage per the docs), so large rate swings large enough to shrink the graduating-buy size to dust-level LT amounts are a realistic, foreseeable market condition rather than a contrived edge case. An attacker only needs to control the *timing* of a small buy/trigger call relative to a naturally (or LT-mechanism-)large rate move, which is well within reach of any unprivileged trader watching `exchangeRate()`.

### Recommendation
Add an explicit minimum-liquidity precheck in `_seedDirectMint` (and the `_seedRebalancing` direct-mint fallback) before calling `pair.mint`: if `Math.sqrt(tokensForLP * ltFromPair) <= MINIMUM_LIQUIDITY` (mirroring the real V2 pair's constant), fall back to accumulating/escrowing the dust amounts (e.g., topping up from `LP_RESERVE` burn budget, or deferring finalize until enough value has accrued) instead of calling `pair.mint` unconditionally. Alternatively, enforce a minimum absolute `ltFromPair`/`tokensForLP` floor as a precondition inside `canGraduate`/`previewLtUntilGraduation` for the USD leg, so a graduation can never be triggered with an LP-seeding amount that a real V2 fork would reject.

### Proof of Concept
1. Launch a token normally via `Bonding.launch` at launch-time rate `R0`.
2. Buy a small amount of LT-denominated curve tokens so that `realLtRaised` (the pair's `assetReserve` minus the launch-time virtual reserve) is a tiny dust value `d` — deliberately far below the point where `sqrt(tokensForLP · ltFromPair) > 1000` would hold at rate `R0`.
3. Have the LT's `exchangeRate()` rise sharply (e.g. `lt.setExchangeRate(hugeRate)` in a test harness, modeling a real market pump) such that `d × hugeRate ≥ graduationThresholdUsd`.
4. Call `Bonding.triggerGraduation(token)` from any unprivileged address — `canGraduate` returns true and phase 1 (`_enterGraduating`) fires, caching `tokensForLP`/`ltFromPair` computed from the dust `d`.
5. Call `Bonding.finalizeGraduation(token)` — `_seedUniswapV2Direct` routes to `_seedDirectMint` (pristine pair, `totalSupply() == 0`), which calls `pair.mint(lpLock)` with the dust amounts; the V2 pair's `sqrt(amount0*amount1) > MINIMUM_LIQUIDITY` check reverts.
6. Any subsequent call to `finalizeGraduation(token)` reverts identically forever; `triggerGraduation` also permanently reverts with `TokenIsGraduating`. The token is stuck in `Lifecycle.Graduating` with its curve-raised LT and burned token reserves unrecoverable.

### Citations

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```

**File:** packages/contracts/src/Bonding.sol (L970-979)
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
```

**File:** packages/contracts/src/Bonding.sol (L1022-1030)
```text
        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

```

**File:** packages/contracts/src/Bonding.sol (L1079-1096)
```text
        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1098-1119)
```text
    /// @dev Recovers the launch-time virtual LT reserve from immutable
    ///      identities: `Pair._pool.k = tokenReserve_init * assetReserve_init
    ///      = TOTAL_SUPPLY * virtualLtReserve_init` is set ONCE in
    ///      `Pair.mint` and never modified by `Pair.swap` (swap only
    ///      mutates `tokenReserve` / `assetReserve` and asserts K-floor).
    ///      So `Pair.k() / Token.TOTAL_SUPPLY()` returns the exact
    ///      `virtualLtReserve` that was passed to `addInitialLiquidity` at
    ///      launch — for any pair, in any phase, with no storage of our own.
    ///
    ///      Going through this derivation rather than a stored mirror
    ///      eliminates an admin-writable economic-state slot and makes the
    ///      donation-immunity property a pure consequence of the pair's
    ///      already-immutable accounting. The `TOTAL_SUPPLY`-equality check
    ///      in `setTokenImplementation` keeps the divisor consistent across
    ///      impl rotations, so tokens launched under different
    ///      `tokenImplementation` versions still derive the same way.
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
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

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L29-65)
```text
    /// @dev UniswapV2's `MINIMUM_LIQUIDITY`. The first mint to a virgin pair
    ///      locks this many LP tokens permanently and requires
    ///      `sqrt(amount0 * amount1) > MINIMUM_LIQUIDITY`. Real V2 burns to
    ///      `address(0)`; OZ ERC20 v5 rejects `_mint(0)`, so we lock to a
    ///      sentinel `dead` address instead.
    uint256 internal constant MINIMUM_LIQUIDITY = 1000;
    address internal constant DEAD = address(0xdead);

    constructor() ERC20("HyperSwap LP", "HS-LP") {}

    /// @dev Direct-deposit mint matching UniswapV2 semantics: caller has
    ///      pre-transferred token0/token1 to this pair; we derive the
    ///      deposit from `balanceOf(this) - reserves`, mint LP tokens to
    ///      `to`, and update reserves. Used by `Bonding.finalizeGraduation`
    ///      (Regimes 1 & 2) and by the mock router's `addLiquidity`
    ///      delegate (Regime 3 deposit leg).
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
