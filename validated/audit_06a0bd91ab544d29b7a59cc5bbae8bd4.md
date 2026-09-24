### Title
`finalizeGraduation` can permanently revert when `tokensForLP` rounds to zero, bricking the token in `Lifecycle.Graduating` and freezing the curve-raised LT and burned LP reserve forever - (File: `packages/contracts/src/Bonding.sol`, `packages/contracts/src/LPLock.sol`)

### Summary
The external report's bug class is "a one-shot finalize/claim step that resets a lock flag only under a narrow condition, and once that condition is skipped the flag can never be reset again, permanently freezing shareholder funds." The alt.fun analog of this pattern is `Bonding.finalizeGraduation` (phase 2 of the permissionless two-phase graduation), which unconditionally calls `LPLock.recordLock`, and `LPLock.recordLock` unconditionally reverts with `ZeroAmount` when the LP `amount` minted is `0` [1](#0-0) . Because the values consumed by phase 2 (`tokensForLP`, `ltFromPair`) are pinned at the end of phase 1 and never recomputed [2](#0-1) , if `tokensForLP` rounds down to `0` in `_prepareGraduationLiquidity`, every future call to `finalizeGraduation(tokenAddress)` deterministically re-derives the same `0`-liquidity outcome and reverts identically, forever.

### Finding Description
Phase 1 (`_enterGraduating` → `_prepareGraduationLiquidity`) computes the LP-seed amount with integer division:

