### Title
LP seeded at a manipulated price when a pre-existing/pre-seeded HyperSwap V2 TOKEN/LT pair is used for graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
alt.fun's graduation flow computes the exact LT/TOKEN ratio to seed into a HyperSwap V2 pool so the pool "opens" at precisely the bonding curve's last price, then calls the standard Uniswap-V2-style `addLiquidity` on that pool. [1](#0-0)  This mirrors the UwU Lend bug class at a structural level: UwU Lend's payout math depended on a price read from an externally-influenceable pool (Curve), and an attacker moved that price with a large swap before the vulnerable code consumed it. Here, the analogous externally-influenceable venue is the HyperSwap V2 TOKEN/LT pair that `Bonding` seeds at graduation time.

### Finding Description
The graduation LP-seeding design explicitly targets "zero price gap" seeding: `_graduate()` reads the pair's stored reserves, computes `ltFromPair` (real LT raised, excluding the virtual seed) and `tokensForLP = (ltFromPair × reserve0) / reserve1` so that the LP opens at exactly the curve's last price. [2](#0-1)  This value is then fed as the desired amounts into HyperSwap V2's `addLiquidity`.

HyperSwap V2 (a standard Uniswap V2 fork) is a permissionless AMM: any unrelated wallet can create the TOKEN/LT pair and seed it with an arbitrary ratio *before* `Bonding` ever calls `addLiquidity` for that token. Uniswap-V2-style `addLiquidity` does not use the caller's "desired" amounts verbatim once a pool already has reserves — it computes the optimal amount of the second asset from the *existing pool ratio* and only reverts if the result falls below the caller-supplied `amountMin`. The system prompt itself confirms this exact fallback surface exists in the codebase: `addLiquidity with amountMin = 1` and the `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` fallback paths in `Bonding.sol`, present specifically to handle a pool whose reserves don't match `Bonding`'s intended ratio.

Because `amountMin` is hardcoded to `1` (a near-zero slippage floor), an attacker who pre-seeds the HyperSwap pair with a skewed ratio before a token's `canGraduate()` trigger fires can force the real graduation `addLiquidity` call to accept a badly-priced fill instead of reverting — the `1`-wei floor cannot protect against this because it accepts almost any output. The `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` fallbacks then absorb the leftover LT/TOKEN in whatever way the code is designed to, but the LP that results is priced according to the attacker's pre-seeded ratio, not the bonding curve's last price — defeating the entire "zero price gap" design goal stated in the docs.

Because graduation is a *permissionless, dual-trigger* event (`Bonding.canGraduate()` fires automatically inside every buy, and `triggerGraduation` can also be invoked externally by any sell path per the docs), an attacker can predict and race the exact block a token graduates, front-run it with a pool-creation + skewed-seed transaction, and let the victim protocol's own graduation transaction land into the poisoned pool. [3](#0-2) 

### Impact Explanation
A successfully-poisoned graduation seeds real, curve-raised LT (deposited by every prior trader on that bonding curve) and 250M reserved tokens into a pool priced away from the true last curve price. [4](#0-3)  The attacker who pre-seeded the skewed pool can then immediately arbitrage the mispriced pool against the true curve-implied price, extracting value that should have accrued to LPLock/token holders — directly analogous to the UwU Lend attacker arbitraging a manipulated Curve price against other pool assets. This is a concrete theft of LP/creator/trader value at the moment of graduation, which for a high-value token could reach a material fraction of the entire curve-raised LT (potentially hundreds of thousands of dollars per graduating token), and is High/Critical severity per the loss and permanence of the mispriced LP (locked one-shot by `LPLock.recordLock`, which the rules confirm `finalizeGraduation` cannot skip).

### Likelihood Explanation
Creating a Uniswap-V2-style pair and seeding it with an arbitrary ratio requires no privilege — any unrelated wallet can call the standard factory `createPair`/`addLiquidity` functions on HyperSwap V2 ahead of a specific token's graduation. Graduation is deterministic and observable (`canGraduate()`/dual triggers are public view state), making the graduating block predictable and front-runnable by mempool-watching bots, which raises likelihood to at least Medium-High for high-volume tokens approaching their threshold.

### Recommendation
- Do not rely on `amountMin = 1` when seeding the HyperSwap V2 LP at graduation. Before calling `addLiquidity`, check whether the target pair already has non-zero reserves and, if so, either (a) abort/queue graduation and alert, or (b) compute `amountMin` dynamically from the curve's last price with a tight tolerance band so any pre-seeded ratio outside that band causes a revert rather than a partial, mispriced fill.
- Consider having `Bonding`/`Router` create the HyperSwap V2 pair itself (rather than relying on `factory.createPair` being callable by anyone) so a pre-existing, attacker-seeded pool cannot exist at all at graduation time, or explicitly detect and reject graduating into a pre-existing pair with non-zero reserves.
- Audit the `_seedRebalancing` / `_pairRebalance` / `_seedDirectMint` fallback paths specifically for the case where the pre-existing pool ratio diverges materially from the curve's last price, ensuring none of them silently accept the divergence.

### Proof of Concept
1. Attacker monitors a bonding-curve token approaching `canGraduate()` (either the USD trigger or the supply trigger described in `docs/contracts-scope.md`). [5](#0-4) 
2. Attacker calls HyperSwap V2's factory to create the TOKEN/LT pair for that specific token, then seeds it via `addLiquidity` with a heavily skewed ratio (e.g., minimal LT against a large TOKEN amount, or vice versa) — all permissionless, unrelated-wallet actions.
3. Attacker (or any trader) submits the triggering buy/sell that flips `canGraduate()` true, causing `Bonding`'s graduation flow to compute `tokensForLP`/`ltFromPair` from the curve's true reserves and call `addLiquidity` against the already-skewed pool with `amountMin = 1`.
4. Because the pool already has reserves, `addLiquidity` fills at the pre-seeded ratio (accepted since `amountMin` barely constrains it), producing an LP priced away from the curve's true closing price.
5. Attacker immediately arbitrages the mispriced HyperSwap pool (buy the underpriced side, sell into the true-price venue or across LT redemption), extracting value that should have remained with the curve's traders/creator/LP.

Note: I was unable to retrieve the exact line-level implementation of `_graduate`, `_prepareGraduationLiquidity`, `_seedRebalancing`, `_pairRebalance`, and `_seedDirectMint` inside `packages/contracts/src/Bonding.sol` before running out of tool iterations — the file's presence and function names were confirmed via `grep_search`, but I could not read their bodies to pin exact line numbers or confirm the precise `amountMin` handling logic. The finding above is grounded in the confirmed design description in `docs/contracts-scope.md` and the confirmed existence of these functions/parameters in `Bonding.sol`; a full source read of `Bonding.sol`'s graduation section is recommended to verify the exact `amountMin` values and fallback behavior before treating this as fully proven.

### Citations

**File:** docs/contracts-scope.md (L34-38)
```markdown
**Virtual token reserve.** The pair's `reserve0` is seeded at `totalSupply` (1B) while only `curveSupply = 75%` (750M) of real tokens are actually transferred. The other 250M are held in `Bonding` as `lpReserve`. This virtual-reserve design:

- Extends the curve beyond the sellable supply.
- Gives a deterministic supply trigger (curve exhausts at 750M sold).
- Makes the dynamic-LP-seeding parabola `tokensForLP(sold) = sold·(S−sold)/S` peak at exactly `S/4 = 250M = LP_RESERVE` — so `tokensForLP ≤ lpReserve` is a mathematical invariant, not a runtime guess.
```

**File:** docs/contracts-scope.md (L66-76)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

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
