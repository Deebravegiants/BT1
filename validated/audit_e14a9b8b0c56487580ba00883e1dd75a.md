### Title
Direct-transfer donation of the launched Token to its `Pair` permanently disables the supply-based graduation trigger, freezing the LP reserve and curve-raised LT - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.canGraduate` treats `IPair(pair).tokenBalance() == 0` as one of two independent graduation triggers [1](#0-0) . `tokenBalance()` is a live `IERC20.balanceOf(pair)` read, not the pool's stored, swap-only `tokenReserve` [2](#0-1) . Because this equality check is exact (`== 0`), any unprivileged holder can permanently and irreversibly disable the supply trigger for a specific token by directly transferring even a tiny amount of that launched `Token` to its `Pair` address, a plain ERC20 transfer that is explicitly in-scope per the prompt's rules.

### Finding Description
`Router._computeBuy`/`sell` only ever move `tokenReserve` (the stored virtual reserve) and the real ERC20 balance by the exact same amount on every buy/sell, via `Pair.swap` and `transferToken`/direct pair transfers [3](#0-2) . Consequently, under normal trading, `reserveToken(stored) - tokenBalance(live)` is a constant equal to the `LP_RESERVE` gap set at launch, an invariant explicitly asserted by the test suite: `test_inv_virtualReserveAlwaysExceedsRealBalance` [4](#0-3) .

A direct ERC20 `transfer(pair, amount)` of the launched `Token`, bypassing `Bonding.sell`/`Router.sell`, increases the live `tokenBalance()` without touching the stored `_pool.tokenReserve` (only `Pair.swap`, callable only via `onlyRouter`, mutates it) [5](#0-4) . Every subsequent buy still decrements the stored reserve and the live balance by the exact same `tokensOut`, so the donated offset never shrinks back to zero on its own — `tokenBalance()` can never again equal exactly `0`, no matter how the curve trades afterward. This makes the equality check in `canGraduate` permanently unsatisfiable via the supply leg for that token: [6](#0-5) 

Since donated tokens are only ever burned inside `_prepareGraduationLiquidity`, which runs *after* `canGraduate` returns true, the burn-on-graduation defense described in the docs never fires for a token whose supply trigger has been permanently blocked and whose USD trigger (`realLtRaised × exchangeRate ≥ threshold`) never crosses the fixed `$9K` threshold — exactly the "flat/bear market" scenario the docs say the supply trigger exists to cover [7](#0-6) . For such a token, `Lifecycle.Curve` never transitions to `Graduating`/`Graduated`: `_enterGraduating`, `Router.graduate`, and LP seeding are all unreachable [8](#0-7) .

### Impact Explanation
The result is permanent freezing of protocol funds for the affected token:
- The `LP_RESERVE` (250M) tokens held by `Bonding` for that token are never released to an LP or burned, since that only happens inside `_prepareGraduationLiquidity` [9](#0-8) .
- All curve-raised LT sitting in the `Pair` (`assetReserve - virtualLtReserve`) is never drained via `Router.graduate`, so it is permanently locked in the pair with no other authorized withdrawal path (`Router.graduate`/`Pair.transferAsset` require `BONDING_ROLE`, only invoked from `_prepareGraduationLiquidity`) [10](#0-9) .
- The token can never migrate to the HyperSwap V2 pool, permanently denying post-graduation liquidity/fee flows for creator/protocol on that token.

This qualifies as "permanent freezing of trader, creator or LP funds" per the validation criteria. Severity is bounded by the fact that curve buy/sell still function normally (traders are not locked out of trading on the bonding curve itself), which argues for Medium/High rather than Critical, but the frozen LP reserve and raised LT are a real, permanent, unrecoverable loss of protocol-intended value.

### Likelihood Explanation
The attack requires only owning and transferring a nonzero amount of the target's own launched `Token` directly to its `Pair` address — a single unprivileged ERC20 `transfer` call, reachable by any trader who has bought even a small amount on the curve (or by the token's own creator). No special timing, capital beyond a small token purchase, or privileged role is required. It is a deliberate, cheap, and irreversible griefing action, but it is fully reachable by any unrelated wallet, satisfying the "unprivileged" reachability bar.

### Recommendation
Change the supply trigger in `canGraduate` (and its mirrored logic in `previewLtUntilGraduation` and `_prepareGraduationLiquidity`) to be donation-immune, e.g. compare the stored `tokenReserve` against the real balance with a `<=` threshold derived from the known `LP_RESERVE`/curve-supply invariant, or track curve-sold tokens via an explicit stored counter rather than relying on an exact `balanceOf == 0` equality that a griefer can permanently perturb with a single donation.

### Proof of Concept
1. Launch a token via `Zap.createToken` (or `Bonding.launch`), noting `pair = tokenInfo.pair`.
2. Buy a small amount of the token so the caller holds a nonzero `Token` balance.
3. Call `Token.transfer(pair, 1)` — a single-wei direct donation to the pair.
4. Continue buying through `Bonding.buy`/`Zap.buy` until the curve would otherwise be fully sold (`tokenBalance()` would hit `0`). Observe `IPair(pair).tokenBalance()` never reaches `0` (it stabilizes at `1`), so `canGraduate`'s supply leg (`packages/contracts/src/Bonding.sol:689`) never returns `true`.
5. If the paired LT's `exchangeRate()` stays below the USD threshold (e.g., a flat-priced LT scenario, as already exercised by `test_inv_supplyTrigger_belowUsdThreshold` in `GraduationInvariants.t.sol`), the token is permanently stuck in `Lifecycle.Curve`, and `finalizeGraduation`/`Router.graduate` are never reachable — freezing the `LP_RESERVE` tokens and curve-raised LT indefinitely.

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

**File:** packages/contracts/src/Pair.sol (L65-79)
```text
    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }
