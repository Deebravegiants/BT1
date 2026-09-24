This confirms the mechanism: `MockHyperswapPair.mint` (mirroring canonical `UniswapV2Pair`) computes `liquidity = min(amount0*totalSupply/reserve0, amount1*totalSupply/reserve1)` for a non-empty pair and `require(liquidity > 0, "...INSUFFICIENT_LIQUIDITY_MINTED")` [1](#0-0) . This is what backs the finding below.

### Title
Permanent freeze of a graduating token's curve-raised LT and LP-bound tokens via oversized hostile pre-seed of the HyperSwap V2 pair, which drives `finalizeGraduation`'s `addLiquidity`/`pair.mint` to compute `liquidity == 0` and revert deterministically — ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation` is a permissionless, unconditional two-step commit: it deposits into a HyperSwap V2 pair and then calls `LPLock.recordLock`, which has a one-shot, mandatory, non-skippable guard [2](#0-1) . The rebalance/deposit machinery (`_seedRebalancing` → `_pairRebalance` → `_routerDepositAndDispose`) caps the corrective swap at a fixed 1%/99% split of *this graduation's own* LT/TOKEN inventory [3](#0-2) , which is bounded by the curve's real raise, not by the attacker's pre-seed size. If an attacker pre-seeds the destination pair (via `pair.mint`) with reserves large enough relative to the graduation's `(tokensForLP, ltFromPair)` inventory, the capped rebalance cannot move the pool close enough to the target ratio, and the residual deposit computed by `_routerDepositAndDispose` (`addLiquidity(...,1,1,...)`) yields `liquidity = min(amountA*supply/reserveA, amountB*supply/reserveB) == 0` inside `pair.mint`, which reverts with `INSUFFICIENT_LIQUIDITY_MINTED`. Because the pool state, the cached `PendingGraduation` amounts, and the swap budget are all deterministic, every retry of `finalizeGraduation` hits the identical revert — permanently. Meanwhile Phase 1 (`_enterGraduating`) has already drained the curve, transferred the curve's real raised LT into `Bonding` via `Router.graduate`, and frozen trading [4](#0-3) , so that LT and up to `LP_RESERVE` (250M) tokens are permanently parked in `Bonding` with no rescue path — this is the exact "resource acquired, never released on the failing branch" pattern of CVE-2023-52838, mapped onto Solidity's two-phase, cross-transaction graduation design.

### Finding Description
Graduation is split into two transactions: `_enterGraduating` (phase 1) drains the curve, computes and caches `(tokensForLP, ltFromPair, lpBurned, unsoldBurned)` in `pendingGraduation[token]`, moves the real curve-raised LT into `Bonding` via `Router.graduate`, and flips the token to `Lifecycle.Graduating`, freezing trading [5](#0-4) . `finalizeGraduation` (phase 2), callable by anyone, is expected to always succeed ("Phase 2 must never revert under any pre-seed shape") [6](#0-5)  and ends by unconditionally calling `LPLock.recordLock`, which has no bypass [7](#0-6) .

The hostile mint-pre-seed defense (`_seedRebalancing`) rebalances via a direct `pair.swap`, capped at `_swapBudget` = 99% of `Bonding`'s *own* inventory of the swapped-in token — `_ltSwapInventory(lt, protectedLT)` or `IERC20(tokenAddress).balanceOf(address(this))` [8](#0-7) . This budget scales with the curve's own raise/inventory, not with the size of an attacker's pre-existing pool reserves. The comment on `_swapBudget` explicitly acknowledges the underlying risk was previously exploitable ("M-02") when the swap fully consumed one side, and claims the 1% reserve "guarantees the deposit leg always lands AND mints non-zero LP" [9](#0-8)  — but that guarantee only bounds `remToken`/`remLT` away from zero; it does **not** bound the *minted LP amount*, which is `min(amount*totalSupply/reserve)` against the pair's post-swap reserves [1](#0-0) . If the attacker's pre-seeded reserves are large enough relative to the graduation's capped inventory (achievable by repeatedly buying `TOKEN` on the curve and holding a real `LT` balance, then calling `pair.mint` directly), the swap — capped at 99% of a small curve-raise — cannot bring the ratio close enough, and the subsequent `_routerDepositAndDispose` → `addLiquidity` → `pair.mint` computes `liquidity == 0` for the deposited amounts against the now-massive reserves, reverting the entire `finalizeGraduation` transaction with `INSUFFICIENT_LIQUIDITY_MINTED`.

Because `PendingGraduation` is deleted only on success [10](#0-9) , the token remains in `Lifecycle.Graduating` and any retry recomputes the *identical* deterministic swap/deposit path against the *same* pool state, hitting the *same* revert forever. Trading was already frozen in phase 1 (`buy`/`sell` revert with `TokenIsGraduating` while `Lifecycle.Graduating`), and there is no admin/owner rescue function for `pendingGraduation` state or for LT/tokens sitting in `Bonding` mid-graduation. This is the "resource leak on error path" analog: phase 1 (the equivalent of `init_imstt`'s partial resource acquisition — `iounmap(par->cmap_regs)`'s counterpart) commits real assets (curve LT via `Router.graduate`, up to 250M `LP_RESERVE` tokens) to `Bonding`, and phase 2's failure path has no cleanup/rescue, permanently stranding them — exactly the missing-`iounmap`-on-failure shape of CVE-2023-52838, translated to Solidity's inability to partially commit and roll back across two independent transactions.

### Impact Explanation
A single unprivileged attacker can permanently freeze a token's entire curve-raised leveraged-token reserve (up to the graduation trigger, i.e. potentially all real value ever deposited by traders into that curve) plus up to 250M `LP_RESERVE` tokens, with no recovery path — matching the "permanent freezing of trader, creator, or LP funds" impact bar. The token can never graduate, its LP can never be locked, and the creator/traders who bought on the curve lose all access to the raised LT (it sits in `Bonding`, unreachable by any external function). This is a Medium/High-severity denial-of-funds vulnerability, not merely a griefing inconvenience, because the loss is irreversible absent a contract upgrade.

### Likelihood Explanation
Reachable by any unprivileged wallet with capital: the attacker needs (a) enough `TOKEN` bought from the curve (permissionless `Bonding.buy`/`Zap.buy`) and (b) a real `LT` balance, then calls `pair.mint` directly on the HyperSwap pair before/while the target token is `Graduating`. No special role, no timing dependent on validators or off-chain infra — only capital proportional to the size of the curve's own graduation-time inventory (which is comparatively small — a single graduation's `ltFromPair`/`tokensForLP`), making the required pre-seed size to overwhelm the 99%-capped rebalance/deposit modest for a determined griefer. The extensive existing fuzz coverage (`testFuzz_hostilePreSeed_neverProfitable_neverBricks`) exercises `seedMultiple` only up to 1000×, and the dedicated end-to-end hostile-pre-seed regression suite (`test/HostilePreSeed.t.sol`) was explicitly removed post-deployment for runtime reasons [11](#0-10) , so this larger-multiplier boundary is not currently regression-tested.

### Recommendation
Give `finalizeGraduation` a bounded-liquidity fallback: if the computed deposit would mint `liquidity == 0` (query `Pair`'s reserves/`totalSupply` before calling `addLiquidity`, or wrap the deposit call and, on revert, fall back to `_seedDirectMint`-style direct `pair.mint` at the cached ratio even against a non-empty pool), so a hostile pre-seed of any magnitude cannot deterministically brick the deposit. Alternatively, add an owner- or time-gated rescue path that can redirect `pendingGraduation`'s cached LT/token allocation to a fresh, protocol-controlled pair (or directly to a claimable escrow) if `finalizeGraduation` fails past a retry/backoff window, so a permanently-hostile-preseeded pair does not strand funds indefinitely.

### Proof of Concept
1. Attacker (or any address) buys `TOKEN` from the curve via `Zap.buy`/`Bonding.buy` up to just below the graduation trigger, accumulating a large `TOKEN` balance while holding a proportionally large `LT` balance.
2. A legitimate buy crosses the graduation trigger; `_enterGraduating` fires, draining the curve, moving `ltFromPair` LT into `Bonding` via `Router.graduate`, caching `(tokensForLP, ltFromPair, ...)` in `pendingGraduation[token]`, and freezing trading.
3. Before anyone calls `finalizeGraduation`, the attacker creates the HyperSwap `TOKEN`/`LT` pair (or reuses an existing one) and calls `pair.mint(attacker)` after transferring reserves many multiples larger than `(tokensForLP, ltFromPair)` at a skewed ratio.
4. Anyone calls `bonding.finalizeGraduation(token)`. `_seedRebalancing` computes a rebalance swap capped at 99% of `Bonding`'s own `ltFromPair`/`tokensForLP` inventory — negligible against the attacker's oversized reserves — leaving the pool far from the target ratio. `_routerDepositAndDispose`'s `addLiquidity` call then triggers `pair.mint`, which computes `liquidity = min(amount0*supply/reserve0, amount1*supply/reserve1) == 0` against the attacker's massive reserves and reverts with `INSUFFICIENT_LIQUIDITY_MINTED`.
5. Every subsequent call to `finalizeGraduation(token)` recomputes the identical deterministic values and reverts identically — the token is permanently stuck in `Lifecycle.Graduating`, and `ltFromPair` LT plus up to `LP_RESERVE` tokens remain unrecoverable in `Bonding`. [12](#0-11) [13](#0-12) [14](#0-13)

### Citations

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L56-65)
```text
        uint256 totalSupply_ = totalSupply();
        if (totalSupply_ == 0) {
            liquidity = _sqrt(amount0 * amount1) - MINIMUM_LIQUIDITY;
            _mint(DEAD, MINIMUM_LIQUIDITY);
        } else {
            uint256 liquidity0 = (amount0 * totalSupply_) / reserve0;
            uint256 liquidity1 = (amount1 * totalSupply_) / reserve1;
            liquidity = liquidity0 < liquidity1 ? liquidity0 : liquidity1;
        }
        require(liquidity > 0, "MockPair: INSUFFICIENT_LIQUIDITY_MINTED");
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

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
```text
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

**File:** packages/contracts/AGENTS.md (L86-86)
```markdown
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```

**File:** packages/contracts/AGENTS.md (L229-229)
```markdown
The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.
```
