### Title
Permissionless, front-runnable HyperSwap V2 pair pre-seeding can open the graduation LP at a manipulated price - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation` [1](#0-0)  is a **permissionless** phase-2 graduation entry point that creates (or reuses) the HyperSwap V2 TOKEN/LT pair via `_ensureUniswapV2Pair` and then seeds liquidity through `_seedUniswapV2Direct`, which branches into a hostile-pre-seed rebalance path (`_seedRebalancing` / `_pairRebalance` / `_seedDirectMint`) whenever the pair already holds attacker-supplied reserves. Any unprivileged address can pre-create and pre-seed that pair with an arbitrary token/LT ratio before the keeper's `finalizeGraduation` call lands, forcing the code down the rebalance branch and opening the locked LP at a price the attacker chose rather than the curve's true close price.

### Finding Description
Graduation is intentionally split into two transactions to fit HyperEVM's small-block gas ceiling: Phase 1 (`_enterGraduating`, inline on the threshold-crossing buy) freezes the curve and caches `tokensForLP` / `ltFromPair` at the last curve price [2](#0-1) . Phase 2 (`finalizeGraduation`) is permissionless by design — "anyone can call to rescue a stuck token" — and must "never revert under any pre-seed shape," per the project's own documentation [3](#0-2) .

Because `finalizeGraduation` is callable by anybody and the target HyperSwap V2 pair address is deterministic (create2 from the token/LT pair), an attacker can pre-create the pair and donate/imbalance its reserves before the keeper (or anyone else) calls `finalizeGraduation`. The maintainers' own documentation explicitly names this class of attack — "hostile mint pre-seeds" — and states that the brick-resistance design routes such cases through `_pairRebalance` / direct `pair.swap` plus router `addLiquidity` for "the canonical quote-based deposit" [4](#0-3) .

Critically, the AGENTS.md file also states that the dedicated regression suite that once proved this path was safe — `test/HostilePreSeed.t.sol`, covering "the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties" — **was removed for runtime reasons after deployment** and "are no longer enforced by automated tests" [5](#0-4) . This means the exact property that would rule out an attacker being able to open the LP at a skewed price via pre-seeding is documented as unverified in the current codebase, while the underlying permissionless, brick-proof `finalizeGraduation` path that reaches this code is unchanged and still live [6](#0-5) .

This is the direct structural analog of the Woodpecker advisory: an unprivileged actor supplies attacker-controlled state (there, env vars altering which plugin entrypoint executes; here, pre-seeded pair reserves altering which graduation code branch executes and at what price) ahead of a privileged/automated execution step (there, the CI agent running the workflow; here, the keeper/anyone calling `finalizeGraduation`), diverting the execution flow into a path that was not fully hardened/tested and that can produce value extraction (LP opened away from fair price) at the expense of the protocol and traders whose curve-raised LT and 250M reserved tokens are deposited into that LP.

### Impact Explanation
If `_seedRebalancing`/`_pairRebalance` does not perfectly restore the curve-close price ratio when reconciling an attacker's pre-seeded reserves, the graduation LP — funded by all of the curve's raised LT (`ltFromPair`) and the protocol's reserved 250M tokens (`tokensForLP`) — is permanently locked into `LPLock` at a wrong price [7](#0-6) . An attacker who seeded the skew can arbitrage the mispriced pool immediately after seeding (buying the underpriced side), extracting value that should have accrued to the curve's traders/creator and to the protocol-owned LP. Because `LPLock.recordLock` is one-shot and the LP cannot be unwound in v1, the loss is not recoverable after the fact. This satisfies the "LP seeded away from the curve close price" and "unbacked token/LT payout" impact criteria.

### Likelihood Explanation
The precondition (pre-creating/pre-seeding the HyperSwap V2 pair before `finalizeGraduation` executes) requires no privilege, only capital and the ability to observe `TokenGraduating` and front-run the ~60-second keeper window — exactly the scenario the codebase's own comments describe as the motivating threat for the (now test-unverified) rebalance logic. The removal of `test/HostilePreSeed.t.sol` means this exact attack surface currently has no automated regression coverage protecting the invariant that the rebalance path reopens at the correct price.

### Recommendation
Reinstate (or re-derive) the `HostilePreSeed.t.sol` coverage — specifically the wrong-opening-price / LP-capture, attacker-no-profit, and leftover-recovery properties — before relying on `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` in production. Consider adding an on-chain invariant check in `finalizeGraduation` that asserts the resulting LP price is within tolerance of the cached curve-close ratio (`tokensForLP` : `ltFromPair`) and reverts (or routes to a safe fallback) otherwise, rather than trusting the rebalance math unconditionally.

### Proof of Concept
1. Attacker observes `TokenGraduating(tokenAddress, tokensForLP, ltFromPair, ...)` emitted by `_enterGraduating` [8](#0-7) .
2. Before the keeper calls `finalizeGraduation`, attacker calls the HyperSwap V2 factory to `createPair(token, lt)` at the deterministic address and transfers a skewed ratio of `token`/`lt` directly into the pair (a plain ERC20 `transfer`, reachable by any unrelated wallet).
3. Attacker (or the keeper) calls `Bonding.finalizeGraduation(tokenAddress)`; `_ensureUniswapV2Pair` finds the pair already exists and non-empty, forcing `_seedUniswapV2Direct` into the hostile-pre-seed rebalance branch (`_seedRebalancing`/`_pairRebalance`) instead of the clean empty-pair path [4](#0-3) .
4. Absent the removed regression suite proving price-parity of this branch, the resulting LP may open away from the curve's close price; attacker immediately arbitrages the pool for profit at the expense of the locked LP value.

### Citations

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

**File:** packages/contracts/AGENTS.md (L79-90)
```markdown
## Graduation — Two-Phase, Dynamic LP Seeding (Read This Before Touching Graduation Code)

This is the most bespoke piece of the protocol. Full rationale + invariants live in [`docs/contracts-scope.md`](../../docs/contracts-scope.md#graduation); the short version:

- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
- **Virtual token reserve.** At launch, `Pair.reserve0 = totalSupply (1B)` while only `curveSupply = 75%` (750M) of real tokens are transferred to the pair. The other 250M (`LP_RESERVE`) sit in `Bonding` for graduation. This extends the curve beyond the sellable supply, which is what makes dynamic LP seeding work cleanly.
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
- **Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation.
```

**File:** packages/contracts/AGENTS.md (L223-229)
```markdown
### Tests you MUST re-run if you change any of this

- `test/NoFeeSwapInput.t.sol` — 9 deterministic + 2 fuzz tests on the load-bearing math (degenerate inputs, monotonicity, cap-at-budget, closed-form correctness, overflow safety, the round-down-to-zero input shape that motivated the precheck).
- `test/TwoPhaseGraduation.t.sol` — brick-resistance + phase-1-fits-in-small-block tests, plus the hostile-pre-seed open-at-cached-ratio tests (`test_hostilePreSeed_*`) covering both the dust direct-mint fallback and the meaningful-reserve swap path, must still pass.
- `test/GraduationInvariants.t.sol` — zero-gap, supply conservation, parabola cap. Honest-path properties unchanged by the defense.

The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.
```