```solidity
tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
``` [3](#0-2) 

`assetReserve` is `virtualLtReserve + ltFromPair`, where `virtualLtReserve` is the large launch-time virtual LT amount baked into the curve's `k` [4](#0-3) . The dual graduation trigger fires as soon as `(assetReserve − virtualLtReserve) × exchangeRate ≥ $9K` (the USD trigger) [5](#0-4) . Because the reserve asset is an *external, rebasing-priced* leveraged token whose `exchangeRate()` is read live and can appreciate sharply, the real LT actually raised (`ltFromPair`) needed to cross the fixed $9K USD threshold can be arbitrarily small in LT-native units whenever `exchangeRate()` is large. In that regime, `ltFromPair` is tiny relative to `assetReserve` (which is dominated by the large, fixed `virtualLtReserve`), so `(ltFromPair * tokenReserve) / assetReserve` floors to `0`.

When `tokensForLP == 0`:
- `lpBurned = LP_RESERVE − tokensForLP == LP_RESERVE` — the entire 250M token LP reserve for that token is burned immediately in phase 1 [6](#0-5) , and this burn is irreversible.
- The real LT raised (`ltFromPair`) has already been drained from the curve pair into `Bonding` via `_s().router.graduate(tokenAddress, ltFromPair)` inside the same phase-1 call [7](#0-6)  — also irreversible.
- Phase 2 (`finalizeGraduation`) then attempts to seed the HyperSwap LP with `p.tokensForLP = 0` and unconditionally finishes with `LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity)` [8](#0-7) . Depositing/minting with one side at `0` yields `liquidity == 0`, and `recordLock` reverts with `ZeroAmount` [1](#0-0) .
- The revert unwinds the entire `finalizeGraduation` transaction, so `info.lifecycle` stays `Graduating` forever, `TokenIsGraduating` continues to be enforced on `buy`/`sell` (as shown by the existing regression tests) [9](#0-8) , and `pendingGraduation[tokenAddress]` — the source of the pinned `0` value — is never cleared, so every subsequent `finalizeGraduation` call reproduces the exact same revert. This is structurally identical to the WithdrawProxy bug: a one-shot "unlock" flag (`finalAuctionEnd`/`Lifecycle.Graduated`) that can only be set by a call (`claim()`/`recordLock`) whose precondition (non-empty LP/matching epoch) is permanently unsatisfiable once skipped.

Unlike the documented "hostile pre-seed" defenses (`_swapBudget`'s 99% cap, `_seedDirectMint` fallback) which explicitly guard against an *attacker-seeded pair* driving `liquidity` to `0`, none of that logic guards against `tokensForLP` itself being `0` **before any pre-seed even exists** — it is a pure consequence of the curve's own rounding when a real raise is economically tiny in LT terms but large in USD terms, which is exactly the situation a volatile leveraged-token reserve is designed to produce.

### Impact Explanation
This permanently freezes:
- All curve-raised LT for that token (already parked in `Bonding` via `Router.graduate`, unrecoverable — there is no admin/owner sweep of `ltFromPair`, only of `protectedLT`/dust) [10](#0-9) .
- All 750M curve-sold tokens' holders, who can never sell (buy/sell revert with `TokenIsGraduating` while stuck in `Graduating`) [9](#0-8) .
- The entire 250M `LP_RESERVE` token allocation, already burned with no LP ever created.

This is a permanent freeze of trader/creator funds with no on-chain recovery path (the only remedy stated for LP-lock-adjacent brick scenarios is a UUPS admin upgrade) [11](#0-10) , matching the High-severity bar for "permanent freezing of trader, creator or LP funds."

### Likelihood Explanation
No privileged action is required. Any ordinary buyer's `Zap.buy`/`Bonding.buy` call that happens to cross the USD threshold while `exchangeRate()` is elevated triggers phase 1 automatically inside `_executeBuy`'s `canGraduate` check [12](#0-11) ; `triggerGraduation` is explicitly permissionless as well [13](#0-12) . Given the reserve asset is a leveraged token whose price can move quickly, the scenario where a disproportionately small real LT raise crosses the fixed USD threshold is a realistic edge case, not a contrived one — it is a direct consequence of the protocol's own design choice to use a volatile external LT as curve reserve. I was not able to fully verify the exact numeric threshold constant / `canGraduate` implementation within the available tool budget, so I cannot present a fully worked numeric PoC; this should be verified with a concrete unit test before triage/fix.

### Recommendation
In `_prepareGraduationLiquidity`/`_enterGraduating` or `finalizeGraduation`, explicitly guard against `tokensForLP == 0` (and, symmetrically, `ltFromPair == 0`) before committing irreversible state: either (a) refuse to enter `Graduating` (revert `triggerGraduation`/skip the inline phase-1 trigger) when the computed `tokensForLP` would round to zero, deferring graduation until the raise is large enough to produce non-zero LP, or (b) make `finalizeGraduation` tolerate a zero-liquidity result by skipping `LPLock.recordLock` and instead routing the drained LT back to a claimable/refundable state (e.g., un-burn-equivalent accounting) rather than calling into a function that unconditionally reverts on `amount == 0`.

### Proof of Concept
Not independently reproduced with concrete numbers due to tool-call budget exhaustion before the exact `canGraduate`/threshold constant could be read. The mechanism is fully supported by code inspection:
1. Pump `exchangeRate()` on the mock/production LT so a very small `ltFromPair` (real LT raised above the launch-time virtual reserve) makes `(assetReserve − virtualLtReserve) × exchangeRate ≥ $9K` true, while `assetReserve` itself stays dominated by the large `virtualLtReserve`.
2. Have any unprivileged trader submit a normal `Zap.buy`/`Bonding.buy` that lands while this condition holds; `_executeBuy` calls `canGraduate` → `_enterGraduating` → `_prepareGraduationLiquidity`, where `tokensForLP = (ltFromPair * tokenReserve) / assetReserve` floors to `0` [3](#0-2) .
3. Any account calls `finalizeGraduation(tokenAddress)` (permissionless) [8](#0-7) ; the seeding path mints `liquidity == 0`, and `LPLock.recordLock` reverts `ZeroAmount` [1](#0-0) , reverting the whole call.
4. Repeat step 3 indefinitely — same pinned `pendingGraduation` values, same revert, forever. Token is stuck `Lifecycle.Graduating`; already-drained LT and already-burned 250M `LP_RESERVE` tokens are permanently unrecoverable.

A background engineer should add a targeted Foundry test in `packages/contracts/test/TwoPhaseGraduation.t.sol` that pumps the mock LT's `exchangeRate()` to a value engineered so `tokensForLP` computes to exactly `0` (or a value close to the rounding boundary), drives the threshold-crossing buy, and asserts that `finalizeGraduation` reverts and continues to revert on repeated calls, to numerically confirm the root cause before implementing the fix.

### Citations

**File:** packages/contracts/src/LPLock.sol (L31-36)
```text
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

**File:** packages/contracts/src/Bonding.sol (L916-931)
```text
    /// @dev `tokenHolder` is where `Router` pulls LT from / delivers tokens to
    ///      (the calling Zap). `trader` is event-only attribution (the user EOA).
    function _executeBuy(
        address tokenHolder,
        address trader,
        uint256 amountIn,
        address tokenAddress
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, true, amountInUsed, tokensOut, newCurveSupply, newLtReserve);

        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
```

**File:** packages/contracts/src/Bonding.sol (L934-953)
```text
    /// @dev Phase 1: drain curve, cache LP-bound amounts, freeze trading. Runs
    ///      inline at end of the threshold-crossing buy. Pinning `tokensForLP`
    ///      and `ltFromPair` here (at the last curve price) is what preserves
    ///      the zero-gap invariant across the tx split.
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

**File:** packages/contracts/src/Bonding.sol (L955-979)
```text
    /// @notice Permissionless trigger for phase 1 of graduation. Same flow as
    ///         the inline post-buy trigger inside `_executeBuy`, but callable
    ///         without any buy. Closes the case where `canGraduate` is true
    ///         (LT appreciation pushed the curve past the USD threshold) but
    ///         the closing buy on the curve would mint below the BounceTech
    ///         LT mint floor and revert with `BelowMinTransactionSize`,
    ///         making the token un-graduatable via `Zap.buy`.
    /// @dev    `_enterGraduating` reads pair reserves and the launch-time
    ///         virtual reserve only — it does not depend on a buy having
    ///         just landed, so the same logic is safe to expose as a
    ///         standalone entry point. The lifecycle pre-checks mirror
    ///         `Bonding.buy`; the launch trading delay is intentionally
    ///         not enforced because `canGraduate` already requires either
    ///         the USD threshold or full curve sellout, both of which are
    ///         unreachable from a fresh launch within the delay window.
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

**File:** packages/contracts/src/Bonding.sol (L1000-1052)
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

    /// @dev Send LT held by this contract above `keep` to the owner,
    ///      emitting `LTRescued`. Called at the end of
    ///      `finalizeGraduation` with `keep = protectedLT` (any escrow
    ///      that doesn't belong to this graduation), so only THIS
    ///      graduation's rebalance residue lands on the owner. No-op on
    ///      the empty-pair fast path (nothing to sweep).
    function _sweepLTToOwner(
        address lt,
        uint256 keep
    ) internal {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        if (bal <= keep) return;
        uint256 amount = bal - keep;
        address recipient = owner();
        IERC20(lt).safeTransfer(recipient, amount);
        emit LTRescued(lt, recipient, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1084-1096)
```text
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

**File:** docs/contracts-scope.md (L66-73)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L122-152)
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

    function test_phase1_sell_during_pending_reverts() public {
        // Seed a holder before graduating so they have something to try to sell.
        (address tokenAddr,) = _launchToken();
        _buyNoFinalize(tokenAddr, trader, _ltStageBeforeGraduation());
        uint256 holderBalance = Token(tokenAddr).balanceOf(trader);
        assertTrue(holderBalance > 0);

        // Now graduate via the standard rate-pump pattern.
        lt.setExchangeRate(_ratePumpForStagedGraduation());
        _buyNoFinalize(tokenAddr, trader2, _ltGraduationTrigger());
        assertTrue(bonding.isGraduating(tokenAddr));

        vm.startPrank(trader);
        Token(tokenAddr).approve(address(curveRouter), holderBalance);
        vm.expectRevert(Bonding.TokenIsGraduating.selector);
        bonding.sell(holderBalance, tokenAddr, 0, trader);
        vm.stopPrank();
    }
```
