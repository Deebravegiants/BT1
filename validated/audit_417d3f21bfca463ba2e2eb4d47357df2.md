Based on my investigation, I found strong evidence of a reachable arithmetic-underflow DoS analog in `Router._computeBuy`'s overflow cap path, related to (but distinct from) an already-patched donation issue in `Bonding.previewLtUntilGraduation`.

### Title
Attacker-donated tokens can permanently revert `Router.buy`'s overflow-cap path, freezing the ability to fill/graduate a curve - (File: packages/contracts/src/Router.sol)

### Summary
`Router._computeBuy` caps `tokensOut` at `pair.tokenBalance()` (the pair's real ERC20 balance) whenever the uncapped constant-product quote would exceed it, then back-calculates `amountInUsed` from `cappedReserveToken = reserveToken - tokensOut` [1](#0-0) . This subtraction assumes `reserveToken >= realBalance` always holds. The codebase's own tests document that a donation attack can drive `realBalance > reserveToken` [2](#0-1) , and that this previously "underflowed `Bonding.previewLtUntilGraduation`'s supply leg, cascading into a `Zap.buy` DoS," for which "guard added; tests pin the fix" [3](#0-2) . That fix note only speaks to `Bonding.previewLtUntilGraduation` (a preview/view helper) — I could not confirm, within the available index, that an equivalent guard was added inside `Router._computeBuy` itself for the identical `reserveToken - tokensOut` subtraction on the real trade-execution path used by `Router.buy` and `Zap.buy`.

### Finding Description
An unprivileged trader can:
1. Buy on the curve to accumulate `Token` balance via `Zap.buy`/`Bonding.buy`.
2. Directly `transfer()` those `Token`s to the `Pair` address (a permitted, unprivileged ERC20 transfer), inflating `pair.tokenBalance()` above the stored `reserveToken` — exactly the shape proven feasible in `test_donation_realBalanceExceedsReserveToken` [4](#0-3) .
3. Submit (or have any subsequent trader submit) a buy large enough to trip the overflow cap. In `_computeBuy`, once `tokensOut > realBalance` is capped to `tokensOut = realBalance`, the line `uint256 cappedReserveToken = reserveToken - tokensOut;` underflows because `realBalance > reserveToken` [5](#0-4) . Solidity 0.8.24's checked arithmetic reverts the whole call.

Because this cap path is exercised by every buy that would otherwise exhaust the real curve supply — including the supply-trigger graduation buy — this can make it impossible to ever land the closing/oversized buy on a poisoned token, permanently freezing that token's ability to reach the supply-based graduation trigger and DoS'ing all large buys against it.

### Impact Explanation
This is a permanent-freezing / griefing bug on trader and creator funds: a token stuck unable to graduate via the supply trigger leaves creator/trader capital locked in the curve pair indefinitely (subject to the USD trigger eventually firing, which may never happen in a flat/bear LT-rate scenario — precisely the scenario the supply trigger exists to handle, per `docs/contracts-scope.md` [6](#0-5) ). This matches the "permanent freezing of trader, creator or LP funds" acceptance bar.

### Likelihood Explanation
Reachable by a single unprivileged wallet using only `Zap.buy`/`Bonding.buy` (to acquire tokens) and a plain ERC20 `transfer` of the launched `Token` into the `Pair` — both explicitly in-scope reachable primitives. The precondition (`realBalance > reserveToken`) is already demonstrated achievable on-chain by the project's own regression test [7](#0-6) ; only the downstream consequence in `Router._computeBuy` (as opposed to `Bonding.previewLtUntilGraduation`) is unverified as fixed.

### Recommendation
In `Router._computeBuy`, guard the cap branch the same way the (apparently already-fixed) `previewLtUntilGraduation` guard does: clamp/floor `tokensOut` to `min(realBalance, reserveToken)` before computing `cappedReserveToken`, or explicitly branch when `realBalance >= reserveToken` to avoid the subtraction underflowing, treating any tokens above `reserveToken` as un-sellable-via-cap (consistent with the "virtual reserve always exceeds real balance" invariant the tests otherwise rely on) [8](#0-7) .

### Proof of Concept
1. Launch a token via `Zap.createToken`.
2. As `trader`, `Zap.buy` a chunk of tokens.
3. `Token.transfer(pairAddr, tokensHeld)` to donate tokens directly into the `Pair`, reproducing `_stageDonationAttack` from `test/Zap.t.sol` (lines 944-965) so that `pair.tokenBalance() > reserveToken` [9](#0-8) .
4. Any subsequent buy sized to trip `Router._computeBuy`'s overflow-cap branch (`tokensOut > realBalance`) reverts on the `reserveToken - tokensOut` underflow at [5](#0-4) , DoS'ing the closing/graduation buy for that token.

**Caveat**: I was not able to fully confirm, within the indexed portions of `Bonding.sol` and `Router.sol`, whether a subsequent patch already guards `_computeBuy` itself against this exact underflow (only the `previewLtUntilGraduation` fix was directly evidenced by the tests I found). A Devin session with full repository access would be needed to definitively confirm whether `Router._computeBuy`'s cap-branch subtraction is still exploitable in the current code or has since been hardened alongside the `Bonding` preview fix.

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

**File:** packages/contracts/test/Zap.t.sol (L939-977)
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

**File:** docs/contracts-scope.md (L71-71)
```markdown
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-362)
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
```