```

**File:** packages/contracts/src/Pair.sol (L95-105)
```text
    function getReserves() external view returns (uint256, uint256) {
        return (_pool.tokenReserve, _pool.assetReserve);
    }

    function k() external view returns (uint256) {
        return _pool.k;
    }

    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }
```

**File:** packages/contracts/src/Router.sol (L92-148)
```text
    function buy(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);

        (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
    }

    /// @notice External view of `_computeBuy`. Returns `(amountInUsed,
    ///         tokensOut)` for a hypothetical LT-in buy of `amountIn`,
    ///         honouring the same overflow cap as `buy()`. Used by `Zap` to
    ///         pre-size the LT mint and by the frontend for buy-quote previews.
    function previewBuy(
        address token,
        uint256 amountIn
    ) external view returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        return _computeBuy(pairAddr, amountIn);
    }

    /// @dev Capped: `amountInUsed` is back-calculated from the K invariant
    ///      (rounded up so the curve never under-charges).
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
    }
```

**File:** packages/contracts/src/Router.sol (L184-211)
```text
    /// @notice Transfer exactly `amount` of LT out of the pair to the caller.
    ///         Called by `Bonding._prepareGraduationLiquidity` during graduation
    ///         with `amount = stored assetReserve - virtualLtReserve` (i.e. the
    ///         real LT raised by the curve, excluding the virtual seed).
    /// @dev    Donation-resistant: passing an explicit `amount` instead of
    ///         draining `assetBalance()` ensures any LT that was donated
    ///         directly to the pair via `IERC20.transfer` is left behind and
    ///         excluded from LP seeding.
    ///
    ///         "Locked" here is a trust-assumption claim, not an on-chain
    ///         guarantee. `Pair.transferAsset` is gated by `onlyRouter`, and
    ///         `Router` only exposes it via this function and `sell`. Both
    ///         require `BONDING_ROLE`, which only `Bonding` holds. `Bonding`
    ///         in turn only calls `graduate` from
    ///         `_prepareGraduationLiquidity` — which is unreachable once the
    ///         token's lifecycle has flipped past `Curve`. So the leftover
    ///         is unreachable as long as (a) `BONDING_ROLE` is not granted
    ///         to any other address, and (b) future `Bonding` upgrades
    ///         preserve the lifecycle gate.
    function graduate(
        address token,
        uint256 amount
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        IPair(pairAddr).transferAsset(msg.sender, amount);
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L362-377)
```text
    function test_inv_virtualReserveAlwaysExceedsRealBalance() public {
        (address tokenAddr, address pairAddr) = _launchNoSeed();

        // Right after launch.
        assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "post-launch invariant");

        // After a series of buys the property must continue to hold while
        // the curve is still trading.
        for (uint256 i = 0; i < 10; i++) {
            if (!bonding.isTrading(tokenAddr)) break;
            _buy(tokenAddr, trader, 100 ether);
            if (bonding.isTrading(tokenAddr)) {
                assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "invariant must hold after every buy");
            }
        }
    }
```

**File:** docs/contracts-scope.md (L66-73)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)
```
