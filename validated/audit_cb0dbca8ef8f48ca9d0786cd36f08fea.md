### Title
Permissionless hostile pre-seeding of the HyperSwap V2 TOKEN/LT pair lets an attacker force `Bonding.finalizeGraduation` to seed the permanently-locked LP away from the curve-close price (and can revert-lock the graduation entirely) - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The external report's bug class is a permissionless, unauthenticated action (`socket.emit('UNSUBSCRIBE', ARCHIVER_PUBLIC_KEY)`) that lets any unprivileged party trigger a privileged-effect state transition with no signature/consent check, causing irreversible network damage. The Alt Fun analog is `Bonding._seedUniswapV2Direct` / `_seedRebalancing` / `_pairRebalance`, which is invoked from the fully permissionless `finalizeGraduation(tokenAddress)` [1](#0-0) . Any address can pre-create the HyperSwap V2 `TOKEN/LT` pair and `mint` a hostile, self-funded LP position into it *before* the token graduates. When `finalizeGraduation` later runs, `_seedRebalancing`'s ratio-correction swap is explicitly budget-capped at 99% of the available side [2](#0-1) , so for a sufficiently extreme pre-seed the post-swap pool ratio never actually reaches the curve-close price — the code's own comment on `_pairRebalance` documents that a large-enough pre-seed leaves the deposit landing at an off-ratio price rather than reverting. Because the attacker's pre-existing LP shares are already sitting in the pool when Bonding's `router.addLiquidity(..., min=1, min=1, ...)` deposits at that skewed ratio [3](#0-2) , the attacker's LP position captures a disproportionate share of the curve-raised LT and the 250M reserved tokens that `Bonding` is depositing on behalf of every trader/creator of that token — value that, once minted to `LPLock`, can never be withdrawn (`LPLock` has "No withdraw in v1") [4](#0-3) .

### Finding Description
`finalizeGraduation` is permissionless by design ("keeper drives the happy path; anyone can rescue a stuck token") [5](#0-4) . It depends on `_ensureUniswapV2Pair`, which either fetches or *creates* the V2 pair for `(token, lt)` [6](#0-5)  — meaning nothing stops any address from creating that pair and seeding it with liquidity via `pair.mint` long before the token's curve even reaches the graduation trigger.

`_seedUniswapV2Direct` handles this "mint pre-seed" as "Regime 3": it routes into `_seedRebalancing`, which computes whether the pool is TOKEN-rich or LT-rich relative to the cached curve-close ratio `(tokensForLP, ltFromPair)` and calls `_pairRebalance` to swap toward that ratio [7](#0-6) . The swap input is deliberately capped:

```
function _swapBudget(uint256 budget) internal pure returns (uint256) {
    return (budget * 99) / 100;
}
``` [8](#0-7) 

The contract's own natspec on this function admits the trade-off: *"for any realistic pre-seed `s_unconstrained` is orders of magnitude below `maxSwap`, so the cap doesn't bind and behaviour is unchanged. It only kicks in for catastrophic pre-seeds beyond our budget capacity, where the alternative is bricking."* [9](#0-8)  — i.e. the developers explicitly chose "seed at an incorrect price" over "revert," for the case where an attacker's pre-seed is large enough that the full corrective swap would exceed Bonding's own LT/TOKEN inventory for that graduation.

When the cap binds, `_pairRebalance`'s swap only partially corrects the ratio, and `_routerDepositAndDispose` then deposits the remaining `(remToken, remLT)` into the pool via `addLiquidity(..., 1, 1, lpLock_, ...)` at whatever ratio the pool is left at — not the true curve-close ratio [3](#0-2) . Because the attacker's own LP shares were minted into that pool before this deposit, the attacker earns a proportional claim on the newly-deposited reserves at the mispriced ratio, extracting value that should have accrued entirely to the (permanently locked, non-withdrawable) protocol LP.

The same code path also documents a related, more severe failure mode: `_noFeeSwapInput`'s `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` is explicitly noted to `revert` (not truncate) for "constructed adversarial inputs" whose result doesn't fit in `uint256` [10](#0-9) . Since `reserveIn`/`reserveOut` are attacker-controlled (via the pre-seed), such a revert propagates all the way out of `finalizeGraduation`. Because all of `finalizeGraduation`'s state writes (`info.lifecycle = Graduated`, `graduatedPair[...]`, `delete pendingGraduation[...]`, `LPLock.recordLock`) happen in the same transaction with no partial-commit path [11](#0-10) , a revert here leaves the token permanently stuck in `Lifecycle.Graduating` — trading frozen, curve-raised LT and the 250M `lpReserve` tokens permanently parked inside `Bonding` with no retry path, since the hostile pre-seed persists forever and every retry hits the same computation.

### Impact Explanation
This breaks the "Accept only concrete theft or permanent freezing of trader, creator or LP funds ... an LP seeded away from the curve close price" bar directly:
- **Theft/value leak**: an unprivileged attacker permanently captures part of the curve-raised LT and reserved 250M tokens that `Bonding` deposits into the graduation LP, by pre-seeding the pool to force the budget-capped rebalance to land off the curve-close price. That value is locked forever in `LPLock` (no withdraw path), so it is not recoverable by the protocol, the creator, or curve traders.
- **Permanent freeze (compounding)**: in the more extreme pre-seed case, the `Math.mulDiv` overflow-revert path can permanently strand a token in `Lifecycle.Graduating`, freezing all of that token's curve-raised LT and 250M reserved tokens inside `Bonding` with no recovery mechanism.

Both effects are reachable purely through `Bonding.launch`/curve trades to get a token graduating, a HyperSwap `Factory.createPair` + `pair.mint` self-seed by any wallet, and the pre-existing permissionless `finalizeGraduation` call — no privileged role, no signature, exactly the class of "anyone can disrupt a critical, load-bearing state transition" in the original report.

### Likelihood Explanation
Medium-to-High: creating a V2 pair and minting an unbalanced LP position is a normal, unrestricted DeFi action available to any wallet before a target token's curve crosses its graduation trigger (which is public/predictable via `canGraduate`/`previewLtUntilGraduation`). The defensive code's own comments acknowledge the budget cap is designed to bind only for "catastrophic" pre-seeds — i.e. the authors already know sufficiently large pre-seeds defeat full correction; an attacker only needs to size the pre-seed relative to the specific token's expected `(tokensForLP, ltFromPair)` at graduation, which is derivable from `Pair.k()` and curve state ahead of time.

### Recommendation
- Reject or fully neutralize hostile pre-existing LP positions rather than depositing around them at a skewed ratio — e.g., require the pool's `totalSupply()` to be zero at `finalizeGraduation` time (revert/queue otherwise) so no third-party LP shares can ever share in the protocol's deposit, or route all pre-existing LP supply through a burn/skim step before any deposit.
- If a swap-budget cap must exist to avoid bricking, refuse to deposit at an off-target ratio instead of silently accepting the residual mispricing — either escrow the excess and let the *next* graduation absorb it, or send the shortfall to the protocol treasury rather than letting third-party pre-existing LP shares dilute it.
- Bound `_noFeeSwapInput`'s inputs (or use `Math.mulDiv` with a documented safe upper limit and an explicit `try/catch`-style fallback to the direct-mint path) so adversarial reserve values can never cause an unrecoverable revert inside `finalizeGraduation`.

### Proof of Concept
1. Wait for (or pick) a token nearing graduation on `Bonding`; read `Bonding.pendingGraduation`/`previewLtUntilGraduation` to estimate the eventual `(tokensForLP, ltFromPair)` curve-close ratio for that `(token, lt)` pair.
2. From an unprivileged EOA, call `IUniswapV2Factory.createPair(token, lt)` (or let `Bonding._ensureUniswapV2Pair` do it later) and `transfer` + `pair.mint(attacker)` a large, deliberately imbalanced `(TOKEN, LT)` seed sized so the ratio correction required in `_seedRebalancing`/`_pairRebalance` exceeds `_swapBudget`'s 99% cap for that graduation's LT/TOKEN inventory.
3. Trigger the graduation normally (buy/sell into the threshold, or call `Bonding.triggerGraduation(token)` once `canGraduate` is true), then call the permissionless `Bonding.finalizeGraduation(token)`.
4. Observe: the rebalance swap is capped, `_routerDepositAndDispose` deposits the remaining `(remToken, remLT)` at the still-skewed ratio into the pool where the attacker's LP shares already sit, so the attacker's pre-existing LP now claims a portion of the freshly-deposited (curve-raised) reserves. Compare the attacker's post-mint LP value in LT terms before vs. after `finalizeGraduation` to quantify the extracted value, confirming the LP was seeded away from the true curve-close price at the expense of `LPLock`'s permanently-locked funds.

### Citations

**File:** packages/contracts/src/Bonding.sol (L981-1034)
```text
    /// @notice Phase 2: seed the V2 LP and lock it. Permissionless —
    ///         keeper drives the happy path; anyone can rescue a stuck token.
    /// @dev Bypasses the V2 router and calls `pair.mint(lpLock)`
    ///      directly. This is brick-proof against a front-runner pre-creating
    ///      the pair and dust-seeding it between phases.
    /// @dev Exchange-rate drift between phase 1 and phase 2 is accepted by
    ///      design. The cached `(tokensForLP, ltFromPair)` are pure pair-
    ///      state arithmetic — see `_prepareGraduationLiquidity`, which
    ///      never reads `exchangeRate()` — so the LP opens at the exact
    ///      LT-per-token ratio the curve closed at, regardless of how long
    ///      phase 2 takes. What drifts is only the USD denomination of the
    ///      LT side, which is inherent to using a leveraged token as the
    ///      curve reserve: holders accept that exposure when they buy in.
    ///      A keeper Worker drives finalize within ~60s of `TokenGraduating`,
    ///      so the practical drift window is single-digit seconds. No
    ///      freshness timestamp / staleness gate: a recompute would return
    ///      byte-identical values (inputs are frozen while
    ///      `Lifecycle.Graduating`), and re-pricing the LP at the live
    ///      `exchangeRate()` would break the zero-gap-in-LT-units invariant.
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

**File:** packages/contracts/src/Bonding.sol (L1121-1130)
```text
    function _ensureUniswapV2Pair(
        address tokenA,
        address tokenB
    ) internal returns (address pair) {
        IUniswapV2Factory v2Factory = IUniswapV2Factory(_s().uniswapV2Factory);
        pair = v2Factory.getPair(tokenA, tokenB);
        if (pair == address(0)) {
            pair = v2Factory.createPair(tokenA, tokenB);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1275-1354)
```text
    /// @dev Hostile-mint-pre-seed branch of `_seedUniswapV2Direct`. Split
    ///      out because (a) it's the cold path (~99% of graduations hit
    ///      the empty-pair branch above) and (b) the local-variable density
    ///      would otherwise blow stack-too-deep.
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
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

**File:** packages/contracts/src/Bonding.sol (L1449-1473)
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
```

**File:** packages/contracts/src/Bonding.sol (L1488-1522)
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
    ///      uint256. Call sites must keep that invariant — in practice
    ///      both the V2 uint112 reserve cap and the bound that
    ///      `tokensForLP` ≤ `LP_RESERVE` and `ltFromPair` ≤ raised LT
    ///      are well inside the safe envelope. Constructed adversarial
    ///      inputs that violate this would `revert` rather than silently
    ///      truncate, which is the correct failure mode.
    function _noFeeSwapInput(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 targetN,
        uint256 targetD,
        uint256 maxSwap
    ) internal pure returns (uint256) {
        if (reserveIn == 0 || reserveOut == 0 || targetN == 0 || targetD == 0 || maxSwap == 0) {
            return 0;
        }
        uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
        uint256 newIn = Math.sqrt(product);
        if (newIn <= reserveIn) return 0;
        uint256 s = newIn - reserveIn;
        return s > maxSwap ? maxSwap : s;
    }
```

**File:** packages/contracts/src/LPLock.sol (L8-18)
```text
/// @title LPLock
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `LPLockStorage` at `_LP_LOCK_STORAGE_LOCATION`.
```
