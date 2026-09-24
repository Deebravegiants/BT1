Based on my investigation, the `Bonding.previewLtUntilGraduation` underflow was already patched (donation-inflated `realBalance` case is explicitly guarded at line 729: `if (realBalance >= reserveToken) return ltUntilThreshold;`), and `Zap.buy` continues to succeed even under the donation attack per `test_donation_zapBuyStillSucceeds` and `test_donation_sellsStillWork`.

However, `Router._computeBuy` — the function `Zap.buy`'s curve path and `Router.buy` itself ultimately execute against — was **not** patched with the same guard:

```solidity
// packages/contracts/src/Router.sol:140-146
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;   // underflows if tokensOut > reserveToken
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    ...
``` [1](#0-0) 

The invariant that "protects" this line — `tokenBalance() < reserve0` always — is only proven to hold across ordinary curve buys, per the test's own comment: "the `cappedReserveToken == 0` branch in `Router._computeBuy` is unreachable [under buys]; if it ever ceased to hold, that branch would revert." [2](#0-1)  The repo's own regression test proves the invariant is *not* preserved under direct token donations: `test_donation_realBalanceExceedsReserveToken` shows any unprivileged wallet can drain most of the curve then `Token.transfer(pairAddr, donatedTokens)` to push `realBalance > reserveToken`. [3](#0-2) 

Once `realBalance` (post-donation) exceeds `reserveToken`, any subsequent buy whose uncapped `tokensOut` exceeds `realBalance` (which is now guaranteed once `tokensOut > realBalance` since `realBalance` already exceeds `reserveToken`) hits `tokensOut = realBalance > reserveToken`, and `cappedReserveToken = reserveToken - tokensOut` underflows — a Solidity 0.8 arithmetic-underflow revert (Panic 0x11), not the guarded `OverflowCapDegenerate()` error. This permanently reverts every `Bonding.buy` / `Zap.buy` on that curve (`Router.buy` is the sole curve-buy path called by `Bonding._executeBuy`) — a full denial of service for all future traders on that token, and the token can never reach the supply-graduation trigger via a capped buy either, since the capping branch itself is what breaks.

This is a direct structural analog to the ws advisory: a single unprivileged, low-cost input (a plain ERC20 `transfer` donation, no special role) that a contract's own arithmetic doesn't defensively guard against, causing every subsequent legitimate request (buy transactions) on that resource to crash/revert — a classic reachable, unauthenticated DoS.

### Title
Unguarded arithmetic underflow in `Router._computeBuy`'s overflow-cap path lets a donation-drained curve be permanently DoS'd - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` caps `tokensOut` at the pair's live `tokenBalance()` when the curve's constant-product output would exceed the real sellable supply, then computes `cappedReserveToken = reserveToken - tokensOut`. This subtraction assumes the hard invariant `tokenBalance() < reserveToken` (the virtual token reserve always exceeds the real balance). That invariant is proven only under ordinary curve buys; a plain ERC20 `Token.transfer` donation of curve tokens directly to the `Pair` — reachable by any unprivileged wallet that first drains most of the curve via a normal buy and then re-donates the tokens it received — pushes `tokenBalance()` above `reserveToken`. The very next buy that trips the overflow-cap branch then underflows `reserveToken - tokensOut` and reverts with an undecodable Solidity Panic instead of the intended `OverflowCapDegenerate()` guard, permanently bricking `Bonding.buy` / `Zap.buy` for that token's curve.

### Finding Description
`Bonding` already recognized and patched this exact donation shape in `previewLtUntilGraduation` — see the explicit donation guard at `Bonding.sol:729` and the regression tests `test_donation_realBalanceExceedsReserveToken` / `test_donation_previewLtUntilGraduation_returnsThresholdLeg` / `test_donation_zapBuyStillSucceeds` in `test/Zap.t.sol`. [4](#0-3)  But the guard was added only to the `Bonding` preview helper; `Router._computeBuy` — the function every actual curve buy executes through — retains the unguarded subtraction:

```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
``` [5](#0-4) 

The protocol's own invariant documentation and tests state that this line is safe only because `tokenBalance() < reserve0` is "a hard property at every state of the curve" that the `cappedReserveToken == 0` guard defends against — but the accompanying fuzz test `test_inv_virtualReserveAlwaysExceedsRealBalance` only exercises buys, never donations. [6](#0-5)  The docs elsewhere confirm donations can only increase `tokenBalance()` and are otherwise treated as a known, tolerated griefing surface (burned at graduation, excluded from the USD trigger), not something that can never happen. [7](#0-6) 

Once `tokenBalance() >= reserveToken`, any buy sized so that the uncapped `tokensOut = reserveToken - k/newReserveAsset` would exceed `realBalance` triggers the cap; `tokensOut` is set to `realBalance`, which is now `>= reserveToken`, so `reserveToken - tokensOut` underflows in Solidity 0.8's checked arithmetic. `Router.buy` — called for every trade from `Bonding._executeBuy` via `Zap.buy` — reverts with an unrecoverable Panic(0x11) rather than any typed protocol error, for every future buy attempt that lands in the cap-binding regime (which becomes essentially every remaining buy on a supply-exhausted curve, since the cap binds precisely on the closing trades that are supposed to trigger graduation).

### Impact Explanation
This freezes the affected token's bonding curve: `Bonding.buy` / `Zap.buy` (the only paths into the curve for ordinary traders) revert once the cap-binding regime is reached, which is exactly the regime needed to trip the supply-side graduation trigger (`tokenBalance() == 0`). Sells still work (per `test_donation_sellsStillWork`), so no funds are directly stolen, but the token can become permanently stuck pre-graduation — unable to reach `IPair.tokenBalance() == 0` via the (now-reverting) capped buy — unless the USD trigger independently fires first via LT price appreciation. Any wallet with a modest amount of capital (enough to buy a large fraction of a fresh curve and donate the proceeds back) can inflict this denial of service on any token, for free beyond gas and the temporary capital used in the drain-and-donate round trip (their donated tokens are eventually burned at graduation, so this is not obviously profitable, but it is a griefing-cost DoS on an unrelated token/curve — matching the CWE-400 class of the reference advisory).

### Likelihood Explanation
High reachability, low cost: the attack requires only (1) a normal `Zap.buy`/`Bonding.buy` to acquire a large slice of curve tokens (over ~25% of `TOTAL_SUPPLY`, per the test's `250_000_000 ether` threshold) and (2) a single unprivileged `Token.transfer(pairAddr, donatedTokens)`. No special role, no timing dependency, and no interaction with graduation, LT pricing, or HyperSwap is needed. The repo's own test suite already demonstrates the precondition (`realBalance > reserveToken`) is trivially reachable; the only missing piece is a subsequent buy that hits the overflow-cap branch under that condition, which the tests never exercise for `Router.buy` directly (only for the already-patched `previewLtUntilGraduation`).

### Recommendation
Mirror the guard added in `Bonding.previewLtUntilGraduation` inside `Router._computeBuy`: when `realBalance >= reserveToken` (donation-inflated real balance), skip the `cappedReserveToken` back-calculation entirely and either revert with a clean, documented error or fall back to a safe capped-buy formula that doesn't assume `reserveToken > realBalance`. Add a fuzz/regression test that stages the same drain-and-donate sequence used in `test/Zap.t.sol`'s `_stageDonationAttack` and then drives a real `Bonding.buy` (not just `previewLtUntilGraduation`) into the overflow-cap branch to confirm it no longer reverts with an unguarded Panic.

### Proof of Concept
1. Attacker calls `Zap.buy` (or `Bonding.buy` directly if they hold `BONDING_ROLE`-gated router access via a normal flow) to acquire >25% of `TOTAL_SUPPLY` in curve tokens, exactly as `_stageDonationAttack` does in `test/Zap.t.sol:944-965`. [8](#0-7) 
2. Attacker calls `Token(tokenAddr).transfer(pairAddr, donatedTokens)`, pushing `IPair.tokenBalance() > reserveToken`, as proven by `test_donation_realBalanceExceedsReserveToken`. [9](#0-8) 
3. Any subsequent trader calls `Zap.buy`/`Bonding.buy` with an amount large enough that the uncapped `tokensOut` computed in `Router._computeBuy` exceeds the (now donation-inflated) `realBalance` — i.e. any buy that would ordinarily bind the overflow cap. `Router._computeBuy` sets `tokensOut = realBalance`, computes `cappedReserveToken = reserveToken - tokensOut`, and since `tokensOut (=realBalance) > reserveToken`, this subtraction underflows and the entire transaction reverts with a bare Panic(0x11), not `OverflowCapDegenerate()`.
4. Every subsequent buy attempt in this regime reverts identically, permanently denying curve-buy access to all traders for that token until/unless the USD trigger independently fires.

### Citations

**File:** packages/contracts/src/Router.sol (L140-147)
```text
        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
```

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

**File:** packages/contracts/src/Bonding.sol (L726-736)
```text
        }

        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;

        return ltUntilSupply < ltUntilThreshold ? ltUntilSupply : ltUntilThreshold;
    }
```

**File:** docs/contracts-scope.md (L70-71)
```markdown
- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```
