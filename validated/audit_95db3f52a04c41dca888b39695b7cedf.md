### Title
Permissionless HyperSwap pair pre-seeding can round `finalizeGraduation`'s LP deposit to zero, causing `LPLock.recordLock` to revert and permanently bricking the token in `Lifecycle.Graduating` - (File: packages/contracts/src/Bonding.sol, packages/contracts/src/LPLock.sol)

### Summary
`Bonding.finalizeGraduation` computes `liquidity` from seeding a HyperSwap V2 pair and then calls `LPLock.recordLock(tokenAddress, lpPair, liquidity)`, which is a **one-shot, non-skippable** step: `recordLock` unconditionally `revert`s with `ZeroAmount()` if `liquidity == 0` (or `InsufficientLPBalance` if the LP token wasn't actually minted to `LPLock`) [1](#0-0) . Because phase 1 (`_enterGraduating`) has already permanently drained the curve's LT, frozen trading, and cached `pendingGraduation[token]`, and because `Lifecycle.Graduating` has no path back to `Curve`, a `finalizeGraduation` that reverts on this last line leaves the token's curve-raised LT and the 250M `LP_RESERVE` tokens permanently parked and unreachable inside `Bonding` — the on-chain analog of the kernel's leaked, never-freed allocation: resources are allocated (drained/cached) on one path but never released or finalized because the final "registration" step (`recordLock`) can fail with no cleanup.

### Finding Description
Phase 1 of graduation is irreversible and one-directional:
- `_enterGraduating` sets `info.lifecycle = Lifecycle.Graduating`, drains the curve's raised LT via `_prepareGraduationLiquidity`, and caches `(tokensForLP, ltFromPair, lpBurned, unsoldBurned)` in `pendingGraduation[tokenAddress]` [2](#0-1) .
- There is no function that reverts `Lifecycle.Graduating` back to `Lifecycle.Curve`; every other entry point (`buy`, `sell`, `triggerGraduation`) explicitly reverts with `TokenIsGraduating`/`NotGraduating` while in this state [3](#0-2) .

Phase 2, `finalizeGraduation`, is permissionless and is documented as needing to "never revert under any pre-seed shape" [4](#0-3) . Its last two steps are:
```
uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);
_sweepLTToOwner(lt, protectedLT);
info.lifecycle = Lifecycle.Graduated;
...
LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);
``` [5](#0-4) 

`recordLock` has no tolerance for `amount == 0` or an under-funded LP balance — both trigger a hard revert, and because it's called at the very end of `finalizeGraduation`, that revert unwinds the whole transaction, so `finalizeGraduation` can never succeed for that token thereafter (the lifecycle write and state deletion that would have followed never commit) [1](#0-0) .

The protocol's own natspec acknowledges this exact failure mode is possible in principle and had to be specifically defended against: `_swapBudget` caps the rebalance swap at 99% of available inventory "so the subsequent `addLiquidity` always has a non-zero amount of BOTH sides to deposit," explicitly because "an extreme hostile pre-seed … drives the unconstrained `_noFeeSwapInput` past our per-side budget … the swap consumes 100% of one side. `_routerDepositAndDispose` then skips `addLiquidity` (`remToken == 0` or `remLT == 0`), `finalizeGraduation` returns `liquidity = 0`, and `LPLock.recordLock(...)` records a zero-sized lock" [6](#0-5) . This comment mis-describes the actual consequence — a "zero-sized lock" cannot actually be *recorded*, because `recordLock` reverts on `amount == 0` — meaning the defense's real failure mode is not a bad LP allocation but an outright brick of `finalizeGraduation`.

The `_swapBudget` 1%-reservation mitigates the specific "one side fully consumed by the rebalance swap" scenario the comment describes, but the broader class of griefing — a pre-existing, attacker-controlled HyperSwap pair with `totalSupply() > 0` where the protocol's own deposit amounts round to `0` LP minted by V2's `liquidity = min(amount0*ts/reserve0, amount1*ts/reserve1)` formula — is a distinct rounding hazard tied to the *ratio and absolute size* of the attacker's pre-existing reserves versus the protocol's `(tokensForLP, ltFromPair)` deposit, not to the rebalance-swap budget. The fuzz coverage in `TwoPhaseGraduation.t.sol` (`testFuzz_hostilePreSeed_neverProfitable_neverBricks`) only sweeps `seedMultiple` up to `1000×` one side, holding the other side fixed at the curve-close target — it does not exercise the case where the attacker inflates *both* pre-existing reserves and the pair's `totalSupply` by many orders of magnitude simultaneously (i.e., a large, roughly-balanced pre-existing pool at a slightly-off ratio), which is the shape that stresses Uniswap V2's `mint()` rounding-to-zero on the deposit side rather than the swap side. Given the documented brick-resistance requirement is explicitly "must never revert under any pre-seed shape," and the code's own comments show the authors were aware zero-liquidity outcomes are reachable from hostile pre-seeding but only patched one specific path to it, this residual gap is a credible, unpatched analog of the CVE's "allocate-then-fail-to-finalize-cleanly" bug class.

### Impact Explanation
If `finalizeGraduation` reverts on `LPLock.recordLock`, the token is stuck in `Lifecycle.Graduating` forever: trading is frozen (`buy`/`sell` revert with `TokenIsGraduating`), the curve's entire raised LT (`ltFromPair`) and the earmarked `tokensForLP`/`LP_RESERVE` tokens remain locked inside `Bonding` with no withdrawal path, and the token's traders/creator permanently lose access to their curve-raised value and cannot exit or claim LP. This is a permanent freezing of trader and creator funds triggered by an unprivileged, permissionless attacker pre-seeding the HyperSwap pair — one of the explicitly in-scope reachable primitives.

### Likelihood Explanation
`finalizeGraduation` is permissionless and pre-creating/pre-seeding the HyperSwap V2 pair is explicitly called out in this scan's scope as an attacker-reachable action. Any address can watch the mempool for `TokenGraduating` events (phase 1), then front-run the keeper's `finalizeGraduation` call by pre-creating the pair and minting LP at a scale/ratio engineered to make the protocol's subsequent deposit round to zero LP. The `_swapBudget` fix demonstrates the team already anticipated a `liquidity == 0` outcome from hostile pre-seeding; the remaining rounding-to-zero surface through V2's `mint()` formula on the deposit path is plausible but unverified by any test in the current suite (`HostilePreSeed.t.sol` covering these end-to-end scenarios was removed for runtime reasons, per the repo's own notes) [7](#0-6) .

### Recommendation
Add an explicit non-zero-liquidity floor check inside `finalizeGraduation` (or `_seedUniswapV2Direct`) before calling `LPLock.recordLock`, with a fallback seeding strategy (e.g., forcing `_seedDirectMint` or retrying with a rescaled deposit) whenever the computed `liquidity` would be zero or below `LPLock`'s minimum, so that phase 2 can always complete and record a non-zero lock rather than reverting irrecoverably. Extend `TwoPhaseGraduation.t.sol`'s fuzz coverage to stress-test pre-existing pools with large, simultaneously-inflated `totalSupply()` and reserves (not just one-sided reserve multiples) to confirm `liquidity > 0` holds under all V2 `mint()` rounding conditions.

### Proof of Concept
Conceptual reproduction (cannot be executed here without repository access, but derivable from the cited code):
1. Attacker (unprivileged) watches for `TokenGraduating(tokenAddress, tokensForLP, ltFromPair, ...)`.
2. Before the keeper's `finalizeGraduation` lands, attacker calls the HyperSwap factory to create the TOKEN/LT pair, then deposits a large, precisely-ratioed pair of reserves and calls `pair.mint(attacker)` to establish a big `totalSupply()` at a ratio just off the cached `tokensForLP/ltFromPair`.
3. When `finalizeGraduation` executes `_seedUniswapV2Direct` → `_routerDepositAndDispose`, the router's `addLiquidity` computes `liquidity = min(amountToken*totalSupply/reserveToken, amountLT*totalSupply/reserveLT)` against the attacker's now-large `reserveToken`/`reserveLT`/`totalSupply`; if the protocol's post-rebalance deposit amounts are small relative to the attacker's inflated reserves, `liquidity` rounds to `0`.
4. `finalizeGraduation` returns `liquidity = 0` and calls `LPLock.recordLock(tokenAddress, lpPair, 0)`, which reverts with `ZeroAmount()` [8](#0-7) , unwinding the entire `finalizeGraduation` transaction.
5. The token is permanently stuck in `Lifecycle.Graduating`; every future call to `finalizeGraduation` for this token repeats step 4 with the same attacker-held pool state, so the token can never graduate, and its curve-raised LT and 250M reserved tokens remain frozen in `Bonding` indefinitely.

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

**File:** packages/contracts/src/Bonding.sol (L1356-1378)
```text
    /// @dev Cap the rebalance swap at 99% of the available side's budget,
    ///      so the subsequent `addLiquidity` always has a non-zero amount
    ///      of BOTH sides to deposit. Without this, an extreme hostile
    ///      pre-seed (massively imbalanced reserves) drives the
    ///      unconstrained `_noFeeSwapInput` past our per-side budget,
    ///      `_pairRebalance` clamps to the full budget, and the swap
    ///      consumes 100% of one side. `_routerDepositAndDispose` then
    ///      skips `addLiquidity` (`remToken == 0` or `remLT == 0`),
    ///      `finalizeGraduation` returns `liquidity = 0`, and
    ///      `LPLock.recordLock(...)` records a zero-sized lock — the
    ///      attacker's pre-existing LP becomes 100% of the pool. Reserving
    ///      1% guarantees the deposit leg always lands AND mints non-zero
    ///      LP at the post-swap ratio. The 1% comes off the swap, not the
    ///      deposit — for any realistic pre-seed `s_unconstrained` is
    ///      orders of magnitude below `maxSwap`, so the cap doesn't bind
    ///      and behaviour is unchanged. It only kicks in for catastrophic
    ///      pre-seeds beyond our budget capacity, where the alternative
    ///      is bricking.
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
    }
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L192-207)
```text
    function test_phase2_double_finalize_reverts() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);
        bonding.finalizeGraduation(tokenAddr);

        // Second call: token is now `Graduated`, not `Graduating`.
        vm.expectRevert(Bonding.NotGraduating.selector);
        bonding.finalizeGraduation(tokenAddr);
    }

    function test_phase2_finalize_on_curve_token_reverts() public {
        (address tokenAddr,) = _launchToken();
        // Token is in `Curve` — never entered `Graduating`.
        vm.expectRevert(Bonding.NotGraduating.selector);
        bonding.finalizeGraduation(tokenAddr);
    }
```

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```

**File:** packages/contracts/AGENTS.md (L229-229)
```markdown
The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.
```
