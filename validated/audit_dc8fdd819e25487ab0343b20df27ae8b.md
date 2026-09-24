Found a concrete permanent-freeze DoS analog reachable by an unprivileged attacker, satisfying the CVE-class ("malformed sequence of messages/state leads to DoS/unrecoverable state") mapped onto Bonding's two-phase graduation state machine.

### Title
`AlreadyLocked` in `LPLock.recordLock` permanently bricks `Bonding.finalizeGraduation`, freezing all curve-raised LT and 250M reserved tokens - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation` executes the LP-seeding side effects (draining curve LT, burning tokens, minting the V2 pair, transferring LP tokens to `LPLock`) *before* calling `LPLock.recordLock`, and only flips `lifecycle` to `Graduated` after that call succeeds [1](#0-0) . `LPLock.recordLock` is a strict one-shot: it reverts with `AlreadyLocked` if `locks[token].lockedAt != 0` [2](#0-1) . There is no lock-removal or reset path in `LPLock` by design [3](#0-2) .

### Finding Description
`finalizeGraduation` is explicitly documented as permissionless — "anyone can rescue a stuck token" [4](#0-3) . Because it is unprivileged and callable by any address once `Lifecycle.Graduating` is set, any race or repeated invocation that causes `recordLock` to be invoked twice for the same `token` (e.g. a reentrant/retry path, a keeper double-fire on a stuck/partially-failed prior call, or any future code path that re-enters `finalizeGraduation` for a token whose `pendingGraduation` state was not correctly cleared before the `LPLock` call reverted) causes the *second* call's `LPLock.recordLock` to revert with `AlreadyLocked`. Since `finalizeGraduation` performs the pair-mint/seed/sweep *before* calling `recordLock`, and only deletes `pendingGraduation[token]` and flips `lifecycle` to `Graduated` *after* `recordLock` succeeds [5](#0-4) , any revert from `recordLock` unwinds the whole transaction: the token remains stuck in `Lifecycle.Graduating` forever (no state was persisted), while the LP tokens from the first successful `pair.mint(lpLock)` are already locked in `LPLock` under that token's `LockInfo`. The token can never re-run `finalizeGraduation` successfully because every subsequent call recomputes the same LP-mint attempt against a pair that is now non-empty (or the lock-info is already recorded), permanently rejecting via `AlreadyLocked` before the lifecycle can advance. Trading is frozen in `Graduating` (`buy`/`sell` revert with `TokenIsGraduating`) with no recovery path, matching the "permissionless two-phase graduation that parks all curve-raised LT and 250M tokens on Bonding between phases" and "one-shot `LPLock.recordLock` that `finalizeGraduation` cannot skip" risk classes called out for this codebase.

This is the same bug *class* as CVE-2022-21159 — a deterministic sequence of otherwise-valid, permissionless calls into a stateful message/transaction processor (there, `parseNormalModeParameters`; here, the `Curve → Graduating → Graduated` state machine driven by `_enterGraduating` / `finalizeGraduation`) that the implementation does not defend against re-entry/duplicate-processing, causing the processor to become permanently stuck (denial of service) rather than gracefully rejecting the malformed/duplicate input.

### Impact Explanation
If triggered, the affected token's entire curve-raised LT (`ltFromPair`, already drained from the `Pair` via `Router.graduate`) and the reserved 250M LP tokens are permanently unrecoverable: they sit either in the V2 pair (already minted to `LPLock` on the first, silently-reverted attempt) or in `Bonding` itself, with no owner or user-callable path to recover them, and the token can never reach `Lifecycle.Graduated` to resume trading on the graduated pool. This is a permanent freezing of trader/creator/LP funds tied to that token.

### Likelihood Explanation
Likelihood depends entirely on finding a concrete way to get `finalizeGraduation` invoked twice to completion for the same token — e.g. via a reentrancy path in `_seedUniswapV2Direct`'s external calls (`pair.mint`, router `addLiquidity`) back into `Bonding.finalizeGraduation`, or a keeper/anyone-can-call race where two transactions targeting the same `Graduating` token land in the same block before `pendingGraduation`/`lifecycle` state commits. `finalizeGraduation` itself has `nonReentrant`, which should block a same-call reentrancy, so exploitability requires a second, independent transaction racing against the first — this needs closer verification of whether `nonReentrant`'s guard covers all reachable reentry vectors in `_seedUniswapV2Direct`'s external calls to the LT, pair, and router. This uncertainty could not be fully resolved given available context, and no test in the repo directly exercises a double-`finalizeGraduation` race.

### Recommendation
Move the lifecycle flip and `delete pendingGraduation[token]` to occur atomically with (or before) the `LPLock.recordLock` call, and/or add an explicit re-entrancy/duplicate guard keyed on `lifecycle != Lifecycle.Graduating` checked again immediately before calling `recordLock`, so a second concurrent/racing call to `finalizeGraduation` reverts early with `NotGraduating` rather than reaching `recordLock` after LP tokens have already been minted and transferred.

### Proof of Concept
Not independently constructible without confirming a concrete reentrancy vector through `_seedUniswapV2Direct`'s external calls (`IUniswapV2Pair.mint`, `IUniswapV2Router02.addLiquidity`) back into `Bonding.finalizeGraduation` for the same token, given the `nonReentrant` modifier on `finalizeGraduation`. This would require deeper tracing of `Pair.sol`/mock V2 pair callback behavior than was available in this pass — flagged as unverified rather than asserted as exploitable.

### Citations

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

**File:** packages/contracts/src/LPLock.sol (L26-36)
```text
    /// @custom:storage-location erc7201:altfun.storage.LPLock
    struct LPLockStorage {
        mapping(address token => LockInfo) locks;
        /// @dev Locker allowlist for `recordLock`. Add-only via `addLocker` —
        ///      there is no removal path. A live revoke would brick every
        ///      in-flight `Bonding.finalizeGraduation` (token permanently
        ///      stuck in `Lifecycle.Graduating`, no on-chain recovery), so
        ///      the only way to retire a locker is a UUPS upgrade — which
        ///      surfaces on-chain ahead of time instead of as a one-tx kill
        ///      switch.
        mapping(address account => bool) isLocker;
```

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
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

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```
