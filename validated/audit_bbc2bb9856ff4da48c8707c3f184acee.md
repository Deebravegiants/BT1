### Title
Graduation LP seeding can overflow HyperSwap V2's `uint112` reserve slot when the paired LT's `exchangeRate` depreciates after launch, permanently bricking graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
The external report flags `LeqGadget` for silently assuming every compared value fits inside a fixed bit-width (`NUM_BITS_FIELD_CAPACITY - 1 = 253`), so a legitimate value that grows past that width triggers an assertion failure/crash. alt.fun has the same class of bug: `Bonding._deployAndSeed` bounds the *launch-time* virtual LT reserve to `type(uint112).max / 4` on the assumption the LT's `exchangeRate` stays roughly where it was at launch, but nothing re-checks that bound against the *actual* raised-LT amount computed at graduation time, which is driven by the LT's live, volatile `exchangeRate`.

### Finding Description
At launch, `Bonding._deployAndSeed` computes the virtual LT reserve from the LT's current `exchangeRate()` and caps it defensively for the eventual HyperSwap V2 `uint112` reserve slot: [1](#0-0) 

```
uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
...
uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
// The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
// and is later deposited into a HyperSwap V2 pair, whose reserves are
// `uint112`. Bound it at launch (4x headroom) so graduation can never
// exceed that slot.
if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
```

The comment's "peaks at `3 * virtualLtReserve`" claim, and therefore the whole uint112-safety argument, implicitly assumes `exchangeRate` stays roughly constant between launch and graduation. But the paired asset is an external BounceTech leveraged token (LT) whose `exchangeRate()` is explicitly volatile and can move far from its launch-time value over the life of a curve that has no time limit: [2](#0-1) 

