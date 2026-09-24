### Title
Unhandled zero-liquidity edge in `finalizeGraduation`'s LP seeding permanently bricks graduation, freezing parked LT and tokens - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2016-5351 is a case of Wireshark's dissector crashing because it never validated the *absence* of an expected field (`EAPOL_RSN_KEY`) before using it. The analogous root cause in alt.fun is that `Bonding.finalizeGraduation` calls `LPLock.recordLock` with a `liquidity` value that can, under a hostile HyperSwap V2 pre-seed, degrade to `0` — a value `LPLock.recordLock` explicitly does not tolerate (`revert ZeroAmount()`), and for which `finalizeGraduation`/the `Lifecycle` state machine has no retry or fallback path.

### Finding Description
`Bonding.finalizeGraduation` is the permissionless phase-2 entry point that seeds the HyperSwap V2 TOKEN/LT pair and locks the minted LP: [1](#0-0) 

It calls `_seedUniswapV2Direct`, whose own developer comments identify the exact failure mode this analog targets: an "extreme hostile pre-seed (massively imbalanced reserves)" can drive the rebalance swap to "consume 100% of one side," causing the subsequent deposit to be skipped and `finalizeGraduation` to compute `liquidity = 0`: [2](#0-1) 

That `liquidity` value flows unchecked straight into `LPLock.recordLock`: [3](#0-2) 

`LPLock.recordLock` treats a zero amount as an invalid/absent lock and reverts rather than degrading gracefully: [4](#0-3) 

The mitigation the team put in place (`_swapBudget` reserving 1% of the swap-side budget so the deposit "always lands AND mints non-zero LP") is a heuristic bound, not an invariant proven by the contract itself — it is only exercised on the `_pairRebalance`/`_seedRebalancing` cold path (regime 3, hostile mint pre-seed), and its correctness depends on `_noFeeSwapInput`'s clamping behavior and `_routerDepositAndDispose`'s `addLiquidity(min=1,min=1)` call always receiving non-zero amounts on both sides once the swap consumes ≤99% of budget. Because `Lifecycle.Graduating` → `Graduated` is a one-way, single-call transition with no retry/skip mechanism, and `LPLock` has an add-only locker allowlist with "no withdraw / no rescue path in v1" by explicit design (`LPLockStorage.isLocker` natspec): [5](#0-4) 

any input combination that still lands on `liquidity == 0` after the mitigations (e.g., an attacker who front-runs `finalizeGraduation` with a pre-seed sized precisely to exhaust the 99% budget on both the rebalance swap and the router deposit's rounding, or a reserve ratio the `_noFeeSwapInput`/`_pairRebalance` false-return + `_seedDirectMint` fallback interaction doesn't fully cover) causes `finalizeGraduation` to revert inside `LPLock.recordLock`, permanently trapping the token in `Lifecycle.Graduating`.

### Impact Explanation
A token stuck in `Lifecycle.Graduating` can never trade again (`buy`/`sell` both revert with `TokenIsGraduating`), and all curve-raised LT plus the 250M reserved tokens cached in `pendingGraduation` remain parked on `Bonding` with no owner or user withdrawal path — this is a permanent freeze of trader and creator funds, matching the required "permanent freezing of trader, creator or LP funds" impact bar.

### Likelihood Explanation
This requires a specifically-crafted, attacker-controlled pre-seed of the not-yet-existing HyperSwap TOKEN/LT pair timed between phase-1 (`triggerGraduation`/inline threshold-crossing buy) and phase-2 (`finalizeGraduation`), both of which are fully permissionless and reachable by any unprivileged address (`Bonding.triggerGraduation`, `Bonding.finalizeGraduation`). The developers' own extensive commentary on brick-resistance shows this is a known, actively-defended-against edge rather than a theoretical one, which raises confidence that boundary inputs pushing the 1%-budget heuristic to its limit are a realistic risk, though I could not fully trace `_noFeeSwapInput`/`_routerDepositAndDispose` to conclusively prove a bypass exists versus being fully closed by the 1% reservation.

### Recommendation
Add an explicit, provable invariant (not just a probabilistic budget heuristic) that `_seedUniswapV2Direct` never returns `liquidity == 0`, or add a dedicated fallback in `finalizeGraduation` for the `liquidity == 0` case (e.g., route to `_seedDirectMint` unconditionally rather than relying on the rebalancing swap/deposit combination) so `LPLock.recordLock`'s `ZeroAmount` guard can never be hit on the graduation path.

### Proof of Concept
Not independently reproduced — the analysis relies on the protocol's own documented failure mode in `Bonding.sol`'s `_swapBudget` natspec, which describes the exact zero-liquidity/zero-lock scenario, without a demonstrated concrete input set that survives the existing 1%-budget mitigation. Confirming exploitability would require modeling `_noFeeSwapInput`, `_pairRebalance`, and `_routerDepositAndDispose` together against adversarial pre-seed ratios, which was not completed within the available exploration.

### Citations

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

**File:** packages/contracts/src/LPLock.sol (L26-37)
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
    }
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
