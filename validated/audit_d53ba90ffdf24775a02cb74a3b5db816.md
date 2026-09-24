Based on my analysis, I don't find a valid analog for this vulnerability class in the alt.fun codebase.

**Investigation summary:**

The Perennial bug is a subtraction/delta underflow (`latestPosition.invalidation.sub(self.invalidation)` then applied to `self.long`) that can go negative when settlement ordering causes a stored delta to exceed the current value.

The closest analogous subtraction patterns in alt.fun are the `assetReserve - virtualLtReserve` computations used across `Bonding.canGraduate`, `Bonding.previewLtUntilGraduation`, and `Bonding._prepareGraduationLiquidity` [1](#0-0) , plus the `reserveToken - realBalance` supply-leg subtraction in `previewLtUntilGraduation` [2](#0-1) .

However:
1. `_launchTimeVirtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`, and `Pair.k` is immutable after `mint` [3](#0-2) . Because the virtual token reserve (`totalSupply`) is a hard ceiling on `reserveToken` that sells can never exceed (only `curveSupply` real tokens exist to sell back), the constant-product relationship guarantees `assetReserve ≥ virtualLtReserve` at all times, making that subtraction underflow-safe by construction.
2. The exact bug class this report describes — a donation/state-drift causing a stored subtraction to underflow (`realBalance > reserveToken` breaking the supply-leg subtraction in `previewLtUntilGraduation`) — was already discovered and patched in this codebase, as documented directly in the test suite: *"A TOKEN donation that drives `realBalance > reserveToken` previously underflowed `Bonding.previewLtUntilGraduation`'s supply leg, cascading into a `Zap.buy` DoS. Guard added; tests pin the fix."* [4](#0-3)  with regression coverage in `test_donation_realBalanceExceedsReserveToken` and `test_donation_previewLtUntilGraduation_returnsThresholdLeg` [5](#0-4) , and the guard itself is visible at the `if (realBalance >= reserveToken) return ltUntilThreshold;` early return [6](#0-5) .
3. I also chec

### Citations

**File:** packages/contracts/src/Bonding.sol (L691-694)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L728-736)
```text
        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;

        return ltUntilSupply < ltUntilThreshold ? ltUntilSupply : ltUntilThreshold;
    }
```

**File:** packages/contracts/src/Pair.sol (L55-63)
```text
    function mint(
        uint256 tokenReserve,
        uint256 assetReserve
    ) external onlyRouter returns (bool) {
        if (_pool.k != 0) revert AlreadyMinted();
        _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
        emit Mint(tokenReserve, assetReserve);
        return true;
    }
```

**File:** packages/contracts/test/Zap.t.sol (L939-942)
```text
    // ─── Donation attack regression ──────────────────────────────────────
    // A TOKEN donation that drives `realBalance > reserveToken` previously
    // underflowed `Bonding.previewLtUntilGraduation`'s supply leg,
    // cascading into a `Zap.buy` DoS. Guard added; tests pin the fix.
```

**File:** packages/contracts/test/Zap.t.sol (L967-989)
```text
    function test_donation_realBalanceExceedsReserveToken() public {
        address tokenAddr = _createToken(0);
        address pairAddr = bonding.getTokenInfo(tokenAddr).pair;

        (, uint256 donated) = _stageDonationAttack(tokenAddr);
        assertGt(donated, 250_000_000 ether, "Drain must yield > 250M tokens to break the gap");

        uint256 realBalance = IPair(pairAddr).tokenBalance();
        (uint256 reserveToken,) = IPair(pairAddr).getReserves();
        assertGt(realBalance, reserveToken);
    }

    function test_donation_previewLtUntilGraduation_returnsThresholdLeg() public {
        address tokenAddr = _createToken(0);

        uint256 capBefore = bonding.previewLtUntilGraduation(tokenAddr);
        _stageDonationAttack(tokenAddr);

        uint256 capAfter = bonding.previewLtUntilGraduation(tokenAddr);
        // Non-zero so `Zap._executeBuy` doesn't degrade to floor-bumping every buy.
        assertGt(capAfter, 0);
        assertLt(capAfter, capBefore);
    }
```
