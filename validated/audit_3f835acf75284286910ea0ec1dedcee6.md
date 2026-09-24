### Title
Launch-time `uint112` headroom check in `_deployAndSeed` goes stale as the LT's `exchangeRate` depreciates, letting graduation deposit a real-LT amount that overflows the HyperSwap V2 pair's reserve slot and permanently bricks `finalizeGraduation` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding._deployAndSeed` validates, once at launch, that the curve's `virtualLtReserve` leaves 4x headroom under `type(uint112).max` so that the real LT eventually deposited into the HyperSwap V2 pair "can never exceed that slot." [1](#0-0)  That bound is computed from the LT's `exchangeRate()` sampled at launch time and assumes real LT raised peaks at `3 * virtualLtReserve`. Because the reserve asset is a leveraged token whose price can fall sharply after launch, the same fixed-USD graduation threshold requires proportionally more raw LT units to satisfy, so the actual `assetReserve` (and the `ltFromPair` amount later deposited into the HyperSwap pair) is not bounded by the launch-time check at all. This is the same bug class as CVE-2023-23609: a size check performed once against stale/assumed parameters, while the quantity that is later written into a fixed-capacity buffer (here, the HyperSwap V2 pair's `uint112` reserve slot) is reassembled/accumulated afterward without re-validation.

### Finding Description
`_deployAndSeed` derives `virtualLtReserve = VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate` at launch and reverts if it exceeds `type(uint112).max / 4`, with the natspec explicitly reasoning that "the raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)" so this "4x headroom" bound is safe for the pair's `uint112` reserve slots. [2](#0-1) 

The graduation trigger, however, is denominated in USD and re-reads the *live* `exchangeRate()` every time, not the launch-time snapshot: `canGraduate` computes `realLtRaised * exchangeRate() / 1e18 >= graduationThresholdUsd`. [3](#0-2)  If the LT's `exchangeRate()` falls after launch (a leveraged token can lose most of its value on an adverse move in the underlying), the same fixed `graduationThresholdUsd` requires a proportionally larger `realLtRaised` in raw LT units to satisfy — there is no re-check against the `uint112` capacity at this point, and the "peaks at 3x" assumption from `_deployAndSeed` (which implicitly assumes a roughly constant exchange rate) no longer holds.

That inflated `ltFromPair` is exactly the amount phase 1 (`_prepareGraduationLiquidity`) computes and caches, and phase 2 (`finalizeGraduation` → `_seedUniswapV2Direct` → `_seedDirectMint` / `_seedRebalancing`) unconditionally attempts to deposit into the HyperSwap V2 pair via `pair.mint`/`pair.swap`. [4](#0-3) [5](#0-4)  Since the standard V2 pair's reserve-update path requires both balances to fit in `uint112` and reverts otherwise, a `ltFromPair` that has grown past the `uint112` capacity permanently reverts every call to `finalizeGraduation` for that token.

Crucially, once `_enterGraduating` has fired (either via a crossing buy or via the permissionless `triggerGraduation`), the token is stuck in `Lifecycle.Graduating` forever: `info.lifecycle = Lifecycle.Graduating` is one-directional (`Curve → Graduating → Graduated`), trading is frozen, and there is no admin or user path back to `Curve` or to reclaim the curve-raised LT/`LP_RESERVE` tokens sitting on `Bonding`. [6](#0-5) [7](#0-6) 

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged trader/creator interaction with the curve (ordinary buys, or the permissionless `Bonding.triggerGraduation`). Once a token's `assetReserve` (in raw LT units) has grown enough — due to the LT's price having fallen since launch — to push `ltFromPair` past the `uint112` capacity that `_deployAndSeed`'s one-time check assumed would never be reached, `finalizeGraduation` reverts unconditionally and permanently for that token. All curve-raised LT (the entire real reserve backing every buyer's exposure) and the 250M-token `LP_RESERVE` remain locked in `Bonding` with no rescue mechanism, and holders can never receive their post-graduation LP exposure. This is exactly the class of freezing the review rules flag: "a permissionless two-phase graduation that parks all curve-raised LT and 250M tokens on Bonding between phases."

### Likelihood Explanation
The precondition is a large, sustained depreciation of the paired BounceTech LT's `exchangeRate()` between a token's launch and its graduation — plausible for a leveraged token, whose entire purpose is amplified price movement, especially over the (potentially long) time a slow-moving curve takes to reach the USD graduation threshold. No privileged action, upgrade, or off-chain step is required; ordinary buy activity (or a permissionless `triggerGraduation` call) is sufficient to cross the threshold and enter phase 1, after which the deposit in phase 2 is guaranteed to attempt the oversized write.

### Recommendation
Re-validate the `uint112` capacity bound against the *actual* `ltFromPair`/`assetReserve` computed in `_prepareGraduationLiquidity` at phase-1 time (using the live exchange rate), not only the launch-time snapshot in `_deployAndSeed`. If the live-computed amount would overflow the HyperSwap pair's `uint112` reserve, either cap/split the deposit, add a governance-recoverable escape hatch for a token stuck in `Lifecycle.Graduating`, or reject `_enterGraduating` until the amount can be safely split across the deposit.

### Proof of Concept
1. Attacker/creator launches a token paired with a highly volatile BounceTech LT close to `_deployAndSeed`'s allowed ceiling (`virtualLtReserve` just under `type(uint112).max / 4`), which passes the `ExchangeRateTooLow` check. [1](#0-0) 
2. Over time the underlying the LT tracks falls sharply, so the LT's `exchangeRate()` drops (e.g., to 20-25% of its launch value), which is within the normal behavior of a leveraged token.
3. Ordinary buyers keep buying on the curve (or anyone calls the permissionless `Bonding.triggerGraduation`) until `canGraduate` — which reads the live `exchangeRate()` — returns true: `realLtRaised * exchangeRate() / 1e18 >= graduationThresholdUsd`. [3](#0-2)  Because `exchangeRate()` has fallen, `realLtRaised` in raw LT units is now several times larger than the `3 * virtualLtReserve` figure `_deployAndSeed` assumed, pushing it past the `uint112` capacity.
4. `_enterGraduating` fires, freezing the token in `Lifecycle.Graduating` and caching the oversized `ltFromPair` in `pendingGraduation`. [6](#0-5) 
5. Anyone calls `finalizeGraduation`; `_seedUniswapV2Direct`/`_seedDirectMint` attempts to deposit `ltFromPair` into the HyperSwap V2 pair, which reverts because the resulting reserve does not fit in `uint112`. [5](#0-4)  Every subsequent call reverts identically — the token is permanently stuck, with all curve-raised LT and the 250M `LP_RESERVE` tokens locked in `Bonding` and no recovery path.

### Citations

**File:** packages/contracts/src/Bonding.sol (L437-484)
```text
    /// @dev Launch-time `exchangeRate()` snapshot permanently shapes the
    ///      curve via `K = TOTAL_SUPPLY * virtualLtReserve`. The
    ///      `VIRTUAL_LIQUIDITY_USD / rate` division pins the opening market
    ///      cap at `~VIRTUAL_LIQUIDITY_USD` regardless of the LT's price;
    ///      what the snapshot fixes is the curve's USD-denominated depth,
    ///      which then drifts with the LT.
    ///
    ///      Drift is accepted: it's inherent to using a leveraged token as
    ///      the reserve (same drift class as the phase-1 → phase-2 gap on
    ///      `finalizeGraduation`). The snapshot is also a pre-checkpoint
    ///      view — `exchangeRate()` doesn't settle the LT's accrued
    ///      streaming fee until the seed buy's `mint` checkpoints it moments
    ///      later — so the curve opens off a rate marginally above the
    ///      settled one, bounded by the pending fee and immaterial. A
    ///      donation attack on the LT's `baseAssetBalance` to skew the
    ///      snapshot is cost-negative — the donation is irrevocable and the
    ///      only direct victim is the creator's `MIN_SEED_USDC`-floored seed
    ///      buy.
    ///
    ///      No `(min, max)` band on `LaunchParams` by design: a band
    ///      introduces a launch-failure mode users can't diagnose and forces
    ///      the frontend into a default tolerance that's either too tight
    ///      (legitimate launches fail) or too loose (decorative).
    function _deployAndSeed(
        address tokenAddr,
        bytes32 saltMixed,
        string calldata name_,
        string calldata ticker_,
        address ltAddress
    ) internal returns (address pair) {
        BondingStorage storage $ = _s();
        Clones.cloneDeterministic($.tokenImplementation, saltMixed);

        Token(tokenAddr).initialize(name_, ticker_, address(this));

        uint256 totalSupply = Token(tokenAddr).TOTAL_SUPPLY();
        uint256 curveSupply = (totalSupply * CURVE_BPS) / BPS_DENOM;

        pair = $.factory.createPair(tokenAddr, ltAddress);

        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
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

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
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
