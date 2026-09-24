### Title
Permanent Freeze of `finalizeGraduation` via Zero-Liquidity Revert in `LPLock.recordLock` - (File: `packages/contracts/src/Bonding.sol`, `packages/contracts/src/LPLock.sol`)

### Summary
The Otter report describes a class of bug where a state-transition function (`fcnCheckTradeExpiry`) unconditionally calls a sub-routine (`checkBarriers`) that can revert on an attacker-influenceable arithmetic edge case, permanently freezing the vault because there is no alternate path to settlement. `alt.fun`'s two-phase graduation has the exact same shape: `Bonding.finalizeGraduation` unconditionally calls `LPLock.recordLock(token, lpPair, liquidity)` as its last step [1](#0-0) , and `recordLock` reverts with `ZeroAmount` whenever `liquidity == 0` [2](#0-1) . An attacker who can drive the deposit leg of the hostile-pre-seed defense to net `liquidity == 0` causes `finalizeGraduation` to revert every single time it is retried, because `pendingGraduation[token]` (the cached `tokensForLP`/`ltFromPair` from phase 1) is immutable and the attacker's hostile pre-seed sitting in the HyperSwap pair persists across calls — reproducing byte-identical inputs and the same zero-liquidity outcome forever.

### Finding Description
Graduation is split into two phases [3](#0-2) :
- Phase 1 (`_enterGraduating`) freezes trading (`Lifecycle.Curve → Graduating`) and caches `tokensForLP`/`ltFromPair` computed at the last curve price [4](#0-3) .
- Phase 2 (`finalizeGraduation`, permissionless) seeds the HyperSwap V2 LP using those cached amounts, locks the LP via `LPLock.recordLock`, and flips the lifecycle to `Graduated` [5](#0-4) .

For the "hostile mint pre-seed" regime, `_routerDepositAndDispose` only calls `addLiquidity` (which sets `liquidity`) when **both** `remToken > 0` and `remLT > 0`; if either side is exactly zero after the preceding rebalance swap, `liquidity` remains at its default value of `0` and the function silently returns without depositing [6](#0-5) . That `liquidity` value is threaded straight up through `_seedUniswapV2Direct` into `finalizeGraduation`'s call to `LPLock.recordLock(tokenAddress, lpPair, liquidity)` with no zero-check or fallback in `Bonding` [7](#0-6) . `LPLock.recordLock` then reverts with `ZeroAmount` for `amount == 0` [8](#0-7) .

Because the whole `finalizeGraduation` transaction reverts, none of its earlier state writes persist — the lifecycle stays `Graduating` and `pendingGraduation[token]` is unchanged. Since the cached amounts, the rebalance math (`_seedRebalancing`/`_pairRebalance`, described as "the smallest swap input that drives the pool's reserve ratio... capped at maxSwap" [9](#0-8) ), and the attacker's already-deposited hostile pre-seed are all deterministic and unchanged between calls, **every** future call to `finalizeGraduation` reproduces the identical zero-liquidity computation and reverts identically. There is no governance lever, retry path, or alternate seeding branch that bypasses `recordLock`, and `LPLock.isLocker` is explicitly documented as "add-only... there is no removal path" and a revoke "would brick every in-flight `Bonding.finalizeGraduation`" — confirming the protocol itself has no on-chain recovery mechanism for a stuck graduation [10](#0-9) .

The documentation explicitly claims "Phase 2 must never revert under any pre-seed shape" [11](#0-10)  and separately concedes that the hostile-pre-seed economic-safety end-to-end suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons, so "wrong-opening-price / LP-capture scenarios... and concurrent-graduation isolation properties are no longer enforced by automated tests" [12](#0-11)  — an explicit acknowledgment that the residual edge-case space (including an exact-zero-liquidity deposit) is not currently pinned by regression tests.

### Impact Explanation
If an attacker can craft a hostile mint pre-seed of the HyperSwap V2 pair such that the rebalance swap consumes exactly all of the `tokensForLP` or `ltFromPair` budget on one side, `finalizeGraduation` permanently reverts. The token is then stuck forever in `Lifecycle.Graduating`: `Bonding.buy`/`sell` both revert with `TokenIsGraduating` while pending [13](#0-12) , so all curve trading is frozen, the curve-raised LT (`p.ltFromPair`) and the 250M reserved tokens (`p.tokensForLP`) remain permanently locked in `Bonding` with no recovery function, and the token can never reach `Graduated` to trade on HyperSwap. This is a permanent freeze of trader/creator funds analogous to the FCN vault being permanently unsettleable.

### Likelihood Explanation
Reaching this state requires an attacker to precisely engineer a mint pre-seed of the HyperSwap V2 pair (permissionless, reachable via direct `pair.mint` calls before `finalizeGraduation` executes) such that the deterministic rebalance math zeroes out one side of the deposit. The exact feasibility depends on integer-rounding behavior inside `_seedRebalancing`/`_pairRebalance`/`_noFeeSwapInput`, which was only partially reviewed here — the docstring shows the swap size is a closed-form `sqrt` computation capped at the exact per-side budget, meaning hitting the boundary (rather than merely approaching it) plausibly requires the attacker to solve for pre-seed reserves that make the capped swap consume the budget exactly, which is a solvable but non-trivial griefing computation the attacker can perform off-chain before submitting the pre-seed transaction.

### Recommendation
- In `Bonding._routerDepositAndDispose` / `_seedUniswapV2Direct`, treat `liquidity == 0` as a valid terminal outcome of the hostile-pre-seed defense rather than propagating it into `LPLock.recordLock`. For example, skip the `recordLock` call (or record a zero-amount lock explicitly) when the computed deposit is legitimately zero, and still allow `finalizeGraduation` to flip the lifecycle to `Graduated`.
- Alternatively, relax `LPLock.recordLock`'s `ZeroAmount` guard to accept `amount == 0` as a no-op "record" (there is nothing to lock, but the token still needs to progress past `Graduating`), while keeping the `AlreadyLocked` one-shot semantics intact.
- Add a dedicated regression test that crafts a hostile pre-seed driving `_routerDepositAndDispose`'s deposit to exactly zero on one side, asserting `finalizeGraduation` still succeeds (this is the class of test explicitly noted as removed/uncovered).

### Proof of Concept
1. Launch a token and buy until `canGraduate` is true, triggering `_enterGraduating`; note the cached `(tokensForLP, ltFromPair)` in `pendingGraduation[token]` [14](#0-13) .
2. Before anyone calls `finalizeGraduation`, the attacker (permissionlessly) creates the HyperSwap V2 TOKEN/LT pair and calls `pair.mint` with a self-funded (TOKEN, LT) ratio precisely computed off-chain so that, when `_seedRebalancing`/`_pairRebalance` performs its capped rebalance swap (budget-capped at `tokensForLP` or `ltFromPair` per the natspec at [9](#0-8) ), the post-swap `remToken` or `remLT` computed in `_routerDepositAndDispose` [15](#0-14)  lands at exactly `0`.
3. Anyone calls `Bonding.finalizeGraduation(tokenAddress)`. `_routerDepositAndDispose`'s `if (remToken > 0 && remLT > 0)` gate is skipped, `liquidity` stays `0`, and `LPLock.recordLock(tokenAddress, lpPair, 0)` reverts with `ZeroAmount` [16](#0-15) .
4. Every subsequent call to `finalizeGraduation` recomputes identical values from the unchanged cached `pendingGraduation[token]` and the unchanged attacker-controlled pair state, and reverts identically — the token is permanently stuck in `Lifecycle.Graduating`, unable to trade or ever reach `Graduated`.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1449-1486)
```text
    function _routerDepositAndDispose(
        address tokenAddress,
        address lt,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        BondingStorage storage $ = _s();
        address routerAddr = $.uniswapV2Router;
        address lpLock_ = $.lpLock;
        uint256 remToken = IERC20(tokenAddress).balanceOf(address(this));
        // Subtract `protectedLT` (LT that doesn't belong to this graduation
        // — concurrent escrows or stray dust, snapshotted at the top of
        // `finalizeGraduation`) so the deposit allowance can never pull
        // another graduation's earmark or accidentally absorb dust into a
        // locked LP.
        uint256 ltBal = IERC20(lt).balanceOf(address(this));
        uint256 remLT = ltBal > protectedLT ? ltBal - protectedLT : 0;

        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
            IERC20(tokenAddress).forceApprove(routerAddr, 0);
            IERC20(lt).forceApprove(routerAddr, 0);
        }

        // Burn off-ratio TOKEN remainder (`Bonding` is the Token owner).
        // Hostile pre-seeds reduce circulating supply by the attacker's
        // wasted-side share, net positive for honest holders.
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
        // LT remainder is third-party — we cannot burn it. It stays in
        // this contract until `finalizeGraduation`'s post-bookend sweeps
        // it to the owner. Honest graduations never reach this code path,
        // so the residue is zero outside attack scenarios.
    }
```

**File:** packages/contracts/src/Bonding.sol (L1488-1500)
```text
    /// @dev Smallest swap input that drives the pool's reserve ratio
    ///      `(reserveIn + s) / (reserveOut - out)` to `targetN/targetD`
    ///      under the no-fee constant-product model:
    ///        `(reserveIn + s)² = reserveIn * reserveOut * targetN/targetD`
    ///      ⇒ `s = sqrt(reserveIn * reserveOut * targetN/targetD) - reserveIn`,
    ///      capped at `maxSwap`. The actual swap is fee-charging (the pair's
    ///      live fee), so the post-swap ratio drifts from the target by the
    ///      fee; the balanced-subset deposit absorbs the residual without
    ///      donating.
    ///
    ///      `Math.mulDiv` keeps the intermediate product
    ///      `reserveIn * reserveOut * targetN` inside its 512-bit working
    ///      space, but the final result `... / targetD` must still fit in
```

**File:** packages/contracts/src/LPLock.sol (L29-36)
```text
        /// @dev Locker allowlist for `recordLock`. Add-only via `addLocker` —
        ///      there is no removal path. A live revoke would brick every
        ///      in-flight `Bonding.finalizeGraduation` (token permanently
        ///      stuck in `Lifecycle.Graduating`, no on-chain recovery), so
        ///      the only way to retire a locker is a UUPS upgrade — which
        ///      surfaces on-chain ahead of time instead of as a one-tx kill
        ///      switch.
        mapping(address account => bool) isLocker;
```

**File:** packages/contracts/src/LPLock.sol (L70-84)
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
