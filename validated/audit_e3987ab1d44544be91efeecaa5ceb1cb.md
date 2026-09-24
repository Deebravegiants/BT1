### Title
Direct Token donation to `Pair` collapses the virtual-reserve gap and permanently reverts every overflow-capped buy on that curve - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` caps `tokensOut` at the pair's *real* token balance (`pair.tokenBalance()`) whenever a buy would otherwise exceed it, then back-calculates `amountInUsed` from `cappedReserveToken = reserveToken - tokensOut`. This subtraction is only ever safe because `reserveToken` (virtual reserve) is guaranteed to stay a fixed 250M‑token gap above the real balance under normal curve operation. That invariant is not actually enforced on-chain — it is only maintained by the fact that `Pair.swap` moves both numbers in lockstep. A plain `IERC20(token).transfer(pair, amount)` (a direct ERC20 donation of the launched `Token` into `Pair`) increases `tokenBalance()` without touching the internal `_pool.tokenReserve`, shrinking or eliminating that 250M gap. Once the gap is closed, any buy that lands in the overflow-cap branch computes `cappedReserveToken = reserveToken - tokensOut` with `tokensOut >= reserveToken`, which either explicitly reverts (`OverflowCapDegenerate`, when the gap is exactly closed) or silently underflows and reverts with a Solidity arithmetic panic (when the gap goes negative). [1](#0-0) 

### Finding Description
`Pair.tokenReserve` (the virtual reserve that defines `k`) and `pair.tokenBalance()` (the real, live `balanceOf(pair)`) are only kept in the documented 250M-token relationship because every legitimate state transition — `Pair.mint` at launch and `Pair.swap` on every buy/sell — moves both by the same amount: [2](#0-1) 

This is only a soundness property of the *intended call paths*; it is not enforced against an arbitrary `IERC20.transfer` directly to the `Pair` address, which is a plain, unprivileged, externally-callable ERC20 operation (explicitly listed as in-scope: "direct ERC20 transfers of a launched Token ... into Pair"). The project's own tests acknowledge this exact donation vector is dangerous elsewhere in the codebase — a prior fix was applied to `Bonding.previewLtUntilGraduation`'s supply leg specifically because "a TOKEN donation that drives `realBalance > reserveToken` previously underflowed ... cascading into a `Zap.buy` DoS": [3](#0-2) 

However, `Router._computeBuy` — the function that actually executes every real buy through `Router.buy` (and is also reused by the `getAmountOut`/`previewBuy` views) — performs the identical unguarded subtraction:

```
tokensOut = reserveToken - (k / newReserveAsset);
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;   // <-- can underflow/hit 0
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
    amountInUsed = cappedReserveAsset - reserveAsset;
}
``` [4](#0-3) 

The invariant the developers rely on is documented as an assumption, not a guarantee, and the codebase itself notes the branch is only unreachable "in normal operation" — i.e., absent a donation: [5](#0-4) 

An unprivileged attacker who (a) buys or otherwise acquires ≥250M of a token's real supply (up to `curveSupply = 75%` of the 1B total, i.e., up to the full sellable amount) via the normal `Zap.buy`/`Bonding.buy` path, and (b) sends that balance straight to the `Pair` contract with a raw ERC20 `transfer`, drives `pair.tokenBalance() ≥ pair.tokenReserve()`. From that point on, any buy sized to hit the overflow-cap branch (including the exact buy that would otherwise trip the supply-side graduation trigger, `IPair.tokenBalance() == 0`) reverts every time, either with the explicit `OverflowCapDegenerate` error or with an unchecked-arithmetic panic.

### Impact Explanation
This causes a permanent, repeatable denial-of-service on the affected token's curve, mirroring the CVE's "hang or frequently repeatable crash" class:
- The supply-side graduation trigger (`tokenBalance() == 0`) becomes permanently unreachable for that token, because the exact buy that would drain the curve to zero is the one guaranteed to hit the broken cap branch and revert.
- If the paired LT's exchange rate never independently pumps enough to satisfy the USD-side trigger, the token is permanently stuck in `Curve` lifecycle — its remaining real tokens, the 250M `LP_RESERVE` parked in `Bonding`, and any LT raised on the curve are frozen with no path to graduation.
- Even short of full graduation-blocking, every subsequent large/near-final buy attempt on that token reverts, denying legitimate traders access to the tail of the curve — a repeatable crash of the buy path for that specific market, reachable by any single unprivileged wallet with enough capital to acquire and donate the tokens.

This matches the "permanent freezing of trader/creator funds" and "dual graduation trigger" bug classes called out as in-scope.

### Likelihood Explanation
Medium. The attack requires the attacker to control (via legitimate purchase) a large fraction of the curve's real token balance before donating it back — a real capital cost, since tokens must be bought through the curve (spending LT/USDC) rather than minted for free. It is cheapest against thinly-traded or freshly-launched tokens where 250M+ of supply is still cheap to acquire, and is entirely permissionless and reproducible: a plain `transfer` call, no privileged role, no timing dependency, and it permanently damages the specific token's curve once executed.

### Recommendation
Guard the capped-branch subtraction in `Router._computeBuy` (and any other site performing `reserveToken - realBalance`-style arithmetic) against `realBalance >= reserveToken`, e.g. by clamping/saturating instead of relying on the untracked-donation invariant, mirroring the saturating-subtract pattern already applied elsewhere in `Bonding` (`_ltSwapInventory`). Alternatively, sweep/burn any TOKEN donation received directly by the `Pair` before it can affect `tokenBalance()`-based caps, the same way `_prepareGraduationLiquidity` already unconditionally burns donated tokens at graduation time.

### Proof of Concept
1. Launch a token via `Zap.createToken(...)`; note `pair = bonding.getTokenInfo(tokenAddr).pair`, `curveSupply = 750_000_000e18` real tokens initially in `pair`, virtual `reserveToken = 1_000_000_000e18`.
2. Attacker buys through `Zap.buy`/`Bonding.buy` until they hold ≥ `250_000_000e18` of the launched `Token` (this is the maximum size of the virtual-reserve gap, `reserveToken - tokenBalance()`, which starts at exactly 250M and only shrinks as more is bought).
3. Attacker calls `Token(tokenAddr).transfer(pair, 250_000_000e18)` directly — a plain ERC20 transfer, no allowlisting required.
4. `pair.tokenBalance()` now equals or exceeds `pair.getReserves().reserveToken`, while `_pool.tokenReserve` in `Pair` storage is unchanged.
5. Any subsequent buy sized so that uncapped `tokensOut > realBalance` (i.e., any buy that would otherwise land in the overflow-cap branch of `Router._computeBuy`, including the one that would exhaust `tokenBalance()` to trigger supply-side graduation) computes `cappedReserveToken = reserveToken - tokensOut` with `tokensOut >= reserveToken`; the call reverts with `OverflowCapDegenerate()` or an arithmetic-underflow panic, and this repeats for every future attempt at that buy size — the curve's tail becomes permanently un-tradeable and the supply-side graduation path is permanently blocked.

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

**File:** packages/contracts/src/Pair.sol (L65-93)
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

    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }

    function transferToken(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(launchedToken).safeTransfer(recipient, amount);
    }
```

**File:** packages/contracts/test/Zap.t.sol (L939-946)
```text
    // ─── Donation attack regression ──────────────────────────────────────
    // A TOKEN donation that drives `realBalance > reserveToken` previously
    // underflowed `Bonding.previewLtUntilGraduation`'s supply leg,
    // cascading into a `Zap.buy` DoS. Guard added; tests pin the fix.

    function _stageDonationAttack(
        address tokenAddr
    ) internal returns (uint256 drainLtSpent, uint256 donatedTokens) {
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
