### Title
Hostile pre-seed of the HyperSwap pair can force `finalizeGraduation` into a permanent revert via `LPLock.recordLock`'s zero-amount guard, bricking graduation forever - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` (phase 2 of graduation) computes the LP amount to lock and unconditionally calls `LPLock.recordLock(tokenAddress, lpPair, liquidity)` at the end. `LPLock.recordLock` reverts with `ZeroAmount` if `amount == 0` [1](#0-0) . The contract's own natspec documents a code path in which the hostile-mint-pre-seed defense can drive the computed `liquidity` to zero, at which point `recordLock` would revert rather than "recording a zero-sized lock" as the comment assumes [2](#0-1) . Because `finalizeGraduation` is the *only* path from `Lifecycle.Graduating` to `Lifecycle.Graduated`, and there is no owner/admin override or lifecycle-reset function anywhere in `Bonding.sol`, a token that hits this branch is permanently stuck in `Lifecycle.Graduating` — freezing all curve-raised LT and the 250M `LP_RESERVE` tokens parked in `Bonding` for that token, forever.

### Finding Description
The two-phase graduation design deliberately parks all curve-raised LT (`ltFromPair`) and the 250M token `LP_RESERVE` inside `Bonding` between phase 1 (`_enterGraduating`) and phase 2 (`finalizeGraduation`) [3](#0-2) . Phase 2 is explicitly documented as permissionless and required to "never revert under any pre-seed shape" [4](#0-3) .

The hostile-pre-seed defense (`_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` / `_routerDepositAndDispose`) caps the rebalance swap at 99% of the available side's budget specifically to guarantee the subsequent `addLiquidity` deposit always has non-zero amounts on both sides [2](#0-1) . The comment on `_swapBudget` explicitly states the failure mode this is defending against: "`_routerDepositAndDispose` then skips `addLiquidity` (`remToken == 0` or `remLT == 0`), `finalizeGraduation` returns `liquidity = 0`, and `LPLock.recordLock(...)` records a zero-sized lock" [5](#0-4) .

This statement is factually inconsistent with `LPLock.recordLock`'s actual guards: `recordLock` reverts with `ZeroAmount` whenever `amount == 0`, before any state is written [1](#0-0) , confirmed by `test_recordLock_revertsOnZeroAmount` [6](#0-5) . So the "zero-sized lock" the mitigation comment describes as the residual risk does not merely record a no-op — it reverts the entire `finalizeGraduation` transaction.

`finalizeGraduation` performs `info.lifecycle = Lifecycle.Graduated` and `delete $.pendingGraduation[tokenAddress]` only *after* `_seedUniswapV2Direct` returns and *before* calling `LPLock.recordLock` [7](#0-6) ; because `recordLock` reverts, the whole transaction (including the lifecycle flip and the `delete`) is rolled back atomically. The token remains in `Lifecycle.Graduating`. Since `_prepareGraduationLiquidity`'s cached `(tokensForLP, ltFromPair)` are frozen and the hostile pair reserves the attacker seeded do not change on their own, every subsequent call to `finalizeGraduation` (permissionless, callable by anyone) recomputes essentially the same rebalance/deposit path and hits the same `liquidity == 0` outcome, reverting every time. There is no lifecycle-reset function, no owner escape hatch, and `triggerGraduation`/`buy`/`sell` all revert for a token in `Lifecycle.Graduating` [8](#0-7) , so the token, its curve-raised LT, and the 250M `LP_RESERVE` tokens sitting in `Bonding` are permanently frozen with no on-chain recovery — directly analogous to the referenced report's `anchorGame` permanently blacklisted state that can never be updated via `setAnchorState()`, breaking all downstream flows that depend on it.

### Impact Explanation
This permanently freezes:
- All real LT raised by the bonding curve for the affected token (`ltFromPair`, drained into `Bonding` by `Router.graduate` during phase 1) [9](#0-8) .
- The 250M `LP_RESERVE` tokens reserved for LP seeding, since `_prepareGraduationLiquidity` already burned/allocated them at phase 1 and the token can never reach `Lifecycle.Graduated` to release them into a working pool [10](#0-9) .
- All traders holding the token pre-graduation, who can no longer buy/sell (curve is frozen in `Graduating`) nor trade post-graduation (graduation never completes).

This is a permanent freezing of trader/LP funds trapped inside `Bonding`, matching the "Medium/High" impact bar from the rules.

### Likelihood Explanation
Reaching this state requires an unprivileged attacker to construct an extreme hostile mint-pre-seed on the HyperSwap `TOKEN/LT` pair between phase 1 (`_enterGraduating`, which fires inline on a threshold-crossing buy or via permissionless `triggerGraduation`) and phase 2 (`finalizeGraduation`), skewing reserves so severely that even after the 99%-budget-capped rebalance swap, the resulting deposit still rounds to a `liquidity == 0` mint (e.g. via the `_seedDirectMint` fallback minting `min(amount0·totalSupply/reserve0, amount1·totalSupply/reserve1)` against astronomically large attacker-seeded reserves relative to the graduation's real inventory). Both `pair.mint` and pre-creating the pair are permissionless HyperSwap V2 operations reachable by any wallet, and the window between phase 1 and phase 2 is attacker-observable on-chain. The protocol's own code comments acknowledge this residual edge case exists and only partially mitigate it (99% budget cap addresses the common case but the fallback direct-mint path's rounding-to-zero is not itself guarded).

### Recommendation
- Do not let a `liquidity == 0` result from `_seedUniswapV2Direct` propagate into an unconditional `LPLock.recordLock` call that reverts the whole transaction. Either guarantee `liquidity > 0` is unreachable via a stronger invariant check inside `_seedDirectMint`/`_routerDepositAndDispose`, or make `finalizeGraduation` tolerant of a zero-liquidity outcome (e.g., skip `recordLock` and still flip `Lifecycle` to `Graduated`, or add a distinct recovery/retry path with an adjusted seeding strategy) so a hostile pre-seed can never leave a token permanently parked in `Lifecycle.Graduating`.
- Add a fuzz/invariant test that specifically drives `_seedRebalancing`'s fallback (`_seedDirectMint`) against reserves several orders of magnitude larger than the graduation's cached `(tokensForLP, ltFromPair)`, asserting `finalizeGraduation` never reverts and always completes the lifecycle transition.
- Reconcile the `_swapBudget` natspec (which assumes `recordLock` tolerates zero) with `LPLock.recordLock`'s actual `ZeroAmount` guard.

### Proof of Concept
1. Attacker monitors for a token approaching its graduation threshold (`canGraduate`) or calls `triggerGraduation` themselves once `canGraduate` is true, firing phase 1 (`_enterGraduating`) and caching `(tokensForLP, ltFromPair)` at the last curve price.
2. Before anyone calls `finalizeGraduation`, attacker front-runs by calling `factory.createPair(token, lt)` (or reuses an existing empty pair), then transfers an extremely large, hostilely-imbalanced amount of `LT` and `token` into the pair and calls `pair.mint(attacker)`, minting themselves LP at a hostile ratio with reserves many orders of magnitude larger than the graduation's real `(tokensForLP, ltFromPair)` inventory.
3. Anyone calls `Bonding.finalizeGraduation(tokenAddress)`. `_seedUniswapV2Direct` routes to `_seedRebalancing`, the rebalance swap is capped at 99% of the (small) real inventory and cannot meaningfully move the now-astronomically-skewed reserves, `_pairRebalance` returns `false` or negligible movement, and the fallback `_seedDirectMint` mints `liquidity = min(amount0·totalSupply/reserve0, amount1·totalSupply/reserve1)` against the attacker's huge reserves, rounding to `0`.
4. `finalizeGraduation` calls `LPLock.recordLock(tokenAddress, lpPair, 0)`, which reverts with `ZeroAmount`, rolling back the entire transaction (including the lifecycle flip to `Graduated`).
5. Every subsequent call to `finalizeGraduation` recomputes the same values against the same hostile reserves and reverts identically. The token is permanently stuck in `Lifecycle.Graduating`; its curve-raised LT and the 250M `LP_RESERVE` tokens remain locked in `Bonding` indefinitely with no recovery function available.

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

**File:** packages/contracts/src/Bonding.sol (L973-979)
```text
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1022-1031)
```text
        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);
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

**File:** packages/contracts/AGENTS.md (L85-86)
```markdown
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```

**File:** packages/contracts/test/LPLock.t.sol (L145-149)
```text
    function test_recordLock_revertsOnZeroAmount() public {
        vm.prank(bonding);
        vm.expectRevert(LPLock.ZeroAmount.selector);
        lpLock.recordLock(tokenAddr, pairAddr, 0);
    }
```
