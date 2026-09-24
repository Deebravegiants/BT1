### Title
Permanent freeze of curve-raised funds if HyperSwap V2 LP-seeding or LPLock hooks break during graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
The external report's core bug class is: closing a position depends on a call into an external contract, and if that external hook reverts, the user's principal is trapped with no fallback exit. alt.fun's analog is the permissionless two-phase graduation flow: once phase 1 (`_enterGraduating`) fires, all curve-raised LT and 250M reserved tokens are parked on `Bonding`, and phase 2 (`finalizeGraduation`) is the only path that can move them out. `finalizeGraduation` depends on external calls to HyperSwap V2's `addLiquidity` and to `LPLock.recordLock`. If either external call reverts (bad pool state, malicious/broken HyperSwap pair, `LPLock` already-locked guard, etc.), `finalizeGraduation` reverts every time it's called, and because `Zap.sell`/`Bonding.sell` refuse to execute while a token `isGraduating` (`TokenIsGraduating` revert), traders lose the ability to exit their positions and the parked LT/tokens are frozen indefinitely with no emergency-exit path.

### Finding Description
Graduation happens in two phases [1](#0-0) :
- Phase 1, `_enterGraduating`, fires inline at the end of the threshold-crossing buy and flips the token's lifecycle to `Graduating`, parking the curve-raised LT and the 250M `lpReserve` tokens on `Bonding` [2](#0-1) .
- Phase 2, `finalizeGraduation` (via `_graduate`), reads the pair reserves, burns unsold tokens, recovers the virtual LT reserve, drains the real LT via `Router.graduate`, computes `tokensForLP`, and then calls `addLiquidity(tokensForLP, ltFromPair)` on HyperSwap V2, sending the resulting LP tokens to `LPLock` [3](#0-2) .

While a token is `Graduating`, `Zap.sell` explicitly blocks trading: `if (bonding_.isGraduating(tokenAddress)) revert TokenIsGraduating();` [4](#0-3) . This means the only way out for a holder is for `finalizeGraduation` to succeed and flip the lifecycle to `Graduated`, at which point trading resumes on the HyperSwap pool.

`finalizeGraduation`'s `addLiquidity` call and `LPLock.recordLock` call are both external-contract hooks exactly analogous to the `AlgebraPool` hook in the reference report: they are calls into another contract whose failure is not handled by any fallback path in `Bonding`. If HyperSwap V2's `addLiquidity` reverts (e.g., due to a manipulated/attacker-influenced pair state, a `K`-invariant issue from a pre-seeded or pre-funded pool, or the router rejecting the computed `tokensForLP`/`ltFromPair` pair because of `amountMin` slippage checks) or if `LPLock.recordLock` reverts because it is a one-shot call that `finalizeGraduation` cannot skip and something about its state (e.g., already-locked guard, or an unexpected revert condition) is violated, then every subsequent call to `finalizeGraduation` for that token reverts identically. There is no owner/emergency function in `Bonding` that lets holders redeem their tokens for the parked LT while the token is stuck in `Graduating`, nor a way to retry graduation with different parameters or skip the broken hook.

### Impact Explanation
If `finalizeGraduation` becomes permanently unreachable for a token, every unit of LT raised on the curve for that token (up to the graduation threshold, i.e. up to `$9K` equivalent per the documented threshold) plus the 250M reserved tokens are permanently frozen on `Bonding`. Holders can neither sell on the curve (`TokenIsGraduating` blocks it) nor trade on HyperSwap (graduation never completes, so no pool exists). This is a permanent freezing of trader and creator funds — the exact impact class the external report warns about, mapped onto alt.fun's own two-phase graduation and LP-seeding mechanism.

### Likelihood Explanation
Reaching phase 1 (`_enterGraduating`) is fully permissionless: any unrelated trader can push a token's curve past the graduation threshold via ordinary `Zap.buy` calls, or LT appreciation can ripen the USD trigger with the next buy settling it, as documented in `Bonding.canGraduate` [5](#0-4) . Triggering `finalizeGraduation` itself is also permissionless (it's callable by anyone once `Graduating`). The precondition for the freeze is that the external HyperSwap V2 `addLiquidity` call or the `LPLock.recordLock` call reverts deterministically for that token's specific state — this could result from an attacker pre-seeding/pre-funding the target HyperSwap V2 TOKEN/LT pair before graduation (explicitly listed as a reachable path in scope) so that the computed `tokensForLP`/`ltFromPair` fails the pool's internal invariant or `amountMin` checks every time. This makes the trigger condition attacker-controllable rather than merely accidental, raising likelihood above a purely hypothetical external-dependency failure.

### Recommendation
Add a permissionless emergency-exit path for tokens stuck in `Graduating`: if `finalizeGraduation` has failed or has not succeeded within a bounded window/number of attempts, allow holders to redeem their curve tokens directly against the LT parked on `Bonding` (mirroring the curve's own bonding-curve pricing) without requiring the HyperSwap `addLiquidity` / `LPLock.recordLock` calls to succeed. Alternatively, decouple the LT/token draining from the LP-seeding step so that failure of the external DEX/lock call does not block fund recovery, and add a fallback LP-seeding mechanism (as hinted by `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` naming in the reachable-paths list) that degrades gracefully instead of reverting the whole finalize call.

### Proof of Concept
1. An unrelated wallet pre-seeds/pre-funds the HyperSwap V2 TOKEN/LT pair for a not-yet-graduated token before graduation occurs, skewing its reserves so that a later `addLiquidity(tokensForLP, ltFromPair)` call computed by `_graduate()` will violate the pool's proportional-deposit checks (or push `amountMin`-style checks to fail) for the exact `tokensForLP`/`ltFromPair` values `Bonding` will later compute.
2. A separate unrelated trader executes ordinary `Zap.buy` calls that cross the graduation threshold, firing `_enterGraduating` and parking the curve-raised LT and 250M reserved tokens on `Bonding`, with the token lifecycle now `Graduating`.
3. Anyone calls `finalizeGraduation` (or it is attempted automatically) — `_graduate()` reaches the `addLiquidity` call against the pre-skewed pair and reverts.
4. Every retry of `finalizeGraduation` reverts identically since the pool state and computed amounts are deterministic from stored reserves.
5. All holders of the token are now blocked from selling (`Zap.sell` reverts with `TokenIsGraduating`) and the curve-raised LT plus 250M tokens remain locked on `Bonding` indefinitely, with no available function to recover them.

### Citations

**File:** docs/contracts-scope.md (L66-93)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

**Retired LTs.** The reserve asset is an external BounceTech LT. If BounceTech de-registers it (it redeploys a fresh LT at a new address and flips the old address's `ltExists` to `false`), bonding curves already pointing at the old LT keep trading — `mint` / `redeem` / `exchangeRate` still work — but its `exchangeRate` stops tracking the underlying, so leverage is effectively frozen. The USD trigger above then can't ripen further; the supply trigger still graduates the token, and holders can always exit via `redeem`, so no funds are stranded. `Bonding.launch` rejects new bonding curves against a retired LT (its `ltExists` gate), so only pre-existing bonding curves are affected. See root `AGENTS.md` for the full note.

### Dynamic LP Seeding (zero price gap)

The problem: the reserve asset (LT) has a varying USD price, so the exact number of LP tokens needed to make the DEX pool open at the last curve price is not known ahead of time. Naively seeding the LP with the full 250M reserve would create a large price gap that arbitrage bots would immediately close, transferring value out of the protocol.

Our approach: compute the exact `tokensForLP` at graduation time so the LP opens at **precisely** the last curve price. Burn whatever is left of the 250M reserve.

`_graduate()` performs, in order:

1. Read `(reserve0, reserve1)` from the Pair **before** any state mutation.
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
5. Burn `lpReserveTotal − tokensForLP` from `Bonding`'s held reserve (`lpBurned`).
6. `addLiquidity(tokensForLP, ltFromPair)` on HyperSwap V2 → LP tokens go to `LPLock`.

```

**File:** packages/contracts/src/Zap.sol (L421-422)
```text
        if (bonding_.creatorOf(tokenAddress) == address(0)) revert TokenNotTrading();
        if (bonding_.isGraduating(tokenAddress)) revert TokenIsGraduating();
```

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
```
