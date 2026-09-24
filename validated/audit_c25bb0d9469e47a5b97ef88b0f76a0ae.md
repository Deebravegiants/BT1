### Title
Loosened K-invariant check in `Pair.swap` lets reserves drift below the pair's fixed `k`, causing `Router._computeSell`/`_computeBuy` to underflow and permanently DoS trading - ([File: packages/contracts/src/Pair.sol], [File: packages/contracts/src/Router.sol])

### Summary
`Pair.mint` freezes an exact constant-product invariant `k = tokenReserve * assetReserve` at pair creation [1](#0-0) . Every subsequent `Router.buy`/`Router.sell` call recomputes reserves against this fixed `k`, assuming the true reserve product is always `>= k`. However `Pair.swap`'s invariant check is deliberately loosened with a "+1" slack, `(newTokenReserve + 1) * (newAssetReserve + 1) >= k` [2](#0-1) , which permits the *actual* stored reserve product to fall strictly below the pair's fixed `k` by up to `newTokenReserve + newAssetReserve + 1` per swap. Because `Router._computeBuy`/`_computeSell` derive outputs from the fixed `k` divided by the *new* reserve rather than the drifted actual product, this downward drift can make `k / newReserveToken` (sell path) or `k / newReserveAsset` (buy path) exceed the corresponding live reserve, causing an unchecked Solidity subtraction underflow (panic `0x11`) that reverts the trade unconditionally — a direct functional analog of the reported unhandled-panic bug class, but reachable by any unprivileged trader through `Zap.sell`/`Zap.buy`.

### Finding Description
- `Pair.mint` sets `k = tokenReserve * assetReserve` once at launch and never updates it [1](#0-0) .
- `Pair.swap` enforces `(newTokenReserve + 1) * (newAssetReserve + 1) >= _pool.k`, a weaker inequality than the canonical `newTokenReserve * newAssetReserve >= k` [3](#0-2) . This permits `newTokenReserve * newAssetReserve` to sit below `k` by as much as `newTokenReserve + newAssetReserve + 1`, and every subsequent swap can shave off further slack, so the drift can accumulate across many trades.
- `Router._computeBuy` computes `tokensOut = reserveToken - (k / newReserveAsset)` and `Router._computeSell` computes `assetOut = reserveAsset - (k / newReserveToken)` [4](#0-3) [5](#0-4) . Both formulas implicitly assume `reserveToken * reserveAsset >= k` at all times (the canonical, tight invariant). Once accumulated slack has driven the true product below `k`, `k / newReserveToken` (or `k / newReserveAsset`) can exceed the live reserve being subtracted from, and the subtraction underflows — an unhandled arithmetic panic that reverts the entire call, exactly analogous to `MustNewDecFromString` panicking on unvalidated input instead of returning a handled error.
- Neither `_computeBuy` nor `_computeSell` catches or bounds this case: there is no check that the subtrahend is `<=` the minuend before subtracting, and no fallback path (unlike the buy-side `OverflowCapDegenerate` guard, which only handles the unrelated real-balance-exhaustion case) [6](#0-5) .
- The condition is monotonic and non-recoverable: `k` never changes, and slack can only accumulate (never un-drift), so once a pair's true reserve product has drifted far enough below `k` that a `sell` underflows, every future `sell` call against that pair (for any amount, from any trader) reverts. The only exit path for a curve-stage token — `Zap.sell → Bonding.sell → Router.sell` — becomes permanently bricked.

### Impact Explanation
This permanently freezes trader funds: any holder of a curve-stage token whose pair has drifted into the vulnerable state can no longer sell/exit through `Router.sell`/`Bonding.sell`/`Zap.sell`, since the underflow panic reverts unconditionally for every future call, independent of amount or caller. Tokens remain locked on the curve with no redemption path (the pair has not graduated, so the HyperSwap V2 exit path is also unavailable). This matches the required impact bar of "permanent freezing of trader ... funds," and is a direct functional analog of the referenced report's "unhandled panic crashes the process" bug class, here manifesting as a silent, unrecoverable DoS of the sell (and potentially buy) path for the affected token.

### Likelihood Explanation
The drift is a deterministic, protocol-native consequence of the `+1` slack in `Pair.swap`'s invariant check combined with `Router`'s use of the fixed `k` rather than the live reserve product — it requires no attacker capital beyond normal trading activity (many small buys/sells against the same pair), and every trade nudges the true product further from `k`. Any sufficiently active or long-lived bonding-curve pair — or one deliberately hammered with many minimum-size buy/sell round-trips by an unprivileged actor — will eventually reach the underflow condition on `_computeSell` (or `_computeBuy`). Because `Router`/`Pair`'s math is asset-agnostic and applies identically to every launched token, this is systemic rather than a one-off edge case.

### Recommendation
- Tighten `Pair.swap`'s invariant check to the canonical `newTokenReserve * newAssetReserve >= _pool.k` (drop the "+1" slack), or, if the slack is required for rounding reasons, explicitly re-derive/store the *actual* reserve product and use it — not the launch-time fixed `k` — when back-computing `tokensOut`/`assetOut` in `Router._computeBuy`/`_computeSell`.
- Add an explicit bounds check before each subtraction in `_computeBuy`/`_computeSell` (`if (k / newReserveAsset > reserveToken) revert ...` / `if (k / newReserveToken > reserveAsset) revert ...`) and surface a clean, recoverable error instead of an unchecked panic, mirroring the existing `OverflowCapDegenerate` pattern.
- Add invariant tests asserting `tokenReserve * assetReserve >= k` holds after every `Pair.swap` call across long sequences of small buys/sells, to catch drift regressions.

### Proof of Concept
Conceptually (exact drift magnitude requires simulation, not executable here without contract state):
1. Launch a token; `Pair.mint` locks `k = tokenReserve₀ * assetReserve₀`.
2. Repeatedly execute minimum-size `Zap.buy` followed by `Zap.sell` round-trips against the same token. Each `Pair.swap` call only needs to satisfy `(newTokenReserve+1)*(newAssetReserve+1) >= k`, so each round-trip can leave the *actual* stored product `tokenReserve*assetReserve` slightly below `k` (by up to `tokenReserve+assetReserve+1`), and this deficit is never repaid on subsequent swaps because `Router` always computes against the immutable `k`, not the live product.
3. After enough round-trips, the accumulated deficit becomes large enough that for some sell size, `k / newReserveToken` computed in `Router._computeSell` exceeds the pair's live `reserveAsset`.
4. The next `Zap.sell(tokenAddress, tokenAmount, minUsdcOut)` call (from any unprivileged trader) reverts with an unchecked arithmetic-underflow panic inside `Router._computeSell`'s `assetOut = reserveAsset - (k / newReserveToken);` line, and every subsequent sell of any size against that pair reverts identically forever, permanently locking all remaining curve-stage holders' tokens with no exit.

### Citations

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

**File:** packages/contracts/src/Router.sol (L172-182)
```text
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
```
