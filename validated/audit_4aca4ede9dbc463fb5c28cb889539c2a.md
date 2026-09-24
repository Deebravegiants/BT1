### Title
Sub-`MINIMUM_LIQUIDITY` graduation permanently bricks `finalizeGraduation` via HyperSwap V2 first-mint underflow - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation`'s happy-path liquidity seeding (`_seedDirectMint`, Regime 1, ~99% of graduations) transfers the phase‑1‑cached `(tokensForLP, ltFromPair)` straight into the freshly created HyperSwap V2 pair and calls `pair.mint(lpLock)` [1](#0-0) . On an empty V2-style pair, the first mint computes `liquidity = sqrt(amount0*amount1) - MINIMUM_LIQUIDITY` (`MINIMUM_LIQUIDITY = 1000`), which underflows and reverts with a Solidity Panic when `sqrt(tokensForLP * ltFromPair) < 1000` [2](#0-1) . Because `tokensForLP`/`ltFromPair` are frozen at phase‑1 time and phase 2 always replays the same values [3](#0-2) , any graduation whose cached amounts fall under this floor bricks permanently — no retry can succeed.

### Finding Description
Graduation has a dual trigger: the USD trigger fires when `(storedAssetReserve − virtualLtReserve) × exchangeRate() ≥ graduationThresholdUsd` [4](#0-3) . This is explicitly designed to fire on legitimate LT price pumps with very little real LT raised — the docs call this out for "flat/bear markets" on the supply side and "HYPE pumps" on the USD side [5](#0-4) . When `exchangeRate()` is large relative to `graduationThresholdUsd`, the real LT needed to cross the threshold (`realLtRaised`) can be pushed down to a handful of wei by the ceiling division in `previewLtUntilGraduation` / the implicit threshold math [6](#0-5) .

`_prepareGraduationLiquidity` computes `ltFromPair = assetReserve − virtualLtReserve` and `tokensForLP = ltFromPair × tokenReserve / assetReserve`, caps at `LP_RESERVE`, and caches both in `pendingGraduation` at the end of phase 1 [7](#0-6) . There is no floor check anywhere in this pipeline enforcing `sqrt(tokensForLP * ltFromPair) ≥ MINIMUM_LIQUIDITY`. Phase 2's Regime‑1 path (the pristine/empty-pair case that the codebase's own comments say covers ~99% of graduations) transfers exactly these cached amounts to the pair and calls `pair.mint(lpLock)` with no size guard [8](#0-7) . On a real (or the test-faithful mock) V2 pair, the virgin-pair mint formula is `liquidity = sqrt(amount0*amount1) - MINIMUM_LIQUIDITY`; if the product's square root is below `1000`, this line underflows in Solidity 0.8's checked arithmetic and reverts with a bare Panic(0x11) [2](#0-1) .

Because `finalizeGraduation` is permissionless and re-derives nothing — it just replays the byte-identical cached `(tokensForLP, ltFromPair)` from `pendingGraduation[token]` on every call, and the values never change between attempts (the by-design "no freshness gate" rationale) [9](#0-8)  — every subsequent call by the keeper or any rescuer hits the exact same underflow and reverts identically. The token is stuck in `Lifecycle.Graduating` forever: trading is already frozen by phase 1, `Router.graduate` has already drained the curve's real LT into `Bonding` [10](#0-9) , and the 250M `LP_RESERVE` tokens sit unburned/unminted in `Bonding`. There is no admin override, no rescue path, and `LPLock` itself explicitly has no rescue mechanism either [11](#0-10) .

This is the direct structural analog of BIT‑openldap‑2020‑25710 / CVE‑2020‑25710: a piece of externally-influenced state (here, curve reserves shaped by the LT's live, market-driven `exchangeRate()`) is fed into a downstream normalization/accounting routine (V2's `sqrt(amount0*amount1) - MINIMUM_LIQUIDITY`) without a bounds check, causing a failed low-level assertion (arithmetic underflow Panic) that permanently denies service on the affected object — here, an entire token's graduation and its escrowed funds, instead of an LDAP server process.

### Impact Explanation
This is a **High** severity permanent freezing-of-funds bug reachable by an ordinary, unprivileged trade sequence combined with organic LT price movement (no privileged role, no upgrade, no off-chain component required):
- All curve-raised real LT for that token (already moved out of the curve `Pair` into `Bonding` via `Router.graduate`) becomes permanently unreachable — `finalizeGraduation` can never succeed to distribute it into the LP, and there is no alternate withdrawal path.
- The 250M `LP_RESERVE` tokens held by `Bonding` for that token are permanently stuck (never minted into LP, never burned).
- Every holder of the launched token is permanently locked out — trading is frozen by phase 1 and can never resume because phase 2 can never complete.
- `LPLock` has no rescue mechanism, so even the tiny amount of successfully-transferred value has no recovery path.

### Likelihood Explanation
Likelihood is **plausible but not trivially attacker-forced**: the trigger condition is a real, live BounceTech LT exchange rate high enough (relative to `graduationThresholdUsd`) that the USD-trigger threshold is crossed while `realLtRaised` (and consequently `tokensForLP`) is small enough that `sqrt(tokensForLP × ltFromPair) < 1000`. The docs themselves acknowledge the USD trigger is specifically designed to fire "with supply remaining" on LT pumps [12](#0-11) , i.e., exactly the regime where `ltFromPair`/`tokensForLP` can be minimal. A sufficiently large legitimate market move in the leveraged LT's underlying (which is the entire point of the leveraged-token reserve design) or a token launched against an already highly appreciated LT can produce this state without any attacker action; an attacker who controls seed size and buy timing on a token paired against a volatile/high-leverage LT can also engineer it deliberately by minimizing the buy that crosses the USD threshold.

### Recommendation
Add an explicit floor check in `_prepareGraduationLiquidity` (or in `_seedDirectMint` before calling `pair.mint`) that guarantees `tokensForLP × ltFromPair` clears the V2 `MINIMUM_LIQUIDITY` bound (or its square), and define a safe fallback (e.g., top up the smaller side from `Bonding`'s own held reserves, or defer graduation until the curve state naturally clears the floor) so that `finalizeGraduation` can never construct a mint call that underflows on the target DEX. Given the codebase's stated "Phase 2 must never revert under any pre-seed shape" invariant, this floor should be treated with the same priority as the existing brick-resistance test suite (`test/TwoPhaseGraduation.t.sol`), and a regression test should assert that graduations with vanishingly small `ltFromPair`/`tokensForLP` still succeed.

### Proof of Concept
1. Launch a token against an LT whose `exchangeRate()` is (or becomes) very large relative to `graduationThresholdUsd` (e.g. via `MockLeveragedToken.setExchangeRate` in tests, modeling a real LT market pump).
2. Execute a minimal `Zap.buy` / `bonding.buy` that raises just enough real LT to cross `(storedAssetReserve - virtualLtReserve) × exchangeRate() ≥ graduationThresholdUsd`, per `Bonding.canGraduate` [4](#0-3) . Size the buy so the resulting `ltFromPair` and `tokensForLP` (visible via `bonding.pendingGraduation(tokenAddr)` after phase 1) satisfy `sqrt(tokensForLP * ltFromPair) < 1000`.
3. Phase 1 fires inline (`_enterGraduating`), freezing trading and caching the tiny `(tokensForLP, ltFromPair)`.
4. Call `bonding.finalizeGraduation(tokenAddr)` (permissionless). The empty-pair mint in `_seedDirectMint` reverts with an arithmetic underflow Panic inside the V2 pair's first-mint `sqrt(amount0*amount1) - MINIMUM_LIQUIDITY` computation [2](#0-1) .
5. Every subsequent call to `finalizeGraduation` reverts identically since `pendingGraduation[tokenAddr]` is unchanged; the token is permanently stuck in `Lifecycle.Graduating`, freezing its drained curve LT and the 250M reserved tokens with no recovery path.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L697-726)
```text
    /// @notice LT amount that must be added to the curve's `assetReserve` for
    ///         `canGraduate(token_)` to become true. `0` when already
    ///         graduatable or not in `Lifecycle.Curve`.
    /// @dev    Composes the two `canGraduate` legs (supply trigger from
    ///         `IPair.tokenBalance() == 0`, USD trigger from
    ///         `realLtRaised × exchangeRate / 1e18 ≥ graduationThresholdUsd`)
    ///         and returns the cap-binding `min`. Ceil-div on the USD leg
    ///         so the resulting buy strictly crosses the threshold.
    function previewLtUntilGraduation(
        address token_
    ) external view returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return 0;
        if (info.lifecycle != Lifecycle.Curve) return 0;

        address pair = info.pair;
        uint256 realBalance = IPair(pair).tokenBalance();
        if (realBalance == 0) return 0;

        (uint256 reserveToken, uint256 reserveAsset) = IPair(pair).getReserves();

        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }
