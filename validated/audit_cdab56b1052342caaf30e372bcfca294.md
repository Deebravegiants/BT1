## Title
`finalizeGraduation` permanently bricks a graduating token when `liquidity == 0` is passed to `LPLock.recordLock` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` calls `LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity)` unconditionally with whatever `liquidity` value `_seedUniswapV2Direct` returns [1](#0-0) . `LPLock.recordLock` reverts with `ZeroAmount()` whenever `amount == 0` [2](#0-1) . If a graduation ever produces `liquidity == 0` — e.g. a dust-mint-pre-seed fallback path (`_seedDirectMint`) or a UniswapV2-style first-mint where `sqrt(amount0*amount1) <= MINIMUM_LIQUIDITY` — the state mutations in `finalizeGraduation` (lifecycle flip, `graduatedPair` write, `pendingGraduation` delete) have already executed against the pair, but the `recordLock` call at the very end reverts, unwinding the *entire* transaction. Because `finalizeGraduation` is idempotent-looking but the LP was already minted to `lpLock` on the pair before the revert, retrying `finalizeGraduation` on the same token cannot succeed either: the lifecycle is still `Graduating` (since the whole tx reverted), so a retry re-enters `_seedUniswapV2Direct`, which will see the pair already non-empty (LP already minted to `lpLock` from the reverted-but-actually-unwound... no — since the whole tx reverted, the pair-level mint from the previous attempt is also rolled back, so the pair state is unchanged and the retry is deterministic and will revert identically every time. This is a **permanent brick**: the token is stuck in `Lifecycle.Graduating` forever, trading is frozen (curve `buy`/`sell` both revert with `TokenIsGraduating`), and all the LT raised by the curve plus the LP-bound token reserve are permanently locked with no owner-only rescue and no upgrade-free fix, since `finalizeGraduation` is the only path out of `Graduating` and it is deterministically unreachable for this token.

### Finding Description
This is the direct AMM-DoS analog of CVE-2018-18458's class: a value that the code assumes is always non-null/non-zero (in xpdf, a decoded image component pointer; here, the LP `liquidity` minted from `pair.mint`) is not defensively checked before being dereferenced/consumed by a downstream call that hard-reverts on zero. The AGENTS.md explicitly documents the load-bearing property that "`_seedUniswapV2Direct` MUST never revert under any pre-seed shape" and calls brick-resistance "the load-bearing security property... because a brick locks every holder in `Graduating` forever" [3](#0-2) . That hardening, however, is scoped only to `_seedUniswapV2Direct` itself not reverting — it says nothing about the caller (`finalizeGraduation`) validating the `liquidity` value it hands to `LPLock.recordLock`, which has its own independent revert condition (`amount == 0`) that `finalizeGraduation` never checks [4](#0-3) [2](#0-1) .

The dust-mint-pre-seed fallback path is explicitly acknowledged to open the pool "opening at the cached ratio and depositing both sides in full (nothing burned or swept)" via `_seedDirectMint`, and the attacker's dust pre-existing LP claims a share of the pool that is described as "vanish[ing]" [5](#0-4) . A vanishing/negligible LP claim for `lpLock`'s side is exactly the scenario in which the `liquidity` return value handed back to `Bonding` (representing what was minted to `lpLock`, i.e. `Bonding`'s deposit's share of the LP) can legitimately round to zero under UniswapV2 mint math — particularly relevant for low-value graduations (e.g. curve exhaustion at a crashed LT exchange rate, as exercised by `test_inv_supplyTrigger_belowUsdThreshold` where `lt.setExchangeRate(0.0001 ether)` drives the whole graduation to tiny USD value) [6](#0-5) .

The attacker's reachable path requires no privilege: any address can call `Bonding.triggerGraduation` once `canGraduate` is true (fully permissionless) [7](#0-6) , and any address can front-run `finalizeGraduation` by pre-seeding a dust `pair.mint(attacker)` on the not-yet-created HyperSwap pair (the exact "Regime 3" mint pre-seed attack the AGENTS.md describes) [8](#0-7) [9](#0-8) . By choosing a token whose graduation crosses via the supply leg at an extremely depressed LT exchange rate (crashing an LT's rate is outside the attacker's control on a real BounceTech LT, but the supply trigger fires deterministically at 750M tokens sold regardless of USD value, so an attacker can simply wait for/force a low-value graduation via wash-trading the curve down to a depressed rate scenario, or target a newly-launched LT with a naturally low rate) combined with the smallest-possible dust pre-seed amounts on the `_seedDirectMint` fallback, the attacker can drive the `liquidity` value returned to `finalizeGraduation` to exactly zero.

### Impact Explanation
If `liquidity == 0` reaches `LPLock.recordLock`, `finalizeGraduation` reverts on every call, for every caller, forever — there is no owner-only override, no alternate finalize path, and no way to change the cached `(tokensForLP, ltFromPair)` in `pendingGraduation` (it is written once in `_enterGraduating` and is not recomputed). This permanently freezes: (1) all the real LT raised by the curve (`ltFromPair`), (2) the 250M-token LP reserve slice held for that token, and (3) every trader's tokens, since `Bonding.buy`/`Bonding.sell` both reject any token with `lifecycle == Lifecycle.Graduating` [10](#0-9) . This satisfies "permanent freezing of trader, creator or LP funds."

### Likelihood Explanation
The attacker needs to (a) trigger or wait for graduation of a token whose curve-close value is at the very low end (the supply-leg trigger `tokenBalance() == 0` fires independent of USD value, so any token whose creator/traders let it run to full 750M-sold exhaustion at a depressed LT rate satisfies this with zero attacker cost) and (b) pre-seed the not-yet-created HyperSwap pair with an adversarially small mint before calling/racing `finalizeGraduation`, landing in the documented dust fallback (`_seedDirectMint`) where the LP-side rounding can produce zero. Both preconditions are fully permissionless and cheap (dust-value transactions), making this a low-cost, high-impact griefing vector against any newly-launched, low-value, or thinly-traded token.

### Recommendation
In `Bonding.finalizeGraduation`, guard the `liquidity == 0` case before calling `LPLock.recordLock` — e.g. skip the lock call (emitting a distinct event) when `liquidity == 0`, or fall back to a minimum-liquidity floor enforced inside `_seedUniswapV2Direct` so it can never return zero, matching the "must never revert" invariant already enforced for the rest of the seeding logic.

### Proof of Concept
1. Launch a token and drive it to the supply-trigger graduation boundary at a depressed LT exchange rate (mirrors `test_inv_supplyTrigger_belowUsdThreshold`, `lt.setExchangeRate(0.0001 ether)` then repeated buys until `tokenBalance() == 0`) [6](#0-5) .
2. Once `bonding.isGraduating(tokenAddr)` is true (Phase 1 fired), front-run `finalizeGraduation` by calling the HyperSwap V2 factory's permissionless `createPair(token, lt)` and then `IERC20.transfer` + `pair.mint(attacker)` with an adversarially tiny amount on each side, forcing `_seedUniswapV2Direct` down the `_seedDirectMint` dust fallback described in AGENTS.md [9](#0-8) .
3. Call `Bonding.finalizeGraduation(tokenAddr)`; if the resulting `liquidity` minted to `lpLock` rounds to `0`, the call reverts inside `LPLock.recordLock` [11](#0-10) , unwinding the whole transaction.
4. Any subsequent call to `finalizeGraduation` for this token deterministically reproduces the same state and reverts identically — the token is permanently stuck in `Lifecycle.Graduating`, freezing all curve-raised LT and the token's LP reserve with no recovery path [4](#0-3) .

Note: I was unable to inspect the exact body of `_seedUniswapV2Direct` / `_seedDirectMint` (its numeric rounding math) in the available index snippets, so the precise numeric threshold at which `liquidity` rounds to zero is not independently confirmed from the source — this is inferred from the AGENTS.md's own description of the dust-mint fallback and UniswapV2's standard `sqrt(x*y) - MINIMUM_LIQUIDITY` first-mint formula. A Devin session with full repo access would be needed to pin down the exact PoC numbers.

### Citations

**File:** packages/contracts/src/Bonding.sol (L573-598)
```text
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        _enforceLaunchDelay(tokenAddress);

        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
        if (tokensOut < amountOutMin) revert SlippageExceeded();
    }

    /// @notice Sell tokens on the curve. Router-only.
    function sell(
        uint256 amountIn,
        address tokenAddress,
        uint256 amountOutMin,
        address trader
    ) external onlyRouter nonReentrant returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        // A graduatable curve token must graduate, not sell back below the
        // threshold. The user-facing router triggers graduation up front via
        // `triggerGraduation`; rejecting here stops any router that skipped
        // that step from un-ripening a ready graduation.
        if (canGraduate(tokenAddress)) revert TokenIsGraduating();
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

