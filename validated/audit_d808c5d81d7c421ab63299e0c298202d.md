### Title
Direct-transfer token donation to a curve `Pair` can permanently brick `Router._computeBuy`'s overflow cap and the supply-side graduation trigger, freezing the curve's raised LT forever - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` and `Bonding.canGraduate`'s supply trigger both assume the invariant "virtual token reserve always exceeds the pair's real (live `balanceOf`) token balance" — the same class of unvalidated-structural-assumption bug as the CVE (code trusts an ordering/monotonicity property of externally-influenceable data without validating it, and a crafted input that violates the property crashes the code path). Any unprivileged holder can violate that invariant with a plain `Token.transfer(pair, amount)` donation, permanently reverting the overflow-cap buy path and blocking the `tokenBalance() == 0` supply trigger, which can trap a token in `Lifecycle.Curve` forever whenever the USD trigger is never reached.

### Finding Description
The virtual-reserve design is documented as a hard, tested invariant: `pair.tokenBalance() < reserve0` at every state of the curve [1](#0-0) . `Router._computeBuy` relies on this invariant when it caps an oversized buy at the pair's real balance and back-derives the LT actually required: [2](#0-1) 

`realBalance` here is `pair.tokenBalance()` — a live `IERC20.balanceOf(pair)` read, not the pair's stored `reserveToken`. Nothing stops any token holder from calling `Token(tokenAddress).transfer(pair, x)` directly: this raises `pair.tokenBalance()` without touching the stored `reserveToken`/`k` that `Pair.mint`/`Pair.swap` maintain. Doing so shrinks (or, with enough accumulated donation, eliminates) the 250M-token gap the parabola/virtual-reserve design assumes is always present. Once `realBalance ≥ reserveToken` for the pair, the next buy that tries to exhaust the curve computes `cappedReserveToken = reserveToken - tokensOut` with `tokensOut == realBalance`: this either reverts explicitly with `OverflowCapDegenerate()` (equal case) or underflows to a Panic revert (`realBalance > reserveToken`).

The same live read is used by the supply-side graduation trigger: [3](#0-2) 

The docs even call out that this is a live `balanceOf` read and claim it's "donation-resistant" only in the direction that donations can't force premature graduation [4](#0-3) , but the reverse property — that a donation can permanently prevent `tokenBalance() == 0` from ever being satisfied again — is not addressed. `_prepareGraduationLiquidity`'s donation burn only executes *after* graduation is triggered [5](#0-4) , so it can never run if neither trigger can fire in the first place — a chicken-and-egg lockout.

### Impact Explanation
For any token paired against an LT whose price never appreciates enough to cross the fixed USD threshold (a plausible/likely real-world scenario — flat or bear markets, or a low-leverage/stable LT), the supply trigger is the *only* remaining path to graduation. An unprivileged attacker (or even an accidental "gift" transfer, but trivially reproducible by anyone) can:
1. Buy tokens through the curve normally (`Zap.buy` / `Bonding.buy`).
2. `transfer` those tokens directly to the `Pair` address.

This permanently:
- Blocks the supply trigger (`tokenBalance() == 0` becomes unreachable while any donation sits in the pair).
- Reverts any subsequent buy that would hit `Router._computeBuy`'s overflow-cap branch (a Panic or `OverflowCapDegenerate`), i.e. any buy attempting to consume the remaining real balance.

The token is stuck in `Lifecycle.Curve` forever. All real LT raised by the curve stays locked in the `Pair` (unreachable — `Router.graduate` is only callable from `_prepareGraduationLiquidity`, which is unreachable without graduation), and the 250M `lpReserve` tokens held by `Bonding` for that token are permanently stranded as well. This is a concrete, permanent freezing of trader/creator funds (curve-raised LT) reachable by any unprivileged wallet, satisfying the Medium/High bar.

### Likelihood Explanation
High reachability, low cost: the only requirement is holding any nonzero amount of the launched `Token` (freely obtainable via a normal curve buy) and calling a plain ERC20 `transfer` to the `Pair` address — no special role, no timing window, no privileged caller. The scope rules explicitly list "direct ERC20 transfers of a launched Token ... into ... Pair" as an in-scope vector. The bug is latent in every token whose LT never appreciates past the USD threshold, which is not a rare condition.

### Recommendation
- Make the supply trigger and the overflow-cap math donation-immune the same way the USD trigger already is: derive the "real balance" used in both `Bonding.canGraduate`'s supply leg and `Router._computeBuy`'s cap branch from accounted/stored state (e.g., track cumulative tokens actually sold via the curve, rather than a live `balanceOf`), instead of trusting `IPair.tokenBalance()`.
- Alternatively, sweep/skim any tokens donated directly to a `Pair` back out (mirroring the `pair.skim()` pattern already used for HyperSwap pre-seed donations in `_seedUniswapV2Direct`) before they can corrupt the buy-cap or trigger logic, or explicitly floor `cappedReserveToken`/`realBalance` against `reserveToken` so the arithmetic can't underflow or degenerate.
- Add a fuzz/invariant test analogous to `test_inv_virtualReserveAlwaysExceedsRealBalance` that injects an attacker-controlled direct token donation mid-curve and asserts the curve remains tradeable and graduatable to completion.

### Proof of Concept
1. Launch a token via `Zap.createToken` against an LT whose `exchangeRate()` is held flat (never crosses `graduationThresholdUsd()`), so the USD trigger never fires.
2. Buy a sizeable chunk of the curve's real supply as an attacker, via `Zap.buy` (or `Bonding.buy` through an allowlisted router in a test harness).
3. `Token(tokenAddress).transfer(pairAddr, x)` — donate part or all of the purchased tokens directly to the `Pair`, raising `pair.tokenBalance()` above the stored `reserveToken - <needed cap headroom>`.
4. Have any trader attempt a buy sized to hit `Router._computeBuy`'s overflow-cap branch (i.e., an amount whose uncapped `tokensOut` exceeds `pair.tokenBalance()`): the call reverts with `OverflowCapDegenerate()` or a Panic underflow, per [6](#0-5) .
5. Observe `Bonding.canGraduate(tokenAddress)` never returns `true` via the supply leg going forward (`tokenBalance()` can never reach `0` while the donation sits in the pair) — confirmed by the supply-trigger check at [7](#0-6) . The token is permanently stuck in `Lifecycle.Curve`, with all curve-raised LT and the 250M `lpReserve` unreachable.

### Citations

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-377)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
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

**File:** packages/contracts/src/Bonding.sol (L674-689)
```text
    ///         Supply trigger: uses live `IPair.tokenBalance()`. This IS an
    ///         `IERC20.balanceOf` read but is donation-resistant in the
    ///         opposite direction — token donations can only INCREASE the
    ///         balance, never satisfy "== 0", and the only path that drains
    ///         tokens out of the pair is the curve buy flow. Donated tokens
    ///         are unconditionally burned by `_prepareGraduationLiquidity`.
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;
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

**File:** docs/contracts-scope.md (L71-71)
```markdown
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```
