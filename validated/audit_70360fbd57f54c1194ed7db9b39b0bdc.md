### Title
`_seedDirectMint` fallback inside `_seedRebalancing` reuses first-mint semantics on a non-empty HyperSwap pair, letting an attacker capture graduation LP and skew the open price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` seeds the HyperSwap V2 TOKEN/LT pair via `_seedUniswapV2Direct` → `_seedRebalancing`, which is only entered when the pair's `totalSupply() != 0` (i.e., an attacker already minted LP against a hostile pre-seed) [1](#0-0) . Inside `_seedRebalancing`, three fallback branches — the "below-band-on-both-sides" short-circuit and both `_pairRebalance`-failure branches — call `_seedDirectMint` while `totalSupply() > 0` [2](#0-1) . `_seedDirectMint` unconditionally transfers the full cached `(tokensForLP, ltFromPair)` to the pair and calls `pair.mint(lpLock)` without checking `totalSupply()` first [3](#0-2) . Standard UniswapV2 `mint` only uses the "first liquidity" `sqrt(amount0*amount1)` formula when `totalSupply == 0`; once `totalSupply > 0` it uses `liquidity = min(amount0*totalSupply/reserve0, amount1*totalSupply/reserve1)`, pricing the deposit against the *attacker's own pre-seeded reserves* and donating the imbalanced side pro-rata to the attacker's existing LP — precisely the exploit the surrounding rebalance/`_pairRebalance` machinery exists to prevent, as the file's own natspec documents [4](#0-3) .

### Finding Description
`finalizeGraduation` is permissionless and callable by anyone once a token is `Lifecycle.Graduating` [5](#0-4) . It calls `_ensureUniswapV2Pair` (which itself permissionlessly calls `factory.createPair` if the pair doesn't exist) and then `_seedUniswapV2Direct` [6](#0-5) .

`_seedUniswapV2Direct` branches on `IUniswapV2Pair(pair).totalSupply()`:
- `== 0` → `_seedDirectMint` (correct: V2's first-mint formula makes the deposited amounts the sole price input).
- `!= 0` → `_seedRebalancing`, the hostile-mint-preseed defense.

`_seedRebalancing`, however, contains three paths that fall back to the *same* `_seedDirectMint` helper while `totalSupply() != 0` is guaranteed to hold (since that's the only way to reach this function):
1. Both reserve sides are below `DIRECT_MINT_PRESEED_BPS` relative to `(tokensForLP, ltFromPair)` [7](#0-6) .
2. `_pairRebalance` returns `false` on the TOKEN-rich branch [8](#0-7) .
3. `_pairRebalance` returns `false` on the LT-rich branch [9](#0-8) .

`_pairRebalance` returns `false` whenever the no-fee swap input rounds to zero or the pair's fee-charging `getAmountOut` rounds to zero [10](#0-9)  — both conditions an attacker can deliberately engineer by choosing a small, precisely-ratioed pre-seed.

`_seedDirectMint` does not check `totalSupply()` before calling `pair.mint(lpLock)`; it always transfers the full `(tokensForLP, ltFromPair)` and mints against whatever reserves currently exist [3](#0-2) . When `totalSupply() > 0` (guaranteed in these fallback call sites), a standard UniswapV2 pair computes `liquidity = min(amount0 * totalSupply / reserve0, amount1 * totalSupply / reserve1)` — i.e., it prices the deposit against the attacker's own pre-existing reserve ratio, not the curve's last price. Whichever side of the `(tokensForLP, ltFromPair)` deposit is "excess" relative to that ratio is effectively donated pro-rata to all existing LP holders — which is entirely the attacker, since they minted the only pre-existing LP.

This directly contradicts the two properties `_seedRebalancing` is supposed to guarantee (per its own natspec): that the LP opens at the curve-close price and that no side is donated to a pre-existing LP position [4](#0-3) . The fallback silently reintroduces the exact "wrong opening price" / "LP capture" attack described for the naive `pair.mint(lpLock)` call against a hostile pre-seed.

### Impact Explanation
- **LP seeded away from the curve close price**: the graduated pool opens at the attacker's chosen ratio rather than the curve's last marginal price, breaking Invariant #1 ("Zero price gap") tracked by `test/GraduationInvariants.t.sol` [11](#0-10) .
- **Theft of curve-raised LT / protocol tokens**: the "excess" side of the `(tokensForLP, ltFromPair)` deposit — real LT raised from traders and/or protocol-reserved tokens — is donated pro-rata to the attacker's own pre-existing LP position, which the attacker can withdraw for profit.
- Since `finalizeGraduation` is permissionless and `factory.createPair` is permissionless, an unprivileged attacker who observes a `TokenGraduating` event can front-run the keeper's `finalizeGraduation` call to set up the hostile pre-seed within the phase-1→phase-2 window.

### Likelihood Explanation
The window between phase 1 (`_enterGraduating`, fired inline on the threshold-crossing buy) and phase 2 (`finalizeGraduation`) is public via the `TokenGraduating` event, and the keeper Worker only drives finalize "within ~60s" — a public, permissionless race an attacker can win with a single bot watching for the event [12](#0-11) . Constructing a pre-seed that lands in the "both sides below `DIRECT_MINT_PRESEED_BPS`" band, or that makes `_pairRebalance`'s fee-charging quote round to zero, is a matter of picking a sufficiently small/precise `(token, LT)` transfer ratio before calling `pair.mint(attacker)` — well within reach of a single unprivileged address at low cost.

### Recommendation
`_seedDirectMint` must not be used as a fallback once `totalSupply() > 0`. Either:
- Add an explicit `require(IUniswapV2Pair(pair).totalSupply() == 0)` guard inside `_seedDirectMint`, or
- Replace the fallback paths in `_seedRebalancing` with a router-mediated `addLiquidity(..., amountAMin, amountBMin, ...)` deposit sized to the *current* post-attempted-rebalance ratio (the same pattern already used by `_routerDepositAndDispose`), so any residual imbalance is absorbed rather than donated via `pair.mint`'s proportional formula.

### Proof of Concept
1. Wait for (or trigger) `TokenGraduating` on a token `T` paired with LT `L` (phase 1 fired, `Lifecycle.Graduating`).
2. Before the keeper's `finalizeGraduation(T)` lands, call `hyperswapFactory.createPair(T, L)` (permissionless), then transfer a small, precisely-sized `(tokenAmt, ltAmt)` to the new pair and call `pair.mint(attacker)` — sized so that both `tokenAmt` and `ltAmt` fall under `DIRECT_MINT_PRESEED_BPS` relative to the known `tokensForLP`/`ltFromPair` cached by the `TokenGraduating` event (or so the resulting `_pairRebalance` quote rounds to zero).
3. Call/await `Bonding.finalizeGraduation(T)`. Trace shows `_seedUniswapV2Direct` → `_seedRebalancing` → fallback → `_seedDirectMint`, which transfers the full `(tokensForLP, ltFromPair)` into the pair and calls `pair.mint(lpLock)` while `totalSupply() > 0`.
4. Compute LP minted via V2's `min(amount0*totalSupply/reserve0, amount1*totalSupply/reserve1)`: verify the pool opens off the curve-close ratio and that the attacker's LP share (minted in step 2) now claims a pro-rata portion of the deposited `tokensForLP`/`ltFromPair` that exceeds their own contribution — confirmable by comparing the attacker's `pair.balanceOf(attacker)` share of `pair.totalSupply()` against the value of their original dust deposit versus the protocol's `(tokensForLP, ltFromPair)` deposit.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1023)
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

**File:** packages/contracts/src/Bonding.sol (L1155-1176)
```text
    ///        3. **Mint pre-seed.** Attacker called `pair.mint` against a
    ///           self-funded seed, baking a hostile (TOKEN, LT) ratio into
    ///           the pool. Without intervention `pair.mint(lpLock)`'s
    ///           `min(amount0·S/r0, amount1·S/r1)` formula would (a) open
    ///           the LP off curve-close-price and (b) donate the larger arm
    ///           to the attacker's pre-existing LP. We rebalance via a
    ///           direct `pair.swap` toward the curve-close ratio, then
    ///           deposit the remaining inventory via the router's
    ///           `quote()`-based `addLiquidity` — which only pulls the
    ///           optimal amounts at the post-swap ratio, so neither side
    ///           becomes a `min()` donation. Off-ratio TOKEN remainder is
    ///           burned; off-ratio LT remainder is auto-swept to the owner
    ///           by `finalizeGraduation`'s post-bookend (see its natspec).
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
```

**File:** packages/contracts/src/Bonding.sol (L1224-1234)
```text
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1245-1259)
```text
    function _seedDirectMint(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair
    ) internal returns (uint256 liquidity) {
        IERC20(tokenAddress).safeTransfer(pair, tokensForLP);
        IERC20(lt).safeTransfer(pair, ltFromPair);
        liquidity = IUniswapV2Pair(pair).mint(_s().lpLock);
        uint256 leftoverToken = IERC20(tokenAddress).balanceOf(address(this));
        if (leftoverToken > 0) {
            Token(tokenAddress).burn(address(this), leftoverToken);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1291-1348)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1414-1423)
```text
    function _pairRebalance(
        RebalanceParams memory p
    ) internal returns (bool) {
        uint256 s = _noFeeSwapInput(p.reserveIn, p.reserveOut, p.targetN, p.targetD, p.maxSwap);
        if (s == 0) return false;

        // Quote from the pair so the output tracks its live fee; a value
        // derived from a stale fee rate would trip the pair's K-check.
        uint256 expectedOut = IUniswapV2Pair(p.pair).getAmountOut(s, p.tokenIn);
        if (expectedOut == 0) return false;
```

**File:** docs/contracts-scope.md (L98-102)
```markdown
| # | Invariant | Mechanism |
|---|---|---|
| 1 | Zero price gap | `ltFromPair × reserve0End ≈ tokensInLP × reserve1End` within 1 bps |
| 2 | Conservation | `tokensInLP + lpBurned == LP_RESERVE` (250M) |
| 3 | Parabola cap | `tokensInLP ≤ LP_RESERVE` always (guaranteed by virtual reserve setup) |
```

**File:** packages/contracts/AGENTS.md (L83-94)
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
