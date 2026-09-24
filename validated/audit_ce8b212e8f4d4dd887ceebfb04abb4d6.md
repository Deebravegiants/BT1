## Finding [1](#0-0) 

The Holdefi report's core complaint — a permissionless "cleanup" function (`liquidateBorrowerCollateral`) that is expensive to call but pays the caller nothing, so nobody has an economic reason to call it — maps directly onto `Bonding.finalizeGraduation` in this codebase.

### Title
Permissionless `finalizeGraduation` (Phase 2) offers callers zero on-chain compensation for a ~2.5M-gas transaction, risking indefinite freeze of curve-raised LT and reserved tokens if the off-chain keeper stops calling it - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` is the mandatory, permissionless second half of the two-phase graduation flow. Once `_enterGraduating` fires (Phase 1), the token is frozen in `Lifecycle.Graduating` — all buys and sells revert with `TokenIsGraduating` — until someone calls `finalizeGraduation`, a big-block transaction the docs size at ~2.5M gas. [2](#0-1)  No reward, discount, fee rebate, or any other economic incentive is paid to whoever calls it — the function only moves protocol-owned LT and 250M reserved tokens into the HyperSwap LP and locks it. [3](#0-2)  The protocol's own docs state that in practice this gap is closed only by an off-chain Cloudflare Worker keeper, and that "anyone can call to rescue a stuck token" is the on-chain fallback. [4](#0-3) 

### Finding Description
This is structurally the same incentive gap as Holdefi's `liquidateBorrowerCollateral`: a permissionless state-transition function that is costly to execute and economically detached from any benefit to the caller.

- Phase 1 (`_enterGraduating`) drains the curve pair, computes and caches `tokensForLP`/`ltFromPair` in `pendingGraduation[token]`, and flips the token to `Lifecycle.Graduating`, which freezes `buy`/`sell` on the curve. [5](#0-4) 
- Phase 2 (`finalizeGraduation`) must run to completion (creating/seeding the HyperSwap pair, locking LP via `LPLock.recordLock`) before the token can trade again as `Lifecycle.Graduated`. [1](#0-0) 
- `finalizeGraduation` has `nonReentrant` but no fee/reward parameter, no gas-refund mechanism, and no discount analogous to Holdefi's proposed 5% liquidation-collateral incentive. The caller pays full gas for a large transaction (the docs cite a ~1.8M-gas phase-1 budget and ~2.5M for phase 2) and receives nothing in return. [6](#0-5) 
- The design explicitly relies on an off-chain keeper (a Cloudflare Worker) to make the happy path work; the on-chain permissionless path exists purely as a "rescue" fallback with no economic pull for a third party to use it. [4](#0-3) 

Exactly as in the Holdefi report, the absence of any positive incentive means that in the failure mode where the off-chain keeper is down, censored, mis-configured, or simply slow during a gas spike, no rational unprivileged address has a reason to spend ~2.5M gas to unstick someone else's graduation. Because `Lifecycle.Graduating` blocks all curve trading and parks the curve-raised LT plus the 250M reserved tokens on `Bonding` awaiting `finalizeGraduation`, [7](#0-6)  that state can persist indefinitely: token holders cannot buy or sell on the curve, and the curve-raised LT/reserved tokens sit unproductively in `Bonding` rather than being deployed to the LP, for as long as no one is economically motivated to pay the finalize gas.

### Impact Explanation
While `finalizeGraduation` is brick-resistant against hostile pre-seeds (it cannot revert), it can never execute at all unless someone submits the transaction. If the keeper infrastructure is unavailable and gas costs make it uneconomical for an altruistic third party to call `finalizeGraduation`, the token remains stuck in `Lifecycle.Graduating`:
- Traders holding the token cannot buy or sell on the curve (both revert with `TokenIsGraduating`).
- The curve-raised LT (`ltFromPair`) and the 250M `LP_RESERVE` tokens remain parked on `Bonding`, never deployed into the HyperSwap LP, i.e., effectively frozen liquidity for the token's community and creator.

This is a freeze-of-funds condition reachable purely by transaction-level economics (no privileged action, no upgrade, no off-chain compromise required to trigger the underlying gap — only for the keeper to be unavailable, which is a realistic operational condition, e.g. RPC outage, worker downtime, or a gas spike that makes the ~2.5M-gas call unprofitable for any volunteer).

### Likelihood Explanation
Medium. Under normal conditions the Cloudflare Worker keeper finalizes graduations within ~60 seconds, so the window is usually small. [8](#0-7)  But the keeper is a single off-chain component with no on-chain backstop incentive; any outage, bug, or targeted griefing of the keeper directly translates into an indefinite freeze because the on-chain fallback (permissionless call) has zero payoff to compensate a stranger's gas cost. The bigger the gas cost relative to the token's economic relevance (e.g., a small/abandoned token graduating during a gas spike), the less likely any unprivileged party bothers to call it.

### Recommendation
Introduce an on-chain incentive for whoever calls `finalizeGraduation` (and/or `triggerGraduation`), for example: pay the caller a small bounty in LT/USDC funded from the graduation's own `lpBurned`/`unsoldBurned` proceeds, or refund gas via a keeper-fee skimmed from the fee split in `FeeVault`. This removes the dependency on a single off-chain actor being economically rational to run indefinitely and prevents the parked LT/reserved-token freeze from persisting when the keeper is unavailable.

### Proof of Concept
1. A token crosses the graduation threshold; `Bonding._executeBuy` calls `_enterGraduating`, moving it to `Lifecycle.Graduating` and caching `pendingGraduation[token]`. [9](#0-8) 
2. Simulate keeper unavailability (e.g., Cloudflare Worker outage / high gas). No entity calls `finalizeGraduation`.
3. Any holder attempts `Bonding.buy`/`Bonding.sell` on the token and observes reverts with `TokenIsGraduating`, confirmed by existing tests `test_phase1_buy_during_pending_reverts` / `test_phase1_sell_during_pending_reverts`. [10](#0-9) 
4. Because `finalizeGraduation` pays the caller nothing (compare its body, which only moves protocol funds into the LP and lock, to any reward transfer to `msg.sender`), [1](#0-0)  no unprivileged third party has an on-chain economic reason to submit the ~2.5M-gas transaction, and the freeze persists until an altruistic caller (or the recovered keeper) eventually pays the cost.

### Citations

**File:** packages/contracts/src/Bonding.sol (L929-953)
```text
        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
    }

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

