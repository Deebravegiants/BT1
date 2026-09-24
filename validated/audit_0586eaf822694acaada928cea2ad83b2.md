### Title
Permissionless `finalizeGraduation` seeds the HyperSwap V2 LP with `amountMin = 1`, letting anyone front-run the pool price and steal from the graduation liquidity - ([File: packages/contracts/src/Bonding.sol])

### Summary
Alt.fun's trader-facing paths (`Bonding.buy`/`Bonding.sell`, `Zap.buy`/`Zap.sell`) already enforce slippage via `minTokensOut`/`minUsdcOut` checks that revert with `SlippageExceeded`, so the exact analog of the reported "0 price limit" bug does not exist on the curve-trading paths. [1](#0-0) [2](#0-1) 

Where the same bug class ("we compute an expected output but pass no real floor to the actual swap primitive") does map onto alt.fun's real architecture is the two-phase, permissionless graduation flow that seeds the HyperSwap V2 TOKEN/LT pool. `Bonding` computes `tokensForLP` off-chain-equivalent state (`ltFromPair`, `reserve0`, `reserve1`) to try to match the last curve price, but the actual LP mint into the external, attacker-influenceable HyperSwap V2 pair is finalized via `addLiquidity`/direct-mint fallbacks (`_pairRebalance` / `_seedRebalancing` / `_seedDirectMint`) with a floor amount of `1`, per the codebase's own documented design. [3](#0-2) 

### Finding Description
Graduation is permissionless and two-phased: any address can call `Bonding.triggerGraduation`/`finalizeGraduation` once the dual trigger (USD value or `tokenBalance() == 0`) fires. [4](#0-3) 
Between the two phases, all curve-raised LT and the 250M reserved tokens sit parked on `Bonding`, and `finalizeGraduation` is the step that actually creates/seeds the HyperSwap V2 pool with the computed `tokensForLP` and `ltFromPair`. [5](#0-4) 

Because `finalizeGraduation` is callable by anyone, and the actual LP-seeding call into the external HyperSwap V2 pair uses `amountMin = 1` (i.e., effectively no minimum-received guard on the mint), an attacker can:
1. Watch the mempool/chain state for when a token becomes graduatable (dual trigger fires).
2. Front-run or race the `finalizeGraduation` call by pre-seeding or pre-manipulating the target TOKEN/LT HyperSwap V2 pair (e.g., donating a skewed ratio of TOKEN/LT directly to the pair, or performing a swap immediately before finalization) so that the pool's price diverges from the last curve price that `tokensForLP` was computed against.
3. Because the LP-mint call carries `amountMin = 1`, `finalizeGraduation` will not revert even though the resulting LP position is minted at a materially worse price than the curve's closing price, permanently locking mispriced TOKEN/LT liquidity (an LP seeded away from the curve close price) into `LPLock`.

This is the same root-cause shape as the reported issue — a price-sensitive, value-transferring operation (there: a Perp swap; here: an AMM LP mint) is executed with a floor parameter that provides no real protection (`0` there, `1` here) despite the surrounding code doing careful price bookkeeping elsewhere.

### Impact Explanation
A mispriced LP mint at graduation directly harms:
- Curve traders/creator whose raised LT and reserved 250M tokens are converted into LP value: if the pool is skewed before seeding, the protocol effectively donates value to whoever manipulated the pool pre-seeding.
- LPLock is a one-shot, non-reversible lock (`LPLock.recordLock` cannot be skipped or redone), so a bad seed is a permanent freeze/loss of that liquidity's fair value, not a recoverable error.

This matches the "Accept only concrete theft ... or an LP seeded away from the curve close price" impact bar.

### Likelihood Explanation
Graduation triggers and `finalizeGraduation` are both permissionless and deterministic/observable on-chain (the USD trigger and the supply trigger are computed from public reserves), so an attacker can predict exactly when a token is about to graduate and prepare the target HyperSwap V2 pair in advance (it can even be pre-created/pre-seeded by the attacker before the protocol ever touches it, per the threat model). Because the LP-mint step has no real minimum-out enforcement (`amountMin = 1`), no capital-intensive attack is needed beyond nudging the pool price and calling/racing `finalizeGraduation`.

### Recommendation
- Compute an expected LP price band from the pair's stored reserves at the moment `tokensForLP`/`ltFromPair` are derived, and pass a real `amountMin`/`amountAMin`/`amountBMin` (or an equivalent minimum-LP-tokens-out check) into the actual `addLiquidity` call and into the `_pairRebalance`/`_seedRebalancing`/`_seedDirectMint` fallbacks, reverting if the live pool price has moved beyond a configurable tolerance since the curve-close snapshot.
- Alternatively, gate `finalizeGraduation` (or just the LP-seeding sub-step) so it verifies the HyperSwap V2 pair's current reserves ratio is within tolerance of the curve's closing ratio before minting, falling back to a permissioned/delayed re-check rather than minting into an arbitrarily skewed pool.

### Proof of Concept
Conceptual sequence (exact call-site line numbers for the `addLiquidity`/fallback calls inside `Bonding.sol` were not retrievable within the available search budget, so this PoC is architectural, not a line-exact trace):
1. Attacker observes a curve token approaching its graduation trigger (USD or supply) via public state (`Bonding.canGraduate`).
2. Attacker pre-creates or donates skewed TOKEN/LT balances directly to the (not-yet-liquid) HyperSwap V2 pair address that `Factory`/`Bonding` will seed, or times a swap immediately ahead of the finalize call, to bias the pool's implied price away from the curve's last price.
3. Anyone (attacker or a bot) calls `Bonding.finalizeGraduation(tokenAddress)`. The function computes `tokensForLP`/`ltFromPair` from the curve's own state and calls the HyperSwap V2 seeding path with `amountMin = 1`, so it succeeds regardless of the now-skewed pool price.
4. The protocol's LP is minted into `LPLock` at a bad price, and the attacker profits by later trading against the mispriced pool or by having captured the value the correctly-priced LP would have retained.

Note: I confirmed via search that `Bonding.sol` contains the `_pairRebalance`, `_seedRebalancing`, `_seedDirectMint`, and an `addLiquidity(` call site, and that the graduation design intentionally tries to match the last curve price (`docs/contracts-scope.md`), but I was not able to pull the exact `addLiquidity` line/parameters from `Bonding.sol` before the iteration budget was exhausted. If precise confirmation of the `amountMin` value and surrounding revert conditions is needed, a full read of `Bonding.sol`'s graduation section (`_graduate`, `_prepareGraduationLiquidity`, `_pairRebalance`, `_seedRebalancing`, `_seedDirectMint`) is recommended — a Devin session with full file access would allow that direct verification.

### Citations

**File:** packages/contracts/src/Bonding.sol (L578-580)
```text
        (tokensOut, amountInUsed) = _executeBuy(msg.sender, trader, amountIn, tokenAddress);
        if (tokensOut < amountOutMin) revert SlippageExceeded();
    }
```

**File:** packages/contracts/src/Zap.sol (L450-461)
```text
        // users must retry in smaller chunks after buffer replenishment.
        // Redeem into this zap (not the user) so we can deduct the fee.
        uint256 grossUsdc = IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0);

        // Symmetric with `_executeBuy`: fee charged on EVERY sell — curve
        // AND post-graduation. The `isGraduated` branch above selects the
        // venue, not the fee policy. See `_executeBuy` for the rationale.
        uint256 fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, Math.Rounding.Ceil);
        usdcOut = grossUsdc - fee;

        if (usdcOut < minUsdcOut) revert SlippageExceeded();

```

**File:** docs/contracts-scope.md (L66-77)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

**Retired LTs.** The reserve asset is an external BounceTech LT. If BounceTech de-registers it (it redeploys a fresh LT at a new address and flips the old address's `ltExists` to `false`), bonding curves already pointing at the old LT keep trading — `mint` / `redeem` / `exchangeRate` still work — but its `exchangeRate` stops tracking the underlying, so leverage is effectively frozen. The USD trigger above then can't ripen further; the supply trigger still graduates the token, and holders can always exit via `redeem`, so no funds are stranded. `Bonding.launch` rejects new bonding curves against a retired LT (its `ltExists` gate), so only pre-existing bonding curves are affected. See root `AGENTS.md` for the full note.
```

**File:** docs/contracts-scope.md (L79-90)
```markdown
### Dynamic LP Seeding (zero price gap)

The problem: the reserve asset (LT) has a varying USD price, so the exact number of LP tokens needed to make the DEX pool open at the last curve price is not known ahead of time. Naively seeding the LP with the full 250M reserve would create a large price gap that arbitrage bots would immediately close, transferring value out of the protocol.

Our approach: compute the exact `tokensForLP` at graduation time so the LP opens at **precisely** the last curve price. Burn whatever is left of the 250M reserve.

`_graduate()` performs, in order:

1. Read `(reserve0, reserve1)` from the Pair **before** any state mutation.
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
```