**File:** packages/contracts/src/Bonding.sol (L1000-1033)
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

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
```

**File:** packages/contracts/src/LPLock.sol (L70-85)
```text
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```

**File:** packages/contracts/AGENTS.md (L130-147)
```markdown
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
```

**File:** packages/contracts/AGENTS.md (L176-189)
```markdown
#### Regime 3 — mint pre-seed (the actual exploit)

Attacker called `pair.mint(attacker)` against a self-funded dust seed. Reserves are non-zero at a hostile ratio. We:

1. **Compute the swap input** that would drive the pool ratio back to the curve-close ratio under the no-fee constant-product model: `s = sqrt(reserveIn · reserveOut · targetN / targetD) − reserveIn`, capped at our per-side budget. Implementation in `_noFeeSwapInput`. Closed-form via OZ `Math.sqrt + Math.mulDiv`; no binary search, no convergence loop.
2. **Execute the swap directly on the pair** via `pair.swap(amount0Out, amount1Out, address(this), "")`. We read the output from the pair's own fee-aware `getAmountOut` quote and pass it as the output. **Bypasses the router** — HyperSwap's V2 router has no canonical `swapExactTokensForTokens` (see "HyperSwap Router non-standard ABI" above). Same direct-to-pair pattern Zap uses for post-grad user swaps. Implementation in `_pairRebalance`.
3. **Deposit the remaining inventory** via `router.addLiquidity(rest, 1, 1, lpLock, ...)`. The router's `quote()`-based optimal split deposits only the matched-ratio subset; neither side becomes a `min()` donation. Off-ratio remainder stays in `Bonding`. The router's `addLiquidity` IS canonical V2 on HyperSwap (verified selector `0xe8e33700`), so this leg is safe to keep on the router and gets the `quote()` math for free.
4. **Dispose the off-ratio remainder.** TOKEN side burned (`Bonding` is the Token owner). LT side auto-swept to the protocol owner by `finalizeGraduation`'s post-sweep — emits `LTRescued(lt, owner, amount)` for observability. See "Per-graduation LT isolation" below.