```

**File:** packages/contracts/src/Bonding.sol (L981-1023)
```text
    /// @notice Phase 2: seed the V2 LP and lock it. Permissionless —
    ///         keeper drives the happy path; anyone can rescue a stuck token.
    /// @dev Bypasses the V2 router and calls `pair.mint(lpLock)`
    ///      directly. This is brick-proof against a front-runner pre-creating
    ///      the pair and dust-seeding it between phases.
    /// @dev Exchange-rate drift between phase 1 and phase 2 is accepted by
    ///      design. The cached `(tokensForLP, ltFromPair)` are pure pair-
    ///      state arithmetic — see `_prepareGraduationLiquidity`, which
    ///      never reads `exchangeRate()` — so the LP opens at the exact
    ///      LT-per-token ratio the curve closed at, regardless of how long
    ///      phase 2 takes. What drifts is only the USD denomination of the
    ///      LT side, which is inherent to using a leveraged token as the
    ///      curve reserve: holders accept that exposure when they buy in.
    ///      A keeper Worker drives finalize within ~60s of `TokenGraduating`,
    ///      so the practical drift window is single-digit seconds. No
    ///      freshness timestamp / staleness gate: a recompute would return
    ///      byte-identical values (inputs are frozen while
    ///      `Lifecycle.Graduating`), and re-pricing the LP at the live
    ///      `exchangeRate()` would break the zero-gap-in-LT-units invariant.
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

**File:** packages/contracts/test/mocks/MockHyperswapRouter.sol (L45-65)
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
```

**File:** docs/contracts-scope.md (L68-76)
```markdown
Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

```

**File:** packages/contracts/src/LPLock.sol (L9-18)
```text
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `LPLockStorage` at `_LP_LOCK_STORAGE_LOCATION`.
```
