### Title
`finalizeGraduation` can permanently revert (and brick a graduated token forever) when the cached `(tokensForLP, ltFromPair)` amounts are too small to satisfy HyperSwap V2's `MINIMUM_LIQUIDITY` first-mint check - ([File: packages/contracts/src/Bonding.sol])

### Summary
The CVE describes a service that crashes on an input shape its parser never expected to handle (malformed/non-JSON messages), with no recovery. The analogous root cause here is a hard-coded external revert (`UniswapV2Pair.mint`'s `INSUFFICIENT_LIQUIDITY_MINTED` check, `sqrt(amount0*amount1) > MINIMUM_LIQUIDITY`) that the "brick-proof" `finalizeGraduation` phase never defends against, unlike every other pre-seed shape it explicitly handles.

### Finding Description
`Bonding._enterGraduating` caches `tokensForLP` and `ltFromPair` at the last curve price via `_prepareGraduationLiquidity`, storing them in `pendingGraduation[token]` [1](#0-0) . These values are frozen and cannot be recomputed - `finalizeGraduation` consumes them verbatim [2](#0-1) .

In the ~99%-of-graduations "Regime 1" path, `_seedUniswapV2Direct` routes straight to `_seedDirectMint`, which transfers `tokensForLP`/`ltFromPair` to the pair and calls `IUniswapV2Pair(pair).mint(_s().lpLock)` directly [3](#0-2) . A vanilla UniswapV2 pair's `mint()` on an empty pair computes `liquidity = sqrt(amount0*amount1) - MINIMUM_LIQUIDITY` and **reverts with `INSUFFICIENT_LIQUIDITY_MINTED`** if that underflows (i.e., if `sqrt(tokensForLP * ltFromPair) <= 1000`). This is an unconditional external revert that `_seedDirectMint` does not catch, size-check, or otherwise route around.

Every other adversarial pre-seed shape (empty, donation, hostile mint pre-seed, even a catastrophic pre-seed that would otherwise zero out the deposit) is explicitly defended against - the protocol's own documentation states the swap budget is capped specifically "Reserving 1% guarantees the deposit leg always lands AND mints non-zero LP at the post-swap ratio" and that a zero-liquidity outcome would make `LPLock.recordLock` revert with `ZeroAmount` [4](#0-3) , and `LPLock.recordLock` indeed hard-reverts on `amount == 0` [5](#0-4) . But none of this handling covers the case where the *honest*, un-attacked `tokensForLP`/`ltFromPair` pair themselves are simply numerically too small (below V2's `MINIMUM_LIQUIDITY = 1000` floor) - which is reachable without any attacker pre-seed at all, purely through the protocol's own dual-trigger graduation mechanics:

- `k` (and hence the launch-time virtual LT reserve) is sized per-token off the paired LT's price at launch to target a fixed ~$3K market cap [6](#0-5) .
- The supply trigger (`IPair.tokenBalance() == 0`) graduates a token purely on units of tokens sold, independent of USD value raised [7](#0-6) .
- For an LT priced such that the $3K-mcap-derived `k` corresponds to a very small absolute LT quantity (a legitimately possible LT/price combination, not attacker-controlled), the curve can be fully sold out (supply trigger) while `ltFromPair` and the correspondingly-derived `tokensForLP` are both dust-small in absolute terms.

Once phase 1 fires with such dust amounts cached, `finalizeGraduation` is guaranteed to revert every single time it is called (permissionless, callable by anyone, including retries) because the underlying V2 `mint()` computation is deterministic and the cached inputs never change. There is no owner override, no way to update `pendingGraduation`, and no fallback within `_seedDirectMint` for this failure mode - unlike the swap/rebalance path, which explicitly checks `getAmountOut == 0` before calling `pair.swap` to avoid exactly this class of external revert.

### Impact Explanation
This is a permanent freeze of funds, not a griefing/DoS that resolves itself:
- The token is permanently stuck in `Lifecycle.Graduating` - trading is frozen (`Bonding.buy`/`sell` revert with `TokenIsGraduating`) for that token forever.
- The curve-raised LT (`ltFromPair`, drained from the pair into `Bonding` by `Router.graduate` during phase 1) and the reserved 250M `LP_RESERVE` tokens sitting on `Bonding` are permanently unrecoverable - there is no rescue path for a token parked in this failed state.
- `Zap.buy`/`Zap.sell` for that token become permanently unusable (both check `isGraduating` and revert).
- This satisfies "permanent freezing of trader, creator or LP funds" from the validation criteria.

### Likelihood Explanation
This does not require a malicious actor pre-seeding the HyperSwap pair - it can occur on the *honest* graduation path for any LT whose price/parameterization makes the fixed ~$3K-mcap `k` correspond to a small absolute LT-unit reserve, combined with the token being fully sold out via the supply trigger (a legitimate flat/bear-market scenario the supply trigger is explicitly designed to handle, per the docs). Given alt.fun supports arbitrary BounceTech LTs as reserve assets with a wide range of possible prices/exchange rates, this is a realistic, protocol-native edge case rather than a contrived attack requiring privileged access - well within reach of "an unrelated wallet" simply trading normally until the curve sells out.

### Recommendation
Add an explicit floor check in `_prepareGraduationLiquidity` (or `_enterGraduating`) that guarantees `sqrt(tokensForLP * ltFromPair) > MINIMUM_LIQUIDITY` (1000) before caching the graduation amounts, and/or add a defensive `try/catch` (or pre-computed minimum-liquidity check) around the `pair.mint` call in `_seedDirectMint`, with a documented recovery path (e.g., burning/sweeping the parked LT and tokens, or scaling up the deposit) if the cached amounts are ever found to be below the V2 floor. This closes the same class of gap the protocol already closed for the swap/rebalance leg (`_pairRebalance`'s `expectedOut == 0` check) and for the zero-liquidity `LPLock.recordLock` case (the 1% swap-budget reservation).

### Proof of Concept
1. Launch a token paired against an LT whose price is such that `k = f(exchangeRate)` sizing the ~$3K market cap yields a virtual LT reserve on the order of a few thousand wei (a legitimate LT/price combination the protocol permits without restriction).
2. Trade the curve to full sellout via ordinary `Zap.buy` calls (or a single large one, capped by `Router.buy`'s overflow logic) until `IPair.tokenBalance() == 0`, firing the supply trigger and `_enterGraduating`.
3. `_prepareGraduationLiquidity` computes and caches `tokensForLP`/`ltFromPair` such that `sqrt(tokensForLP * ltFromPair) <= 1000`.
4. Call `Bonding.finalizeGraduation(tokenAddress)` (permissionless, callable by anyone) - `_seedDirectMint`'s `IUniswapV2Pair(pair).mint(lpLock)` call reverts with `INSUFFICIENT_LIQUIDITY_MINTED`.
5. Every subsequent call to `finalizeGraduation` for this token reverts identically forever; the token is permanently stuck in `Lifecycle.Graduating`, and the LT/tokens parked on `Bonding` for it are unrecoverable.

(Note: exact reachability of the specific numeric threshold depends on live BounceTech LT prices/exchange rates at launch time, which are external and not fully enumerable from the indexed contract code alone; the root-cause code path and its lack of a floor check are confirmed directly in `packages/contracts/src/Bonding.sol`.)

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

**File:** packages/contracts/src/Bonding.sol (L1217-1259)
```text
        // Regime 1 — no LP minted yet (`totalSupply == 0`): a pristine empty
        // pair, or a dust pre-seed from `transfer(pair, dust) + sync()` that
        // leaves reserves non-zero while supply is still zero. Keying on
        // supply rather than reserves routes the dust shape here instead of
        // the rebalance path: with zero supply V2 mints from our amounts
        // alone, so the pool opens at the cached ratio and any dust becomes
        // reserves with no LP claim.
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

    /// @dev Transfer the full `(tokensForLP, ltFromPair)` to the pair and
    ///      `mint` the LP to `LPLock`, opening at the exact cached
    ///      curve-close ratio. Used by the empty-pair regime and as the
    ///      dust-pre-seed fallback in `_seedRebalancing` — against dust
    ///      reserves the V2 `min()` formula's donation to any pre-existing
    ///      LP is negligible (see `_seedUniswapV2Direct` natspec). Any TOKEN
    ///      remainder (a skimmed pure-donation pre-seed) is burned; the LT
    ///      remainder is left for `finalizeGraduation`'s `_sweepLTToOwner`
    ///      post-bookend.
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

**File:** packages/contracts/src/LPLock.sol (L70-85)
```text
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

**File:** docs/contracts-scope.md (L32-38)
```markdown
This deploys a `Token` clone (1B supply) and creates a `Pair` (token/LT). K is computed per token so every token opens at ~`$3K` market cap regardless of which LT is paired.

**Virtual token reserve.** The pair's `reserve0` is seeded at `totalSupply` (1B) while only `curveSupply = 75%` (750M) of real tokens are actually transferred. The other 250M are held in `Bonding` as `lpReserve`. This virtual-reserve design:

- Extends the curve beyond the sellable supply.
- Gives a deterministic supply trigger (curve exhausts at 750M sold).
- Makes the dynamic-LP-seeding parabola `tokensForLP(sold) = sold·(S−sold)/S` peak at exactly `S/4 = 250M = LP_RESERVE` — so `tokensForLP ≤ lpReserve` is a mathematical invariant, not a runtime guess.
```

**File:** docs/contracts-scope.md (L68-76)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

```