Graduation is triggered by a fixed **USD** threshold computed from the *current* exchange rate, not the launch-time one — the real LT amount needed to cross that threshold scales inversely with whatever `exchangeRate()` is at the moment of the triggering buy: [3](#0-2) 

If the LT depreciates after launch (a leveraged token can lose a large fraction of its value, especially over an extended, unbounded trading window), the LT quantity required to hit the same fixed-USD graduation trigger grows well beyond the `3 × virtualLtReserve` figure the launch-time uint112 bound was sized against. Nothing in `canGraduate`, `previewLtUntilGraduation`, or the graduation-liquidity preparation path re-validates that the *actual* `ltFromPair` / `tokensForLP` computed at graduation time still fits in `uint112` before they get deposited into the HyperSwap V2 pair, whose reserve slots are hard-typed `uint112`: [4](#0-3) 

The mock pair used in tests shows exactly what happens when a deposited amount doesn't fit: reserves are naively cast, i.e. either silently truncated/wrapped (corrupting the AMM's stored K permanently) or, on a real Uniswap V2 fork that uses `SafeCast`/explicit bounds-checking, the seeding call reverts outright: [5](#0-4) 

That seeding call sits inside the permissionless, non-skippable phase-2 of graduation: [6](#0-5) 

Phase 1 (`_enterGraduating`) has already drained the curve and parked the raised LT plus the 250M reserved tokens on `Bonding`, and there is no rollback path back to `Curve` lifecycle once `Graduating` is set. If phase 2's `pair.mint`/`addLiquidity` call reverts (or corrupts state) because the deposit amount exceeds `type(uint112).max`, the token is stuck in `Graduating` forever: trading stays frozen and the parked LT/tokens are unreachable, matching the report's "unrealistic bit-width assumption breaks silently and later crashes/DoSes the system" bug class.

### Impact Explanation
A stuck `Graduating` lifecycle permanently freezes: (a) all real LT raised by the bonding curve (trader funds), (b) the creator's 250M reserved token allocation held on `Bonding` for LP seeding, and (c) any further trading for that token, since `Bonding.buy`/`sell` reject once trading is frozen for graduation and `LPLock.recordLock` is one-shot and cannot be invoked outside `finalizeGraduation`'s happy path. This satisfies the "permanent freezing of trader, creator, or LP funds" bar the validation rules require, without any privileged action — it can be reached purely by normal, unprivileged buy transactions plus the natural price movement of an external leveraged asset.

### Likelihood Explanation
The launch-time bound only leaves ~25% headroom (`virtualLtReserve ≤ uint112.max/4`, and the assumed peak raised-LT is `3×` that, i.e. `0.75×uint112.max`). Any creator can permissionlessly launch a token paired with an LT whose `exchangeRate` sits close to that bound (nothing stops picking an LT near the allowed minimum rate). From there, only a moderate depreciation of that LT's `exchangeRate` before the curve graduates — plausible for a leveraged token, especially over the unbounded lifetime a slow-moving curve can have — is enough to push the graduation-time real-LT requirement past the remaining headroom and into `uint112` overflow territory. No attacker coordination, privileged role, or unusual gas/timing is required; it can be triggered by ordinary buy activity from any unrelated trader once the exchange-rate condition is met.

### Recommendation
- **Short term:** Re-check, at the point graduation is actually triggered (inside `canGraduate` / `_enterGraduating` / `_prepareGraduationLiquidity`), that the *live* `ltFromPair` and `tokensForLP` amounts about to be deposited into the HyperSwap V2 pair are `≤ type(uint112).max` (with headroom), and revert/defer gracefully (not park funds irreversibly) if they are not. Document that the launch-time `ExchangeRateTooLow` check is not sufficient protection against LT depreciation over the curve's lifetime.
- **Long term:** Review every place in `Bonding`/`Router` that assumes a value will stay inside a bounded numeric range (uint112 HyperSwap reserves, uint256 `Math.mulDiv` intermediate products noted elsewhere in `_noFeeSwapInput`, etc.) under the assumption that an external, volatile exchange rate stays close to its launch-time value, and add live bounds checks plus a safe-abort/rescue path instead of relying on launch-time-only guards.

### Proof of Concept
1. Creator calls `Zap.createToken` / `Bonding.launch` pairing the new token with a BounceTech LT whose `exchangeRate()` is set (or naturally sits) close to the point where `virtualLtReserve = VIRTUAL_LIQUIDITY_USD*1e18/exchangeRate` is just under `type(uint112).max/4` — this passes the `ExchangeRateTooLow` launch check (`packages/contracts/src/Bonding.sol:484`).
2. Over the life of the curve, ordinary unprivileged buyers call `Zap.buy` while the LT's `exchangeRate()` declines substantially (leveraged-token depreciation, no on-chain party needs to act maliciously — this is native BounceTech LT behavior).
3. Because the USD graduation trigger is fixed while `exchangeRate` has dropped, the real LT raised (`storedAssetReserve - virtualLtReserve`) needed to cross the threshold is now much larger, in wei terms, than the `3×virtualLtReserve` figure the launch-time uint112 bound assumed.
4. A subsequent buy crosses the USD threshold, firing `Bonding._enterGraduating` (phase 1): curve is drained, trading frozen, `pendingGraduation[token]` cached.
5. Anyone calls `Bonding.finalizeGraduation` (phase 2, permissionless): `_prepareGraduationLiquidity`/`_seedUniswapV2Direct` attempts to deposit `ltFromPair`/`tokensForLP` — now exceeding `type(uint112).max` — into the HyperSwap V2 pair via `pair.mint`/router `addLiquidity`. This either reverts (bricking `finalizeGraduation` permanently, since phase 1 cannot be undone) or truncates the stored `uint112` reserves, corrupting the graduated pool's price and permanently locking the discrepancy in `LPLock`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-494)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();

        IERC20(tokenAddr).forceApprove(address($.router), curveSupply);
        // Virtual tokenReserve = full totalSupply; only curveSupply (75%) actually transferred.
        // The launch-time `virtualLtReserve` is recoverable later as
        // `Pair.k() / Token.TOTAL_SUPPLY()`: `Pair.mint` sets `_pool.k =
        // tokenReserve * assetReserve = totalSupply * virtualLtReserve` once
        // and `Pair.swap` never modifies `_pool.k`. That identity is what
        // `_launchTimeVirtualLtReserve` exploits to derive donation-immune
        // raised-LT in `canGraduate` and `_prepareGraduationLiquidity`.
        $.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L26-30)
```text
    function baseAssetBalance() external view returns (uint256);

    /// @notice USDC per LT unit, 18-dp.
    function exchangeRate() external view returns (uint256);

```

**File:** docs/contracts-scope.md (L68-71)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```

**File:** packages/contracts/src/interfaces/IUniswapV2Pair.sol (L11-14)
```text
interface IUniswapV2Pair {
    function token0() external view returns (address);
    function token1() external view returns (address);
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
```

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-71)
```text
    function mint(
        address to
    ) external returns (uint256 liquidity) {
        uint112 reserve0 = _reserve0;
        uint112 reserve1 = _reserve1;

        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));
        uint256 amount0 = balance0 - reserve0;
        uint256 amount1 = balance1 - reserve1;

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

        _mint(to, liquidity);

        _reserve0 = uint112(balance0);
        _reserve1 = uint112(balance1);
    }
```

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```
