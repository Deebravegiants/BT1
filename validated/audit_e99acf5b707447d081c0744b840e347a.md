Found found `Router.buy` at [1](#0-0) : it calls `factory.getPair(token, asset)` but, unlike `sell` and `graduate` in the same file, never checks `pairAddr == address(0)` before using it.

### Title
Missing `PairNotFound` guard in `Router.buy` lets a call against an unregistered/mismatched pair revert with an undecodable low-level error instead of failing safely - ([File: packages/contracts/src/Router.sol])

### Summary
`Router.sell` and `Router.graduate` both explicitly check `if (pairAddr == address(0)) revert PairNotFound();` after `factory.getPair(...)` before touching the pair [2](#0-1) [3](#0-2) . `Router.buy`, however, omits this check entirely: it resolves `pairAddr` and immediately feeds it into `_computeBuy`, `IERC20(asset).safeTransferFrom`, `IPair(pairAddr).transferToken`, and `IPair(pairAddr).swap` [1](#0-0) .

### Finding Description
This is the same bug class as CVE-2024-53167: a lookup that can legitimately return an "unregistered" / zero-value result is used downstream without gating the subsequent operation on a check that the resource is actually valid. In the kernel bug, `bl_free_device` dereferenced a NULL `block_device` because the code assumed the earlier lookup always succeeded; here, `Router.buy` assumes `factory.getPair(token, asset)` always resolves to a live `Pair`, even though the sibling functions `sell` (line 160) and `graduate` (line 209) in the identical file demonstrate that this lookup is *not* always non-zero and must be explicitly checked.

`Router.buy` is reachable from `Bonding.buy`, which is reachable from any allowlisted `Zap` and ultimately from any unprivileged trader calling `Zap.buy` / `Zap.buyWithPermit` / the seed buy inside `Zap.createToken`. If `pairAddr` is `address(0)` (e.g., a caller reaches `Router.buy` for a `token` whose `Factory.ltFor(token)` / `Factory.getPair` mapping was never populated, or diverges from the token actually passed by an upstream caller), execution proceeds to call `IPair(address(0))...`, which reverts inside low-level calls to the zero address rather than with the clean, decodable `PairNotFound` error the rest of the contract uses.

### Impact Explanation
On its own this is a robustness/defense-in-depth gap rather than a directly exploitable fund-theft path in the current call graph, because `Bonding.buy` is gated to only reach `Router.buy` for tokens it itself registered via `Factory.createPair` at `launch()` time, and `BONDING_ROLE` is trusted to only be held by `Bonding`. However, it violates the pattern established by `sell`/`graduate` in the same contract, and — exactly like the kernel CVE — any future code path, upgrade, or accounting edge case (e.g. a token whose pair registration didn't complete atomically, or a discrepancy between `Bonding`'s internal `tokenInfo[tokenAddress].pair` and `Factory.getPair`) that lets `Router.buy` be invoked before/without a valid pair turns into an undecodable low-level revert deep in `IPair` calls instead of a clean `PairNotFound()` revert. This degrades operability (harder to diagnose, worse UX/error surfacing for traders and the Zap layer) and is a real, provable inconsistency in the production contract, but I could not construct a concrete on-chain path in the current, tightly-gated call graph that lets an unprivileged address actually reach `Router.buy` with a zero `pairAddr` and cause fund loss or freezing — `Bonding.launch`'s `_deployAndSeed` always creates the pair before any buy can occur, and `Router.buy` is only ever invoked through `Bonding._executeBuy` against a `tokenAddress` that has already passed the `TokenNotTrading` / lifecycle checks in `Bonding`.

### Likelihood Explanation
Low likelihood of a standalone fund-loss exploit today, since the existing `Bonding`-level gates (`creatorOf(tokenAddress) == address(0)` checks in `Zap`, lifecycle checks in `Bonding.buy`) prevent an unprivileged caller from reaching `Router.buy` against an unregistered token through the intended entry points. The risk surfaces primarily as a latent defect that a future change to `Bonding`/`Factory` (e.g., decoupling token registration from pair creation, or a race between `launch` and `buy`) could turn into a reachable, unprivileged DoS/undecodable-revert bug — precisely the pattern the kernel advisory warns about ("don't attempt [an operation] for invalid/unregistered [resource]").

### Recommendation
Add the same `if (pairAddr == address(0)) revert PairNotFound();` guard to `Router.buy` immediately after resolving `pairAddr`, mirroring `Router.sell` and `Router.graduate`, so all three privileged entry points fail consistently and decodably rather than relying on incidental protection from caller-side gating.

### Proof of Concept
Not exploitable end-to-end via the current unprivileged entry points (`Zap.buy` → `Bonding.buy` → `Router.buy`) because `Bonding` never calls `Router.buy` for a `tokenAddress` whose pair wasn't created at `launch()`. The finding is a code-inconsistency / defense-in-depth gap provable purely by diffing `Router.buy` against `Router.sell`/`Router.graduate` in [4](#0-3) ; a minimal repro would require a unit test that calls `router.buy(amountIn, unregisteredToken, to)` directly with `BONDING_ROLE` (as `test_graduate_revertsForUnknownPair` already does for `graduate`), which would show `buy` reverting with a low-level panic/empty-data error instead of `Router.PairNotFound`.

### Citations

**File:** packages/contracts/src/Router.sol (L92-211)
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

    /// @notice Tokens in → LT out.
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }

    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }

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
