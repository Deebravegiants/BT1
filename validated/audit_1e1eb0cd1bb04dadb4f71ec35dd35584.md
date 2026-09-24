## Title
Direct Token donation to the curve `Pair` permanently disables the supply-exhaustion graduation trigger, bricking graduation and freezing `LP_RESERVE`/curve liquidity forever — ([File: packages/contracts/src/Bonding.sol], [File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Pair.sol])

### Summary
CVE-2019-2982 is a MySQL optimizer bug that lets an attacker permanently hang/crash the server (repeatable DOS with no self-recovery). The alt.fun analog is a permanent, self-inflicted DoS of `Bonding`'s supply-exhaustion graduation trigger: an unrelated wallet can permanently and irrecoverably neutralize `IPair.tokenBalance() == 0` for any launched token by donating enough of the launched `Token` directly to its `Pair`, using nothing but a plain ERC20 `transfer`.

### Finding Description
Graduation has two triggers [1](#0-0) :
- USD trigger: computed from **stored** `assetReserve`, immune to donations.
- Supply trigger: `IPair(pair).tokenBalance() == 0` — a **live** `balanceOf` read.

`Pair.swap` moves the stored `tokenReserve` and the real ERC20 `tokenBalance()` by exactly the same delta on every buy/sell [2](#0-1) . This means the quantity `D = tokenBalance() - tokenReserve` is invariant under normal trading. At launch `D = curveSupply - totalSupply = -250,000,000e18` (the "virtual token reserve" design, `realTokenAmount = 75%` of the virtual `tokenReserve`) [3](#0-2) .

Any wallet can call `Token(tokenAddress).transfer(pair, X)` directly (a plain ERC20 transfer any unrelated wallet can submit, listed as in-scope reachable surface). This increases `tokenBalance()` without touching stored `tokenReserve`, so it increases `D` by `X`. If an attacker first buys enough tokens off the curve (>250M tokens, easily done via `Bonding.buy`) and then donates them back to the `Pair`, `D` flips positive and **stays positive forever** — because `D` is invariant under every subsequent buy/sell (`Router._computeBuy`'s uncapped `tokensOut = reserveToken - k/newReserveAsset` is mathematically always `< reserveToken`) [4](#0-3) . Since `realBalance = reserveToken + D` with `D > 0`, `realBalance` can never again equal `0`. `IPair.tokenBalance() == 0` therefore becomes permanently unreachable — this is exactly the property the docs describe as intentional donation-resistance, but its consequence for the *opposite* direction (donation instead of drain) is a permanent kill of the only fallback trigger:

> "Supply trigger: uses live `IPair.tokenBalance()` ... donation-resistant in the opposite direction — token donations can only INCREASE the balance, never satisfy `== 0`" [5](#0-4) 

The codebase's own regression test proves the exact mechanics of pushing `realBalance > reserveToken` via a 500M-token donation are practically reachable and cost-bounded [6](#0-5) , though that test only pins the (already-patched) view-function underflow in `previewLtUntilGraduation` [7](#0-6)  — it does not address that the same donation permanently disables the supply trigger itself in `canGraduate`.

Once the supply trigger is dead, graduation depends solely on the USD trigger: `(assetReserve - virtualLtReserve) × exchangeRate ≥ $9K`. The docs explicitly state the supply trigger exists precisely because the USD trigger is not guaranteed to fire — "handles flat/bear markets where $9K is never reached" [8](#0-7) . For any token paired with an LT that stagnates or depreciates, a single donation attack permanently traps that token in `Lifecycle.Curve`:
- `finalizeGraduation`/`_enterGraduating` can never fire, so `LP_RESERVE` (250M tokens per token, reserved in `Bonding`) is never burned down or deposited into a HyperSwap LP [9](#0-8)  — it sits dead in `Bonding` forever.
- The token never reaches deeper HyperSwap liquidity; all trading is permanently confined to the internal curve with no LP lock ever created, regardless of how much real LT traders continue to pour in.

### Impact Explanation
This is a permanent, irreversible denial of the protocol's core "graduate to DEX" feature for any targeted token, triggerable by a single unprivileged wallet with no special role, purely via `Token.transfer` (an explicitly in-scope reachable action) plus ordinary curve buys. It permanently locks `LP_RESERVE` tokens in `Bonding` with no burn/seed path and permanently strands the token on the internal curve — denying creators and traders the graduation event and deep liquidity the protocol promises, with no owner/admin recovery path (no setter exists to correct the reserve/balance divergence). This satisfies "permanent freezing of trader/creator/LP funds" at Medium severity, matching CVE-2019-2982's "hang / repeatable non-recoverable denial" characterization once mapped onto alt.fun's real reachable surface.

### Likelihood Explanation
Reachable by any wallet with capital roughly equal to the cost of a large curve buy (500M+ tokens' worth of LT, refundable in part by later selling back if the attacker only needs the tokens transiently before donating, but the tokens used for the donation itself are a sunk cost). No governance, upgrade, or privileged role is required — only `Bonding.buy`/`Zap.buy` (or a direct router-holder buy in tests) followed by a plain ERC20 `Token.transfer(pair, amount)`. This is squarely inside the allowed unprivileged-trader threat surface.

### Recommendation
Do not rely on a live `balanceOf` read for the supply trigger. Track sold-supply via a stored counter (incremented in `Router.buy`/decremented in `Router.sell`, mirroring how `tokenReserve` is already tracked) and trigger graduation off that stored counter reaching `curveSupply`, exactly as the USD trigger already uses stored `assetReserve` rather than a live balance. This removes the donation vector entirely while preserving donation-resistance in the direction the comment intends.

### Proof of Concept
1. Launch a token (`Bonding.launch`/`Zap.createToken`).
2. Attacker (any wallet) buys enough of the curve to receive >250,000,000e18 tokens (`bonding.buy`/`Zap.buy`, sized as in `_stageDonationAttack`) [10](#0-9) .
3. Attacker calls `Token(tokenAddress).transfer(pair, donatedTokens)` — a plain unrestricted ERC20 transfer.
4. `IPair(pair).tokenBalance() > IPair(pair).getReserves().reserveToken` now holds permanently (`test_donation_realBalanceExceedsReserveToken` confirms this state is reachable) [11](#0-10) .
5. For any subsequent trading history, `tokenBalance()` can never reach `0` again because `Router.buy`/`Router.sell` move `tokenBalance()` and stored `reserveToken` by identical deltas each time — `canGraduate`'s supply leg (`IPair(pair).tokenBalance() == 0`) is permanently `false`.
6. If the paired LT's `exchangeRate()` never appreciates enough to cross the USD threshold, `canGraduate` never returns `true` again for this token — `_enterGraduating`/`finalizeGraduation` are permanently unreachable, and this token's `LP_RESERVE` allocation in `Bonding` is permanently stranded.

### Citations

**File:** packages/contracts/src/Bonding.sol (L674-679)
```text
    ///         Supply trigger: uses live `IPair.tokenBalance()`. This IS an
    ///         `IERC20.balanceOf` read but is donation-resistant in the
    ///         opposite direction — token donations can only INCREASE the
    ///         balance, never satisfy "== 0", and the only path that drains
    ///         tokens out of the pair is the curve buy flow. Donated tokens
    ///         are unconditionally burned by `_prepareGraduationLiquidity`.
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

**File:** packages/contracts/src/Bonding.sol (L705-736)
```text
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

        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;

        return ltUntilSupply < ltUntilThreshold ? ltUntilSupply : ltUntilThreshold;
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

**File:** docs/contracts-scope.md (L34-38)
```markdown
**Virtual token reserve.** The pair's `reserve0` is seeded at `totalSupply` (1B) while only `curveSupply = 75%` (750M) of real tokens are actually transferred. The other 250M are held in `Bonding` as `lpReserve`. This virtual-reserve design:

- Extends the curve beyond the sellable supply.
- Gives a deterministic supply trigger (curve exhausts at 750M sold).
- Makes the dynamic-LP-seeding parabola `tokensForLP(sold) = sold·(S−sold)/S` peak at exactly `S/4 = 250M = LP_RESERVE` — so `tokensForLP ≤ lpReserve` is a mathematical invariant, not a runtime guess.
```

**File:** docs/contracts-scope.md (L70-71)
```markdown
- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```

**File:** packages/contracts/src/Router.sol (L127-148)
```text
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

**File:** packages/contracts/test/Zap.t.sol (L944-977)
```text
    function _stageDonationAttack(
        address tokenAddr
    ) internal returns (uint256 drainLtSpent, uint256 donatedTokens) {
        address pairAddr = bonding.getTokenInfo(tokenAddr).pair;
        address drainer = makeAddr("donationDrainer");
        // Size the drain so `tokensOut > 250M` (the LP-reserve floor) under
        // any `VIRTUAL_LIQUIDITY_USD`. Constant-product math gives
        // `tokensOut = TOTAL_SUPPLY × ltIn / (virtual + ltIn)`, which crosses
        // 250M (= ¼ of TOTAL_SUPPLY) when `ltIn = virtual / 3`. Spending the
        // full opening virtual reserve lands `tokensOut = 500M` — plenty of
        // headroom to push `realBalance > reserveToken` after the donation.
        drainLtSpent = _initialVirtualLt();
        lt.mintDirect(drainer, drainLtSpent);
        if (!bonding.isRouter(drainer)) bonding.addRouter(drainer);
        vm.startPrank(drainer);
        lt.approve(address(curveRouter), drainLtSpent);
        bonding.buy(drainLtSpent, tokenAddr, 0, drainer);
        vm.stopPrank();
        donatedTokens = Token(tokenAddr).balanceOf(drainer);
        vm.prank(drainer);
        Token(tokenAddr).transfer(pairAddr, donatedTokens);
    }

    function test_donation_realBalanceExceedsReserveToken() public {
        address tokenAddr = _createToken(0);
        address pairAddr = bonding.getTokenInfo(tokenAddr).pair;

        (, uint256 donated) = _stageDonationAttack(tokenAddr);
        assertGt(donated, 250_000_000 ether, "Drain must yield > 250M tokens to break the gap");

        uint256 realBalance = IPair(pairAddr).tokenBalance();
        (uint256 reserveToken,) = IPair(pairAddr).getReserves();
        assertGt(realBalance, reserveToken);
    }
```