**File:** packages/contracts/AGENTS.md (L83-93)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
- **Virtual token reserve.** At launch, `Pair.reserve0 = totalSupply (1B)` while only `curveSupply = 75%` (750M) of real tokens are transferred to the pair. The other 250M (`LP_RESERVE`) sit in `Bonding` for graduation. This extends the curve beyond the sellable supply, which is what makes dynamic LP seeding work cleanly.
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
- **Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation.
- **Overflow buy cap.** `Router.buy` caps `tokensOut` at the pair's real balance and back-calculates the LT consumed, so the last buy cannot exceed remaining supply. `Zap.buy` returns the unused LT (`ltMinted - amountInUsed`) directly as LT — not redeemed, to avoid re-incurring the LT redemption fee on dust — while unconverted USDC and the fee over-charge are refunded in USDC. `Bonding.buy` returns `(tokensOut, amountInUsed)` for this reason.

**If you change `_enterGraduating`, `finalizeGraduation`, `_prepareGraduationLiquidity`, `_seedUniswapV2Direct` (or any of its `_seedRebalancing` / `_pairRebalance` / `_routerDepositAndDispose` / `_noFeeSwapInput` helpers), `Router.buy`'s capping logic, or the seeding in `_deployAndSeed`:** you MUST re-run `test/GraduationInvariants.t.sol`, `test/TwoPhaseGraduation.t.sol`, and `test/NoFeeSwapInput.t.sol`. All 7 zero-gap invariants must still pass; the phase-1-fits-in-small-block budget assertion (1.8M) must still hold; the brick-resistance regression test must still pass. These invariants are the product — do not loosen their assertions to make a change go green.
```

**File:** packages/contracts/AGENTS.md (L994-995)
```markdown

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
