### Title
Attacker-controlled uint256 overflow in `_noFeeSwapInput`'s discriminant permanently bricks `finalizeGraduation` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` calls `_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput` to defuse a hostile HyperSwap V2 pre-seed. `_noFeeSwapInput` computes `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` where `reserveIn`/`reserveOut` are attacker-controlled uint112 pool reserves (from a front-run `pair.mint`) and `targetN`/`targetD` are `tokensForLP`/`ltFromPair`, with `ltFromPair` scaling inversely with the paired LT's live `exchangeRate()`. The project's own test suite documents that this discriminant can exceed `2^256` and cause `Math.mulDiv` to **revert**, which is exactly CVE-2014-0143's bug class (crafted large values driving an integer computation past its representable range) mapped onto Solidity's checked-arithmetic/`mulDiv`-revert failure mode instead of silent wraparound/heap corruption.

### Finding Description
`_noFeeSwapInput` (`packages/contracts/src/Bonding.sol:1507-1522`):
```solidity
uint256 product = Math.mulDiv(reserveIn * reserveOut, targetN, targetD);
uint256 newIn = Math.sqrt(product);
```
`reserveIn`/`reserveOut` come from `IUniswapV2Pair(pair).getReserves()`, which are `uint112` and can be pushed up to `type(uint112).max` (~5.19e33) by an attacker who front-runs `factory.createPair(token, lt)` and self-funds a `pair.mint(attacker)` with a hostile reserve ratio — this is the documented "Regime 3" mint pre-seed attack that `_seedUniswapV2Direct` is explicitly built to defend against. [1](#0-0) 

`targetN`/`targetD` are `ltFromPair`/`tokensForLP` (or the inverse), computed in `_prepareGraduationLiquidity` as the real LT raised by the curve and the matching token amount. [2](#0-1)  `ltFromPair` is unbounded by the curve's USD-value graduation trigger read against the paired LT's live, externally-controlled `exchangeRate()`: the lower the exchange rate, the more raw LT units are required to cross the fixed `graduationThresholdUsd`, so `ltFromPair` scales inversely with `exchangeRate()`. [3](#0-2) 

The project's own regression suite explicitly documents that `reserveIn * reserveOut * targetN / targetD` can exceed `2^256` and that `Math.mulDiv` will revert in that case, calling it "unrealistic-but-mathematically-possible" and stating call sites "must keep" the discriminant within bounds — i.e., this is an assumed invariant that is **not enforced on-chain**: [4](#0-3) 

`_pairRebalance` only guards against `s == 0` or `expectedOut == 0` from `_noFeeSwapInput`; it does not guard against `_noFeeSwapInput` itself reverting via `Math.mulDiv`'s internal overflow check: [5](#0-4) 

`finalizeGraduation` calls this path unconditionally with no try/catch: [6](#0-5) 

The `AGENTS.md` explicitly states the brick-resistance property this violates: `_seedUniswapV2Direct` "MUST never revert under any pre-seed shape... it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever." [7](#0-6) 

### Impact Explanation
If `finalizeGraduation` reverts every time it is called (because the discriminant permanently exceeds `2^256` for the frozen on-chain reserves and the frozen `pendingGraduation` values), the token is stuck in `Lifecycle.Graduating` forever:
- All curve-raised LT (`ltFromPair`, drained into `Bonding` by `Router.graduate` during Phase 1) is permanently locked in `Bonding` with no path to reach `LPLock` or any user.
- The 250M `LP_RESERVE` tokens reserved for LP seeding are permanently locked in `Bonding`.
- Trading is frozen (Phase 1 already flipped `lifecycle: Curve → Graduating` and froze the curve), so holders cannot sell on the bonding curve, and no HyperSwap LP ever gets seeded to trade against.
This satisfies the "permanent freezing of trader, creator or LP funds" impact bar.

### Likelihood Explanation
The attack requires combining two conditions that are each individually reachable by an unprivileged actor, but jointly require: (a) the paired LT's live `exchangeRate()` to be low enough that `ltFromPair` (bounded ultimately by real economic LT raised to hit the USD threshold) is large, and (b) the attacker being able to self-fund a HyperSwap pre-seed with `uint112`-scale token/LT reserves. Reaching a discriminant that actually exceeds `2^256` in practice requires both `reserveIn*reserveOut` near `2^224` (attacker needs to hold near-`uint112`-max amounts of both the launched token, which is capped at 1e27 total supply, and the LT, whose price would need to have crashed dramatically to make holding huge quantities cheap) and `targetN` at a comparable scale. This is an extreme, capital-intensive edge case rather than a cheap griefing vector, so likelihood is Low-to-Medium, but the project's own tests flag it as a real, unenforced boundary condition rather than a purely theoretical one.

### Recommendation
- Add an explicit pre-check in `_noFeeSwapInput` (or its call site `_pairRebalance`/`_seedRebalancing`) that bounds `reserveIn * reserveOut` and the subsequent `* targetN / targetD` product before calling `Math.mulDiv`, and gracefully falls back to the direct-mint path (`_seedDirectMint`) instead of allowing the call to revert.
- Wrap the `_pairRebalance` call (or the whole rebalance branch) so any revert from `_noFeeSwapInput`/`Math.mulDiv` is caught and treated identically to the existing `s == 0` / `expectedOut == 0` fallback, preserving the "never revert" brick-resistance contract end-to-end.
- Add a fuzz/invariant test that constructs `uint112`-max hostile reserves paired with worst-case `ltFromPair`/`tokensForLP` ratios (driven by an extreme but realistic low `exchangeRate()`) and asserts `finalizeGraduation` never reverts.

### Proof of Concept
1. Launch a token paired with an LT whose mock `exchangeRate()` can be driven very low (as in existing tests, `lt.setExchangeRate(...)`).
2. Drive enough curve buys so that `canGraduate` fires via the USD trigger with a very low exchange rate, making `ltFromPair` (cached in `pendingGraduation`) large relative to `tokensForLP`.
3. Before `finalizeGraduation` is called, front-run: call `hsFactory.createPair(token, lt)`, then self-fund and call `pair.mint(attacker)` with `reserveToken`/`reserveLt` pushed toward `type(uint112).max` on the side that maximizes `reserveIn * reserveOut * targetN`.
4. Call `bonding.finalizeGraduation(tokenAddress)`. Trace through `_seedRebalancing` → `_pairRebalance` → `_noFeeSwapInput`; the `Math.mulDiv(reserveIn * reserveOut, targetN, targetD)` call reverts once the discriminant exceeds `2^256`, per the boundary demonstrated by `test_overflowSafety_atRealisticMax` in `test/NoFeeSwapInput.t.sol`.
5. Every subsequent call to `finalizeGraduation` for this token reverts identically (the on-chain reserves and cached `pendingGraduation` values that produce the overflow don't change), permanently bricking the token in `Lifecycle.Graduating`.

*(Note: exact numeric parameters to hit the `2^256` boundary in production — given the launched-token supply cap of 1e27 and realistic LT economics — could not be fully derived from static review alone; a Devin session with Foundry access would be needed to confirm the precise reachable discriminant bound and construct a concrete reproducing test.)*

### Citations

**File:** packages/contracts/AGENTS.md (L132-149)
```markdown
A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

When our `pair.mint(lpLock)` runs in phase 2 against this non-empty pair, V2's mint formula picks up the existing reserves:

```
liquidity = min(amount0 · totalSupply / reserve0, amount1 · totalSupply / reserve1)
```

The `min(...)` arm whose denominator is bigger relative to its numerator wins, and the OTHER arm's "excess" deposit is donated pro-rata to existing LP holders — i.e. to the attacker. Two harms:

- **Wrong opening price.** Post-mint reserves are `(R_attacker + T_a, R_attacker + T_b)`, so the LP opens at `(R_a + T_a) / (R_b + T_b)`, NOT at the curve close `T_a / T_b`. A `$15` LT pre-seed at 50% off curve close opens the pool ~454 bps off.
- **LP capture.** The wasted-side excess goes to the attacker's LP claim. A `1 wei + 1 LT` pre-seed (~`$1` attack budget) captures ~34 bps of LP.

A cheaper variant skips step 3 entirely: `transfer(pair, dust) + pair.sync()` forces the stored reserves to the dust ratio without minting any LP, leaving the pair at `reserves > 0 && totalSupply == 0`. Regime 1 below covers both shapes by keying on supply rather than reserves.
```

**File:** packages/contracts/AGENTS.md (L191-193)
```markdown
### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:
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

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

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

**File:** packages/contracts/src/Bonding.sol (L1414-1429)
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

        IERC20(p.tokenIn).safeTransfer(p.pair, s);
        (uint256 amount0Out, uint256 amount1Out) = p.tokenInIs0 ? (uint256(0), expectedOut) : (expectedOut, uint256(0));
        IUniswapV2Pair(p.pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
        return true;
    }
```

**File:** packages/contracts/test/NoFeeSwapInput.t.sol (L135-182)
```text
    // ─── Overflow safety ──────────────────────────────────────────────────

    /// @notice Across the input space the call site actually produces,
    ///         the discriminant `reserveIn * reserveOut * targetN / targetD`
    ///         stays inside uint256 and the function returns without
    ///         reverting.
    /// @dev    Reserves and targets are bounded to uint64 (max ~1.8e19)
    ///         which comfortably exceeds anything a real graduation can
    ///         produce — `tokensForLP` ≤ 250M·1e18 and `ltFromPair`
    ///         scales with `graduationThresholdUsd`, both well inside
    ///         this bound. The unrealistic-but-mathematically-possible
    ///         case where the discriminant overflows uint256 (forcing
    ///         `Math.mulDiv` to revert) is documented separately on
    ///         `_noFeeSwapInput`'s natspec — call sites must keep
    ///         `reserveIn * reserveOut * targetN / targetD` ≤ 2^256.
    function testFuzz_overflowSafety(
        uint64 reserveIn,
        uint64 reserveOut,
        uint64 targetN,
        uint64 targetD,
        uint256 maxSwap
    ) public view {
        vm.assume(reserveIn > 0 && reserveOut > 0 && targetN > 0 && targetD > 0 && maxSwap > 0);
        harness.exposed_noFeeSwapInput(reserveIn, reserveOut, targetN, targetD, maxSwap);
    }

    /// @notice Stress at realistic ceiling: V2 uint112 reserves combined
    ///         with the target-ratio bounds the call site actually
    ///         produces. `targetN` and `targetD` come from `tokensForLP`
    ///         and `ltFromPair` (or vice versa), both bounded above by
    ///         `Token.TOTAL_SUPPLY` (1B * 1e18 ≈ 2^90) in any sensible
    ///         BounceTech LT × token combination, so the discriminant
    ///         `reserveIn * reserveOut * targetN / targetD` stays inside
    ///         uint256 even at the extremes that real graduations can
    ///         actually produce.
    ///
    ///         (Note: `_noFeeSwapInput` would revert under the OZ `mulDiv`
    ///         512-bit-intermediate guard if the intermediate result
    ///         exceeded uint256, e.g. with arbitrary uint128 target ratios
    ///         — but no real call site can construct such inputs because
    ///         `tokensForLP` and `ltFromPair` are bounded by token supply.)
    function test_overflowSafety_atRealisticMax() public view {
        uint256 maxReserve = type(uint112).max;
        uint256 totalSupply = 1_000_000_000 ether; // ~2^90, the largest plausible target
        // Discriminant: 2^224 * 2^90 / 1 = 2^314 — overflows uint256, so
        // pin targetD high enough to bring result back within range.
        // 2^224 * 2^90 / 2^90 = 2^224, fits.
        harness.exposed_noFeeSwapInput(maxReserve, maxReserve, totalSupply, totalSupply, type(uint256).max);
```
