### Title
Two-phase graduation has no rollback / cancel path — a failed Phase 2 permanently freezes curve-raised funds and un-graduatable tokens - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding` splits graduation into two independent transactions to fit HyperEVM's small-block gas ceiling. Phase 1 (`_enterGraduating`) irreversibly commits state — drains the curve's real LT into `Bonding`, burns unsold/excess tokens, flips `Lifecycle.Curve → Graduating`, and freezes all further trading — in its own committed transaction, with the LP-seeding amounts merely cached for Phase 2. There is no mechanism to unwind Phase 1 or return the token to `Lifecycle.Curve` if Phase 2 (`finalizeGraduation`) can never succeed for that specific token/pair. This is the same bug class as the ftrace CVE: a registration/state-transition step that commits successfully is never rolled back when a later, dependent step fails, leaving the system holding a permanently dangling, unusable reference — here, curve-raised LT and 250M reserve tokens parked in `Bonding` forever, and a token frozen in `Lifecycle.Graduating` with no exit.

### Finding Description
`Bonding._executeBuy` and `Bonding.triggerGraduation` both call `_enterGraduating`, which: [1](#0-0) 

This function calls `_prepareGraduationLiquidity`, which **immediately and irreversibly** drains the curve's real LT into `Bonding` via `_s().router.graduate(...)` and burns unsold/excess tokens — before Phase 2 has run at all: [2](#0-1) 

Once this transaction lands, `info.lifecycle = Lifecycle.Graduating` is permanent for that token in this call's context; `Bonding.buy`/`Bonding.sell` unconditionally revert with `TokenIsGraduating` while in this state (confirmed by `test_phase1_buy_during_pending_reverts` / `test_phase1_sell_during_pending_reverts`), and `triggerGraduation` itself reverts if called again on a `Graduating` token: [3](#0-2) 

`finalizeGraduation` is the *only* path back out of `Lifecycle.Graduating`: [4](#0-3) 

There is no `cancelGraduation`, no timeout, and no code path anywhere in `Bonding.sol` that reverts a token from `Lifecycle.Graduating` back to `Lifecycle.Curve` (verified by grepping the contract for lifecycle transitions — the only exits from `Graduating` are `finalizeGraduation`'s single success path). The protocol's own documentation concedes that the defenses making `finalizeGraduation` "brick-proof" against every pre-seed shape are no longer fully covered by automated regression tests, i.e., the invariant that Phase 2 "must never revert under any pre-seed shape" is asserted but not continuously enforced: [5](#0-4) 

This is structurally identical to the ftrace CVE: `ftrace_startup` commits a registration (`add_ftrace_ops`) and only later attempts to enable it; when the enable step fails, the registration is never unwound, and any code that assumes "registered ⇒ still valid" walks a now-dangling/freed reference. Here, `_enterGraduating` commits an irreversible state transition (drain LT, burn tokens, freeze trading) assuming `finalizeGraduation` will always subsequently succeed; if that later step is bricked for a given token/pair for any reason not covered by the (now partially untested) defense set, the committed state is never unwound — the token, its raised LT, and its LP_RESERVE tokens are permanently stuck with no on-chain recovery.

### Impact Explanation
If any curve reaches `Lifecycle.Graduating` and `finalizeGraduation` subsequently cannot complete for that specific token/pair (e.g., a regression in the untested hostile-pre-seed defenses, or any other pair-specific state that causes every branch of `_seedUniswapV2Direct` to revert), the impact is a **permanent freeze of funds**:
- All curve-raised LT already drained into `Bonding` via `Router.graduate` is unrecoverable by any trader or the creator.
- The 250M `LP_RESERVE` tokens sitting in `Bonding` for that token can never be deployed to an LP or reclaimed.
- Every existing token holder on that curve is permanently locked out of trading (`TokenIsGraduating` blocks both buy and sell indefinitely), with no way to exit even at the frozen curve price.
- The creator can never claim/earn further fees on that token, and the token can never reach a tradable post-graduation state.

This satisfies "permanent freezing of trader, creator or LP funds" from the validation criteria and is High severity given it can render an entire token's raised capital and holder positions permanently inaccessible with a single, permissionless, unprivileged call sequence (`buy`/`triggerGraduation` reaching threshold, then a `finalizeGraduation` that cannot land).

### Likelihood Explanation
`_enterGraduating` fires automatically and permissionlessly on any buy that crosses the graduation threshold, or via the permissionless `triggerGraduation`, meaning any unprivileged trader can push a curve into the irreversible `Graduating` state. Whether `finalizeGraduation` subsequently gets stuck depends on it hitting an untested/regressed branch of the hostile-pre-seed defense (the team's own AGENTS.md admits the dedicated end-to-end regression suite for these exact properties was removed and "is no longer enforced by automated tests"). Given the complexity of `_seedUniswapV2Direct`/`_seedRebalancing`/`_routerDepositAndDispose`/`_pairRebalance` and the admitted lack of regression coverage, the likelihood of an edge case causing a permanent, un-rollback-able brick is non-trivial, and the root architectural flaw — no rollback path at all once Phase 1 commits — is fully deterministic and always present regardless of which specific edge case triggers it.

### Recommendation
Add a permissionless rescue/rollback path: if `finalizeGraduation` cannot succeed within a bounded window (or after a fixed number of failed attempts/blocks), allow reverting `Lifecycle.Graduating → Curve` (or a dedicated `Failed` state) that restores tradability and/or lets holders redeem their pro-rata share of the drained LT and reserved tokens directly from `Bonding`. At minimum, add a superuser/owner emergency path (distinct from the permissionless keeper path) that can manually re-seed or refund a token stuck in `Graduating`, so that a bug in the brick-resistance logic degrades to an operational incident rather than a permanent, protocol-level loss of funds. Restore and keep running the removed `HostilePreSeed.t.sol` end-to-end suite so regressions in the very code this fix depends on are caught before they can strand a graduation.

### Proof of Concept
Conceptual PoC (illustrating the missing-rollback root cause; the specific revert trigger inside `_seedUniswapV2Direct` depends on which untested edge case is hit):
1. Attacker/trader buys on a fresh curve until `canGraduate(tokenAddress)` is true (`Bonding._executeBuy` → `canGraduate` → `_enterGraduating`), or calls `Bonding.triggerGraduation(tokenAddress)` directly once `canGraduate` is true.
2. `_enterGraduating` executes: `Lifecycle.Curve → Graduating`, `_prepareGraduationLiquidity` calls `_s().router.graduate(token, ltFromPair)` (draining the pair's real LT into `Bonding`) and burns `unsoldBurned`/`lpBurned` tokens. This transaction is fully committed on-chain.
3. Any subsequent call to `Bonding.buy`/`sell` for `tokenAddress` now permanently reverts with `TokenIsGraduating` (confirmed by `test_phase1_buy_during_pending_reverts`, `test_phase1_sell_during_pending_reverts` in `TwoPhaseGraduation.t.sol`).
4. `finalizeGraduation(tokenAddress)` is called by the keeper or any permissionless caller, but reverts because it hits a branch of `_seedUniswapV2Direct`/`_seedRebalancing`/`_routerDepositAndDispose` not covered by the (admittedly reduced) test suite — e.g., an interaction the removed `HostilePreSeed.t.sol` integration tests used to exercise.
5. Because `Bonding.sol` has no code path other than a successful `finalizeGraduation` to leave `Lifecycle.Graduating`, the token, its drained LT (`ltFromPair`), and its `LP_RESERVE` tokens are now permanently stuck: no trader can buy/sell, no creator can graduate, and no funds can ever be recovered — the analog of the ftrace bug's un-rolled-back, permanently dangling registration.

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

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

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

**File:** packages/contracts/AGENTS.md (L223-231)
```markdown
### Tests you MUST re-run if you change any of this

- `test/NoFeeSwapInput.t.sol` — 9 deterministic + 2 fuzz tests on the load-bearing math (degenerate inputs, monotonicity, cap-at-budget, closed-form correctness, overflow safety, the round-down-to-zero input shape that motivated the precheck).
- `test/TwoPhaseGraduation.t.sol` — brick-resistance + phase-1-fits-in-small-block tests, plus the hostile-pre-seed open-at-cached-ratio tests (`test_hostilePreSeed_*`) covering both the dust direct-mint fallback and the meaningful-reserve swap path, must still pass.
- `test/GraduationInvariants.t.sol` — zero-gap, supply conservation, parabola cap. Honest-path properties unchanged by the defense.

The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.

These invariants are the security contract — do not loosen the remaining assertions to make a change go green.
```
