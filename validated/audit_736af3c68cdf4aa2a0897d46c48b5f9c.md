Based on the evidence gathered, I found a plausible mapping of the report's bug class ("an unhandled exception permanently corrupts state / bricks execution") onto alt.fun's graduation finalization path, but I was not able to fully trace the exact arithmetic that would drive the minted liquidity to zero within the remaining tool budget. I present what I confirmed and flag the remaining uncertainty explicitly.

### Title
Unhandled `LPLock.recordLock` revert on zero LP liquidity permanently bricks `finalizeGraduation` - (File: `packages/contracts/src/LPLock.sol`, `packages/contracts/src/Bonding.sol`)

### Summary
The external report describes a client raising an unhandled exception mid-execution, corrupting consensus state irrecoverably. The closest reachable analog in alt.fun is `Bonding.finalizeGraduation` unconditionally calling `LPLock.recordLock` with the LP `liquidity` amount computed by `_seedUniswapV2Direct`, with no zero-guard and no retry/rescue path if that call reverts.

### Finding Description
`LPLock.recordLock` explicitly reverts when `amount == 0`: [1](#0-0) 

`Bonding.finalizeGraduation` computes `liquidity` from `_seedUniswapV2Direct` (which itself dispatches to the empty-pair mint, the donation/skim path, or the hostile-mint rebalance + `router.addLiquidity` path) and passes it straight into `LPLock.recordLock` with no fallback: [2](#0-1) 

`LPLockStorage.isLocker` is documented as add-only with no removal/rescue mechanism, and the codebase's own `AGENTS.md` explicitly states that Phase 2 (`finalizeGraduation`) "must never revert under any pre-seed shape" because a revert here locks the token in `Lifecycle.Graduating` with no on-chain recovery: [3](#0-2) [4](#0-3) 

The developers already engineered "brick resistance" specifically to prevent `pair.swap`/`pair.mint`/`router.addLiquidity` reverts across the three pre-seed regimes (empty, donation, hostile-mint), and they test dust-seed edge cases where the rebalance swap output rounds to zero (`test_brick_resistance_frontRun_dust_seed`), falling back to a direct mint. However, I could not confirm within this investigation whether every combination of `tokensForLP`/`ltFromPair` cached at phase 1 and an adversary's hostile pre-seed reserves can still drive the *final* `liquidity` value returned by `_routerDepositAndDispose`'s `addLiquidity` call (or the direct-mint fallback) down to exactly zero via rounding, in a shape the existing regression tests don't cover. If such a shape exists, `recordLock`'s `ZeroAmount` revert would propagate out of `finalizeGraduation` with no way to retry differently, since `pendingGraduation[token]` values are frozen and deterministic — every future call would revert identically.

### Impact Explanation
If reachable, this permanently freezes the entire curve-raised LT balance and the 250M reserved tokens parked in `Bonding` for that token (`p.ltFromPair`, `p.tokensForLP`, `p.lpBurned`), because the token is stuck in `Lifecycle.Graduating` forever — trading is frozen (`isTrading` false), graduation can't be re-triggered (`NotGraduating`/`TokenIsGraduating` guards elsewhere), and there is no owner-level rescue function for `Bonding`'s held LT/tokens in this state. This matches the "permanent freezing of trader, creator, or LP funds" criterion.

### Likelihood Explanation
Low-to-medium confidence without a confirmed concrete trigger. The attack surface (permissionless pre-seeding of the HyperSwap pair between phase 1 and phase 2, as documented extensively in `AGENTS.md`'s "HyperSwap Pre-Seed Defense" section) is real and attacker-reachable by any unprivileged address via `factory.createPair` + `transfer` + `mint`/`sync`. Whether it can be tuned to produce `liquidity == 0` specifically at the `addLiquidity`/direct-mint step (as opposed to being caught by the existing dust fallback) is unverified.

### Recommendation
Add an explicit zero-liquidity guard/fallback in `Bonding._seedUniswapV2Direct` (or immediately before calling `recordLock`) that either (a) proves by construction `liquidity > 0` for every reachable pre-seed shape and extends `test/TwoPhaseGraduation.t.sol` with a targeted regression at the boundary between the "swap rounds to zero" dust fallback and the "swap fires" rebalance path, or (b) adds a bounded on-chain rescue/retry path for a token stuck in `Lifecycle.Graduating` so an unexpected revert in the LP-seeding leg cannot cause unrecoverable freezing.

### Proof of Concept
Not established — I could not confirm a concrete input combination that drives `liquidity` to exactly `0` at the `LPLock.recordLock` call site within the scope of this investigation. A background engineer should fuzz `_noFeeSwapInput` / `_pairRebalance` / `_routerDepositAndDispose` output at pre-seed ratios just above the existing dust-fallback threshold to determine if `liquidity == 0` is reachable; if not reachable, this finding should be downgraded/rejected.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
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
    }
```

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
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
