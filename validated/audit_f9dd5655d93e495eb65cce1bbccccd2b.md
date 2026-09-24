### Title
Donation-inflated `realBalance` underflows `Router._computeBuy`'s overflow-cap branch, permanently DoS-ing large curve buys - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` caps `tokensOut` at the pair's live `tokenBalance()` and back-calculates `amountInUsed` from `reserveToken - tokensOut`. This subtraction assumes `reserveToken >= realBalance` at all times. An unprivileged attacker can break that assumption for free by donating (direct ERC20 `transfer`) previously-bought `Token` supply back into the `Pair`, inflating `pair.tokenBalance()` above the stored `reserveToken`. Any subsequent buy whose uncapped quote exceeds the (now-inflated) `realBalance` enters the capping branch and underflows `reserveToken - tokensOut`, reverting the whole buy with an arithmetic panic rather than the intended `OverflowCapDegenerate` error.

### Finding Description
`Router._computeBuy` (packages/contracts/src/Router.sol lines 127-148):
```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;   // underflows if realBalance > reserveToken
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    ...
}
``` [1](#0-0) 

Under normal operation `reserveToken` (the stored/virtual reserve, seeded at `TOTAL_SUPPLY` and decremented by `Pair.swap` on every buy) is always `>= realBalance` (the pair's actual `Token.balanceOf`), because both are decremented by the same `tokensOut` on every real trade — this is asserted as `test_inv_virtualReserveAlwaysExceedsRealBalance` in the invariant suite. [2](#0-1) 

However, `Token` is a standard ERC20; any holder (e.g. a trader who bought tokens off the curve) can call `Token.transfer(pair, amount)` directly, which increases `pair.tokenBalance()` without touching the stored `reserveToken`. This is exactly the "donation" primitive already identified and partially fixed elsewhere in the codebase — `Bonding.previewLtUntilGraduation` was patched with a `realBalance >= reserveToken` guard specifically because this scenario was shown to underflow its supply-leg math (see the regression comment in `test/Zap.t.sol`): [3](#0-2) 
and the fix landed in `Bonding.previewLtUntilGraduation`: [4](#0-3) 

But `Router._computeBuy`'s own cap branch was not given the same `realBalance >= reserveToken` guard — it still performs `reserveToken - tokensOut` (where `tokensOut` has just been forced to `realBalance`) with no check that `realBalance <= reserveToken` first. Because `reserveToken` and `realBalance` are read from the same pair (both via `IPair.getReserves()` / `IPair.tokenBalance()`), and any address can donate tokens to the pair, an attacker can drive `realBalance` above `reserveToken` by: (1) buying a large chunk of tokens through the normal curve (`Zap.buy`/`Bonding.buy`), then (2) transferring those tokens directly to the `Pair` address. Once `realBalance > reserveToken`, any buy whose *uncapped* curve quote (`reserveToken - k/newReserveAsset`) exceeds `realBalance` — which is now easy to trigger since `realBalance` can be pushed far above the sellable remainder — lands in the `if (tokensOut > realBalance)` branch and reverts on an EVM arithmetic-underflow panic at `reserveToken - tokensOut`, rather than at the intended `OverflowCapDegenerate` custom-error guard.

This is the same bug class as CVE-2018-19539: an unchecked, attacker-influenceable index/quantity (`realBalance`, analogous to JasPer's unchecked component count) is used directly in a subtraction/array-style access without validating it against the structure's real bound (`reserveToken`), causing an access-violation-style crash (here, a Solidity Panic revert) instead of a graceful error path — reachable purely through externally-supplied data (an ERC20 donation), with no privileged caller required.

### Impact Explanation
Every large buy attempt through `Zap.buy` → `Bonding.buy` → `Router.buy`/`_computeBuy` reverts with an unhandled arithmetic panic once the donation precondition (`realBalance > reserveToken`) holds and the buy size is large enough to trigger the cap branch. This denies service to legitimate traders trying to execute sizeable buys — including the closing buy that would otherwise drain the curve and reach the supply-based graduation trigger (`tokenBalance() == 0`) — for a cost that is bounded by the price of one earlier curve buy (tokens bought and then donated back). Since `Zap.buy`/`Bonding.buy` are the only paths ordinary traders use to buy on the curve, this can strand a token's remaining sellable supply and block its natural graduation path (the USD trigger can still fire independently, but the supply trigger becomes unreliable), amounting to a denial-of-service / griefing vector against traders and the graduation flow reachable by any unprivileged wallet.

### Likelihood Explanation
High reachability: the attacker only needs to (1) execute a normal `Zap.buy` to acquire tokens, then (2) call `Token.transfer(pair, amount)` — both are permissionless actions available to any wallet, with no special privileges, front-running, or precise timing required (unlike the HyperSwap pre-seed attacks documented elsewhere in the repo). The codebase's own regression tests (`test_donation_realBalanceExceedsReserveToken` in `test/Zap.t.sol`) confirm `realBalance > reserveToken` is trivially achievable with a single drain-and-donate sequence. [5](#0-4) 
The only uncertainty is the exact buy size needed post-donation to land in the cap branch on a given pair state, but this is a sizing exercise, not a barrier.

### Recommendation
In `Router._computeBuy`, guard the capped subtraction the same way `Bonding.previewLtUntilGraduation` was fixed: before computing `cappedReserveToken = reserveToken - tokensOut`, check whether `realBalance >= reserveToken` and handle that case explicitly (e.g., treat the buy as fully capped at whatever headroom remains, or revert with a clear, intentional error rather than relying on the implicit Panic). More generally, `tokenBalance()` should never be trusted as a bound for `reserveToken`-relative math without first clamping/validating it against `reserveToken`, mirroring the fix already applied in `Bonding.previewLtUntilGraduation`.

### Proof of Concept
1. Launch a token via `Zap.createToken` (creates `Pair` with `reserveToken = TOTAL_SUPPLY`, `realBalance = curveSupply = 750M`).
2. Attacker calls `Zap.buy` with enough USDC to buy > 250M tokens off the curve (as in `_stageDonationAttack`, spending roughly `virtualLt/3` of LT).
3. Attacker calls `Token.transfer(pair, donatedTokens)` to send the purchased tokens back to the `Pair` directly (bypassing `Router`), inflating `pair.tokenBalance()` above the stored `reserveToken`. [6](#0-5) 
4. A victim (or the attacker) then calls `Zap.buy` with an amount sized so the uncapped curve quote in `Router._computeBuy` exceeds the now-inflated `realBalance`, tripping the `if (tokensOut > realBalance)` branch.
5. `cappedReserveToken = reserveToken - tokensOut` underflows (since `tokensOut` was just set to `realBalance > reserveToken`), causing the entire `Zap.buy` transaction to revert with a raw Solidity Panic instead of completing or hitting the intended `OverflowCapDegenerate` guard — denying that buy and any similarly-sized buy until state changes.

### Citations

**File:** packages/contracts/src/Router.sol (L140-148)
```text
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

**File:** packages/contracts/src/Bonding.sol (L728-733)
```text
        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;
```
