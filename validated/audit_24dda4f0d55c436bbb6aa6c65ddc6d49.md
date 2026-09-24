## Analog Found

### Title
`LPLock.recordLock`'s `ZeroAmount` guard can permanently brick `Bonding.finalizeGraduation`, freezing all curve-raised LT and the 250M LP reserve — ([File: packages/contracts/src/LPLock.sol])

### Summary
The ALPINE-CVE-2022-44793 class is: an unauthenticated/unprivileged actor sends crafted input that hits an unhandled edge case, causing the target to enter a state it cannot recover from (a "crash"). The alt.fun analog is in the permissionless, two-phase graduation state machine: `Bonding.finalizeGraduation` unconditionally forwards whatever `liquidity` the LP-seeding path computes into `LPLock.recordLock`, and `recordLock` reverts on `amount == 0`. If any hostile-pre-seed shape (a class the protocol's own docs acknowledge and partially defend against) drives the computed `liquidity` to zero, `finalizeGraduation` reverts every single time it's called — permanently, since the cached `pendingGraduation[token]` inputs are deterministic and never change. The token is stuck in `Lifecycle.Graduating` forever with no on-chain recovery path.

### Finding Description
`Bonding.finalizeGraduation` computes `liquidity` from `_seedUniswapV2Direct` and passes it straight to the lock: [1](#0-0) 

`LPLock.recordLock` has a hard `ZeroAmount` revert: [2](#0-1) 

The protocol's own natspec on `Bonding._swapBudget` explicitly names the failure mode this analog exploits — an "extreme hostile pre-seed" driving the rebalance swap to consume 100% of one side, causing `_routerDepositAndDispose` to skip `addLiquidity` (because `remToken == 0` or `remLT == 0`), so `finalizeGraduation` returns `liquidity = 0`: [3](#0-2) 

The `_swapBudget` 99%/1% split is the only defense against this, and it is bounded by the *contract's own inventory* (`tokensForLP` / `ltFromPair`), not by the attacker's pre-seed size. For a token whose graduation lands with a very small `tokensForLP` or `ltFromPair` (e.g., a threshold-leg graduation that fires just barely, or a supply-leg graduation on a near-empty curve), `1%` of a small integer can itself round to `0`, forcing `maxSwap = 0` and pushing the flow into the `_seedDirectMint` fallback — which itself is only safe as long as `sqrt(amount0*amount1) > MINIMUM_LIQUIDITY` inside the V2 pair's `mint`. Any pre-seed/graduation-size combination that lands below that threshold, or any combination where the swap/deposit legs otherwise produce a `0` liquidity mint, is unconditionally fatal: there is no `try/catch`, no fallback amount floor, and no owner rescue path around the `recordLock` call.

This is reachable entirely by unprivileged actions: (1) create the HyperSwap V2 pair via the permissionless factory, (2) `transfer`/`sync` a dust or imbalanced pre-seed into it before phase 2 runs, and (3) let (or force, since `finalizeGraduation` is permissionless) `finalizeGraduation` execute against that pre-seed. No privileged role is needed anywhere in this path.

### Impact Explanation
Once a token's `finalizeGraduation` reverts on the `ZeroAmount` check, it reverts on every future call too, because `pendingGraduation[tokenAddress]` and the pair's post-phase-1 reserves are frozen and byte-identical on every retry (`_prepareGraduationLiquidity`'s outputs are cached, and `finalizeGraduation` recomputes the same deterministic swap/deposit split from them). The token is permanently stuck in `Lifecycle.Graduating`: trading is frozen (`isTrading` requires `Lifecycle.Curve`), the entire curve-raised LT (`ltFromPair`) sitting in `Bonding` is unreachable (no sell/withdraw path exists once curve trading is frozen), and the 250M `LP_RESERVE` tokens are permanently orphaned. This is a full, protocol-level, permanent freeze of trader and creator funds for that token — exactly the "permanent freezing of trader, creator or LP funds" impact class the rules call out.

### Likelihood Explanation
The attack requires only unprivileged calls (`factory.createPair`, ERC20 `transfer`, `sync`, and calling/waiting for `finalizeGraduation`), matching the "unprivileged trader/creator/wallet" reachability bar. The protocol's own comments acknowledge the zero-liquidity failure mode is a real, previously-considered risk (`_swapBudget`'s natspec), and the fix is only a probabilistic mitigation (a 99/1 split whose 1% floor is not bounded away from zero for small-value graduations) rather than an absolute guarantee that `liquidity > 0` on every code path into `recordLock`. The dedicated end-to-end hostile-pre-seed test suite (`test/HostilePreSeed.t.sol`) that would have caught edge cases in this exact area was explicitly removed per the AGENTS.md notes, reducing confidence that all zero-liquidity edge cases are actually covered by current tests.

### Recommendation
Make `finalizeGraduation` non-bricking on a zero-liquidity outcome instead of propagating the revert into a state with no recovery: either (a) skip the `LPLock.recordLock` call when `liquidity == 0` and still flip `Lifecycle.Graduating → Graduated` (documenting that a degenerate pre-seed forfeited LP-lock bookkeeping for that token), or (b) add an explicit floor in `_seedUniswapV2Direct`/`_routerDepositAndDispose` that guarantees a non-zero mintable amount regardless of pre-seed size (e.g., bound the swap/deposit legs by an absolute minimum rather than a percentage of the (possibly tiny) available inventory). Add fuzzed regression coverage (replacing the removed `HostilePreSeed.t.sol`) that sweeps small `tokensForLP`/`ltFromPair` values against a spectrum of hostile pre-seed ratios to confirm `finalizeGraduation` never reverts.

### Proof of Concept
1. Launch a token and drive it to `Lifecycle.Graduating` via a graduation where the cached `tokensForLP` or `ltFromPair` in `pendingGraduation[token]` is very small (e.g., a supply-leg graduation on a curve with a tiny seed, or a threshold-leg graduation that fires just above the minimum).
2. Before `finalizeGraduation` is called, front-run: call `hyperswapFactory.createPair(token, lt)`, then `transfer` a small, deliberately imbalanced amount of `token`/`lt` into the pair and call `sync()` (the same "sync-dust" primitive already exercised in `test/TwoPhaseGraduation.t.sol`), sized so that the 1% swap-budget reservation together with the imbalance drives the eventual deposit leg's mintable `liquidity` to `0` (or below `MINIMUM_LIQUIDITY` in the `_seedDirectMint` fallback).
3. Call `Bonding.finalizeGraduation(token)`. `_seedUniswapV2Direct` returns `liquidity = 0`, and the subsequent `LPLock($.lpLock).recordLock(tokenAddress, lpPair, 0)` call reverts with `ZeroAmount`, rolling back the entire `finalizeGraduation` transaction (including the `Lifecycle.Graduating → Graduated` flip).
4. Repeat step 3 indefinitely: every call reverts identically, since `pendingGraduation[token]` and the pair reserves are frozen — the token is permanently stuck in `Lifecycle.Graduating`, and its curve-raised LT plus the 250M LP reserve are permanently unrecoverable.

### Citations

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
