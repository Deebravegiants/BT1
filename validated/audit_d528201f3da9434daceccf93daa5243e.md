### Title
Donation-inflated real token balance causes an unguarded arithmetic underflow Panic in `Router._computeBuy`, permanently blocking the curve-draining buy needed for supply-trigger graduation - (File: `packages/contracts/src/Router.sol`)

### Summary
`Router._computeBuy` assumes the invariant `pair.tokenBalance() < pair.tokenReserve()` always holds, and only guards the degenerate `cappedReserveToken == 0` case with a custom revert. Any unprivileged wallet that buys curve tokens and donates them straight back into the `Pair` via a plain ERC20 `transfer` can push `tokenBalance()` above the stored virtual `tokenReserve`, which makes `cappedReserveToken = reserveToken - tokensOut` underflow into a raw Solidity Panic(0x11) instead of the intended graceful revert. This is the same bug class as ALPINE-CVE-2021-25215 (BIND): a crafted, permissionless input trips an internal invariant/assertion that the code assumes can never fail, producing an unhandled crash that denies service on a critical path — here, the overflow-capped closing buy that empties the curve and arms the supply-based graduation trigger.

### Finding Description
`Router._computeBuy` (`packages/contracts/src/Router.sol:127-148`) computes:

```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
    amountInUsed = cappedReserveAsset - reserveAsset;
}
``` [1](#0-0) 

This is only safe if `tokenBalance() < reserveToken` always holds — the documented "virtual reserve" invariant maintained by construction at launch (`Pair.reserve0 = totalSupply`, only `curveSupply = 75%` transferred) and preserved by normal buys/sells (both sides move by the same amount). [2](#0-1) 

The protocol's own tests and docs acknowledge that a **direct ERC20 donation of the launched token to the pair** breaks this invariant in the opposite direction (real balance grows without `tokenReserve` growing), and even show that `Bonding.previewLtUntilGraduation` explicitly guards against it:

```solidity
// Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
if (realBalance >= reserveToken) return ltUntilThreshold;
``` [3](#0-2) 

`Router._computeBuy`, which executes the *actual* buy (not just a preview), has no equivalent `>=` guard — it only special-cases `cappedReserveToken == 0`. If a donation pushes `tokenBalance() > reserveToken` (strictly greater, not equal), any buy whose uncapped curve quote exceeds the inflated `realBalance` hits `tokensOut = realBalance`, and `reserveToken - tokensOut` underflows to a bare Solidity Panic rather than the intended `OverflowCapDegenerate` custom error. The AGENTS.md/test commentary asserts "if it ever ceased to hold, that branch would revert with `OverflowCapDegenerate` rather than over-pay" — this claim is only true for the exact-equality edge case, not for the realistic donation-driven inequality case. [4](#0-3) 

Any unprivileged trader can trigger the precondition: buy a sizeable chunk of curve tokens (reducing `reserveToken` and `tokenBalance` by the same amount, preserving the gap), then `transfer()` those tokens straight back to the `Pair` address (bypassing `Router.sell`/`Pair.swap`), which increases `tokenBalance()` without moving `_pool.tokenReserve`. Once the attacker has donated enough previously-bought tokens to shrink the 250M-token gap below zero, `tokenBalance() > tokenReserve()` and the overflow-cap branch is armed to Panic on the next large/overflow-triggering buy — this is exactly the closing buy any trader (or the protocol itself, via `Bonding._executeBuy`) must eventually make to drain the curve and satisfy the supply trigger (`IPair.tokenBalance() == 0`). [5](#0-4) 

### Impact Explanation
For any token whose USD graduation trigger cannot be reached (a flat/bear-market token — the exact scenario the supply trigger exists for), the closing/overflow-capped buy is the *only* path to graduation. [6](#0-5) 
Once the invariant is broken by donation, every buy attempt large enough to hit the overflow cap reverts with an unhandled Panic instead of completing the drain, so the token can never reach `tokenBalance() == 0` and never enters `_enterGraduating`/`finalizeGraduation`. This permanently strands the LT already raised by the curve, the traders' locked-in curve positions, and the creator's 250M `lpReserve` tokens inside `Bonding`/`Pair` with no code path to graduate — a permanent freeze of trader, creator, and protocol funds for the affected token. Any unrelated wallet can inflict this with a single buy + donation, no privileged role required.

### Likelihood Explanation
High. The precondition only requires an unprivileged wallet to (1) buy enough curve tokens to exceed the fixed 250M-token virtual/real gap and (2) `transfer()` them directly back to the known `Pair` address — both are plain, permissionless, single-transaction actions explicitly enumerated as in-scope reachable paths ("direct ERC20 transfers of a launched Token ... into Pair"). No race condition, front-running, or privileged access is needed; the attacker only needs enough capital to buy >250M tokens on a given curve, which is well within reach for a determined griefer, especially on a low-liquidity/newly-launched token.

### Recommendation
Add the same guard `Router._computeBuy` already needs to mirror `Bonding.previewLtUntilGraduation`: before computing `cappedReserveToken = reserveToken - tokensOut`, check `if (tokensOut >= reserveToken) { /* handle degenerate/donation-inflated case explicitly, e.g. revert with a descriptive custom error or clamp safely */ }` instead of relying on the `== 0` branch alone. More robustly, treat `realBalance >= reserveToken` as its own explicit branch (mirroring the `previewLtUntilGraduation` treatment) so the buy path can never underflow regardless of how a donation has skewed `tokenBalance()` relative to the stored virtual reserve, and add a regression test that donates tokens directly to a `Pair` to reduce/invert the gap and then drives a cap-triggering buy, asserting it reverts with a controlled error (or still succeeds) rather than a raw Panic.

### Proof of Concept
1. Launch a token via `Bonding.launch`/`Zap.createToken` (fresh `Pair`, `reserveToken = 1B`, real `tokenBalance() = 750M`, gap = `LP_RESERVE = 250M`).
2. As an unprivileged trader, call `Zap.buy`/`Bonding.buy` repeatedly (or once, sized appropriately) to purchase > 250M of the launched tokens on the curve. This reduces `_pool.tokenReserve` and `tokenBalance()` by the same amount, preserving the 250M gap.
3. From the same wallet, call `Token(tokenAddress).transfer(pairAddr, donatedAmount)` directly (bypassing `Router`/`Bonding` entirely) with `donatedAmount > 250M` worth of the tokens just bought. This increases `pair.tokenBalance()` without touching `_pool.tokenReserve`, flipping the invariant so `tokenBalance() > tokenReserve()`.
4. Have any trader submit a buy sized so the uncapped `_computeBuy` quote (`tokensOut = reserveToken - k/newReserveAsset`) exceeds the now-inflated `realBalance` (i.e., attempt to drain the remaining curve supply, the same buy any trader/keeper would eventually submit to trigger the supply-trigger graduation).
5. Observe the transaction reverts with an unhandled Panic(0x11) (arithmetic underflow) inside `Router._computeBuy`, rather than the custom `OverflowCapDegenerate()` error or a successful capped buy — reproducing the failure mode of `packages/contracts/test/GraduationInvariants.t.sol`'s `test_inv_overflowCap_refundsLt` (`packages/contracts/test/GraduationInvariants.t.sol:330-351`) but with the invariant deliberately broken beforehand via donation, showing the closing buy can never succeed again for this token and the curve/graduation path is permanently bricked. [7](#0-6)

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

**File:** docs/contracts-scope.md (L34-38)
```markdown
**Virtual token reserve.** The pair's `reserve0` is seeded at `totalSupply` (1B) while only `curveSupply = 75%` (750M) of real tokens are actually transferred. The other 250M are held in `Bonding` as `lpReserve`. This virtual-reserve design:

- Extends the curve beyond the sellable supply.
- Gives a deterministic supply trigger (curve exhausts at 750M sold).
- Makes the dynamic-LP-seeding parabola `tokensForLP(sold) = sold·(S−sold)/S` peak at exactly `S/4 = 250M = LP_RESERVE` — so `tokensForLP ≤ lpReserve` is a mathematical invariant, not a runtime guess.
```

**File:** packages/contracts/src/Bonding.sol (L728-729)
```text
        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;
```

**File:** packages/contracts/src/Bonding.sol (L918-932)
```text
    function _executeBuy(
        address tokenHolder,
        address trader,
        uint256 amountIn,
        address tokenAddress
    ) internal returns (uint256 tokensOut, uint256 amountInUsed) {
        (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);

        (uint256 newCurveSupply, uint256 newLtReserve) = _getCurveState(tokenAddress);
        emit Trade(tokenAddress, trader, true, amountInUsed, tokensOut, newCurveSupply, newLtReserve);

        if (canGraduate(tokenAddress)) {
            _enterGraduating(tokenAddress);
        }
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L330-351)
```text
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

**File:** packages/contracts/AGENTS.md (L87-91)
```markdown
- **Virtual token reserve.** At launch, `Pair.reserve0 = totalSupply (1B)` while only `curveSupply = 75%` (750M) of real tokens are transferred to the pair. The other 250M (`LP_RESERVE`) sit in `Bonding` for graduation. This extends the curve beyond the sellable supply, which is what makes dynamic LP seeding work cleanly.
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
- **Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation.
- **Overflow buy cap.** `Router.buy` caps `tokensOut` at the pair's real balance and back-calculates the LT consumed, so the last buy cannot exceed remaining supply. `Zap.buy` returns the unused LT (`ltMinted - amountInUsed`) directly as LT — not redeemed, to avoid re-incurring the LT redemption fee on dust — while unconverted USDC and the fee over-charge are refunded in USDC. `Bonding.buy` returns `(tokensOut, amountInUsed)` for this reason.
```