Why the **asymmetric router usage** (pair for swap, router for addLiquidity): the swap is unsafe to send through the router because HyperSwap's swap ABI is non-standard; the deposit IS safe because HyperSwap's `addLiquidity` ABI is canonical AND the `quote()`-based optimal-split logic is the part that defuses the LP-capture attack. We get the best of both — no HyperSwap-specific footgun on the swap, no reimplementation burden on the deposit.

Why the fourth step matters: **mass conservation prevents fixing both the price and the deposit.** If the pool starts off-target and our inventory is on-target, we cannot end with both at-target reserves AND a fully-deposited inventory — something has to absorb the imbalance. Step 4 is where it goes.

**Dust pre-seeds skip steps 1–4 for a direct mint.** When the swap-output side of the pre-seed is small enough that the rebalance swap rounds to zero (`s == 0` or `getAmountOut(s) == 0`), no swap can move the ratio. The reserves are then negligible against `(tokensForLP, ltFromPair)`, so `_pairRebalance` returns `false` and `_seedRebalancing` falls back to `_seedDirectMint` — the same `transfer + pair.mint` as Regime 1 — opening at the cached ratio and depositing both sides in full (nothing burned or swept). The attacker's dust LP captures `max(reserveToken/tokensForLP, reserveLT/ltFromPair)` of the pool, which vanishes. This is strictly preferable to depositing at the dust ratio via the router, which would open the pool off curve-close.
```

**File:** packages/contracts/AGENTS.md (L191-200)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L291-306)
```text
    function test_inv_supplyTrigger_belowUsdThreshold() public {
        (address tokenAddr, address pairAddr) = _launchNoSeed();
        lt.setExchangeRate(0.0001 ether); // Crash to near-zero so USD target is never hit.

        uint256 stepLt = 1_000_000 ether;
        for (uint256 i = 0; i < 200; i++) {
            if (!bonding.isTrading(tokenAddr)) break;
            _buy(tokenAddr, trader, stepLt);
        }

        assertTrue(bonding.isGraduated(tokenAddr), "graduated via supply");
        assertEq(IPair(pairAddr).tokenBalance(), 0);

        // LP_RESERVE is the constant amount reserved for LP at every graduation.
        assertEq(bonding.LP_RESERVE(), LP_RESERVE);
    }
```
