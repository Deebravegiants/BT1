## Finding [1](#0-0) 

The WavPack CVE's root cause — an attacker-tainted `cnt` that is used to size a pointer walk without validating it against the buffer it indexes into — maps onto `Router._computeBuy`'s overflow-cap branch, which uses an attacker-inflatable `pair.tokenBalance()` read as `tokensOut` without validating it against `reserveToken` before subtracting.

### Title
Token-donation-inflated `pair.tokenBalance()` causes unguarded underflow revert in `Router._computeBuy`'s overflow cap, permanently DoS'ing curve-completing buys and the supply-trigger graduation path - (File: packages/contracts/src/Router.sol)

### Summary
`Router._computeBuy` caps `tokensOut` at `pair.tokenBalance()` (the pair's live ERC20 balance) whenever the uncapped curve math would exceed it, then back-calculates `amountInUsed` via `cappedReserveToken = reserveToken - tokensOut`. This subtraction assumes `tokensOut ≤ reserveToken`. An unprivileged attacker can violate that assumption for free by directly `transfer`-ing the launched `Token` to the `Pair` contract, inflating `pair.tokenBalance()` (`realBalance`) above the stored `reserveToken`. Once that holds, any buy large enough to hit the cap branch sets `tokensOut = realBalance > reserveToken`, and `reserveToken - tokensOut` reverts with an arithmetic-underflow panic instead of the intended `OverflowCapDegenerate` custom error.

### Finding Description
`Router._computeBuy` [1](#0-0)  reads:

```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
    amountInUsed = cappedReserveAsset - reserveAsset;
}
```

`pair.tokenBalance()` is a live `IERC20(launchedToken).balanceOf(pair)` read [2](#0-1) , which anyone can inflate by directly transferring the launched `Token` to the `Pair` — a permissionless ERC20 transfer explicitly listed as in-scope. `reserveToken`, by contrast, is only the *stored* pool reserve, updated exclusively through `Pair.swap` [3](#0-2) ; a direct token donation does not touch it.

The protocol already recognized this exact bug class and patched it — but only in `Bonding.previewLtUntilGraduation`, not in `Router._computeBuy` itself:

```solidity
// Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
if (realBalance >= reserveToken) return ltUntilThreshold;
``` [4](#0-3) 

The regression test suite even documents the original bug and its (partial) fix: "*A TOKEN donation that drives `realBalance > reserveToken` previously underflowed `Bonding.previewLtUntilGraduation`'s supply leg, cascading into a `Zap.buy` DoS. Guard added; tests pin the fix.*" [5](#0-4)  The test helper `_stageDonationAttack` proves the donation reliably produces `realBalance > reserveToken` [6](#0-5) , but no equivalent guard or regression test exists for `Router._computeBuy`'s own cap branch. The project's own invariant comment only anticipated `realBalance == reserveToken` (yielding the *handled* `cappedReserveToken == 0` → `OverflowCapDegenerate` case) [7](#0-6) , not `realBalance > reserveToken`, which produces an *unhandled* underflow panic instead.

### Impact Explanation
Once an attacker donates enough `Token` to the pair to push `tokenBalance()` above `reserveToken`, every subsequent buy whose uncapped curve output would exceed the (now-inflated) real balance — i.e., every buy attempting to drain the remaining real curve supply — reverts with an uncontrolled arithmetic panic instead of completing via the intended cap-and-refund path. This is exactly the "last buy that empties the curve" scenario covered by the overflow-cap invariant test [8](#0-7) , which the donation permanently breaks for that token: the supply-based graduation trigger (`tokenBalance() == 0`) becomes permanently unreachable, since the buy that would zero out the real balance can never succeed. If the LT's exchange rate never independently satisfies the USD trigger, the token — and the LT already raised by traders on that curve — is permanently stuck in `Lifecycle.Curve`, unable to graduate and seed the HyperSwap V2 LP, for the cost of one attacker-funded token donation (donated tokens are otherwise worthless to the attacker and are burned at graduation, so the attack is a pure griefing move with a bounded, small cost).

### Likelihood Explanation
Reachable by any unrelated wallet with a trivial `IERC20(token).transfer(pair, amount)` call — no privileged role, no complex setup, and the test harness already demonstrates the precondition (`realBalance > reserveToken`) is easy to stage with an ordinary curve buy followed by a donation of the purchased tokens back to the pair.

### Recommendation
Add the same guard used in `Bonding.previewLtUntilGraduation` to `Router._computeBuy`: when `realBalance >= reserveToken`, either treat the cap as already saturated (skip the back-calculation and revert with the existing `OverflowCapDegenerate`, or a new dedicated error) rather than letting `reserveToken - tokensOut` underflow uncontrolled.

### Proof of Concept
1. Launch a token normally via `Zap.createToken`.
2. Buy enough on the curve via `Zap.buy` to receive a large `Token` balance (mirrors `_stageDonationAttack`'s drain step) [9](#0-8) .
3. `Token(tokenAddr).transfer(pairAddr, purchasedTokens)` — a plain unrelated-wallet ERC20 transfer, pushing `pair.tokenBalance() > reserveToken`.
4. Submit a large buy via `Zap.buy` / `Bonding.buy` sized to attempt draining the remaining real curve supply. `Router._computeBuy`'s `tokensOut > realBalance` branch fires, sets `tokensOut = realBalance`, then `cappedReserveToken = reserveToken - tokensOut` underflows and the whole buy transaction reverts with a bare arithmetic-underflow panic — no cap-and-refund, no graduation, and the supply trigger for this token is now permanently unreachable.

### Citations

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

**File:** packages/contracts/src/Pair.sol (L103-105)
```text
    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }
```

**File:** packages/contracts/src/Bonding.sol (L728-733)
```text
        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;
```

**File:** packages/contracts/test/Zap.t.sol (L939-965)
```text
    // ─── Donation attack regression ──────────────────────────────────────
    // A TOKEN donation that drives `realBalance > reserveToken` previously
    // underflowed `Bonding.previewLtUntilGraduation`'s supply leg,
    // cascading into a `Zap.buy` DoS. Guard added; tests pin the fix.

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
```

**File:** packages/contracts/test/Zap.t.sol (L967-977)
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
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L328-351)
```text
    // ─── 7. Overflow cap & refund ────────────────────────────────────────

    function test_inv_overflowCap_refundsLt() public {
        (address tokenAddr,) = _launchNoSeed();
        // Crash exchange rate so USD trigger never fires and we can isolate the supply
        // trigger & overflow-cap path.
        lt.setExchangeRate(0.0001 ether);

        uint256 balancePre = lt.balanceOf(trader2);
        // Grossly oversized buy that would attempt to absorb >1B tokens on the curve.
        // Real balance is 750M, so `Router.buy` must cap at 750M and back-calc the LT used.
        uint256 oversizedBuy = 1_000_000_000 ether;

        (uint256 tokensOut, uint256 amountInUsed) = _buy(tokenAddr, trader2, oversizedBuy);

        assertTrue(bonding.isGraduated(tokenAddr), "graduated on capped buy");
        assertTrue(amountInUsed < oversizedBuy, "buy must be capped below oversized request");
        assertEq(tokensOut, CURVE_SUPPLY, "tokensOut must equal remaining real supply");

        // `bonding.buy` pulls only `amountInUsed` from trader2 (via Router → pair + fees).
        uint256 balancePost = lt.balanceOf(trader2);
        uint256 ltConsumed = balancePre + oversizedBuy - balancePost;
        assertEq(ltConsumed, amountInUsed, "trader should only pay `amountInUsed`, not the requested amount");
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-361)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
```
