### Title
Cumulative K-invariant slack in `Pair.swap`'s `+1` check can underflow `Router`'s reserve math and permanently DoS a curve — ([File: packages/contracts/src/Pair.sol])

### Summary
CVE-2023-31919 is an assertion-failure/DoS bug class: an internal invariant check that is supposed to guarantee consistency instead permits (or fails to fully police) a state that later trips an unguarded assertion, crashing the component. The alt.fun analog is `Pair.swap`'s K-invariant check, which is deliberately weaker than a true constant-product guarantee (`(newTokenReserve + 1) * (newAssetReserve + 1) < k` reverts, rather than `newTokenReserve * newAssetReserve < k`), letting stored reserves drift below the mathematically "true" curve after repeated buy/sell round trips. `Router._computeBuy` / `_computeSell` then perform unguarded subtractions (`reserveToken - (k / newReserveAsset)`, `reserveAsset - (k / newReserveToken)`) that assume the stored reserves never fall below what `k` implies. Once the drift accumulates past that assumption, any ordinary `Bonding.buy`/`sell` call on the affected token reverts with a Solidity Panic (arithmetic underflow), and — because the drifted state persists in storage — the token's curve becomes permanently untradeable with no recovery path (funds locked in the `Pair` until an upgrade).

### Finding Description
`Pair.swap` enforces:
```solidity
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
``` [1](#0-0) 

This `+1` slack (intended to avoid off-by-one false reverts) means a swap is accepted even when the *actual* product `newTokenReserve * newAssetReserve` is strictly less than `_pool.k`, by up to roughly `newTokenReserve + newAssetReserve` per swap. `Router` computes the amounts it passes to `swap` from the *stored* reserves and the *fixed* `k`, not from a re-derived "true" product:

```solidity
uint256 newReserveAsset = reserveAsset + amountInUsed;
tokensOut = reserveToken - (k / newReserveAsset);
...
uint256 newReserveToken = reserveToken + amountIn;
assetOut = reserveAsset - (k / newReserveToken);
``` [2](#0-1) [3](#0-2) 

Both of these subtractions implicitly assume `k / newReserveX <= reserveY`, i.e. that the stored reserves still satisfy the *exact* `tokenReserve * assetReserve >= k` relationship the pair was minted with (`k = tokenReserve * assetReserve` at `Pair.mint`). [4](#0-3) 

Because `Pair.swap` only enforces the weaker `(x+1)(y+1) >= k` bound, each ordinary buy/sell round trip can shave the true product `tokenReserve * assetReserve` down slightly below `k` and this loss is compounding: nothing in `Router` or `Pair` ever restores the exact product, and nothing prevents an unprivileged trader from executing many small buy/sell pairs (`Bonding.buy` / `Bonding.sell`, reachable by any address once trading is open) purely to walk the stored reserves down through repeated `+1`-slack swaps. Once the accumulated drift is large enough that `k / newReserveX > reserveY` for some legitimate trade size, the subtraction underflows and reverts with a raw Solidity Panic rather than a handled error — this is the direct structural analog of `jcontext_raise_exception`'s assertion failure: an internal invariant (the AMM's constant-product accounting) that the code assumes always holds, but that the actual guard (`Pair.swap`'s `+1`-slack check) does not fully police.

Once a given token's `Pair` reaches this drifted state, every subsequent `buy`/`sell` on that token calls the same unguarded `_computeBuy`/`_computeSell` arithmetic against the same drifted stored reserves, so the underflow is deterministic and permanent for that token — there is no repair path (`Router`/`Pair` expose no rebalancing or reset function, and `Bonding` never calls one), leaving the token's remaining real-token and real-LT balances permanently stranded inside the curve `Pair`.

### Impact Explanation
This satisfies the "permanent freezing of trader/creator funds" bar: any unsold tokens and raised LT sitting in a `Pair` that reaches the drifted state become permanently untradeable — `Bonding.buy`/`sell` (the only paths to move value in or out of the curve pre-graduation) both revert unconditionally once the Panic condition is met, and the token can never reach the supply or USD graduation trigger either, since both graduation triggers are computed from the same drifted reserves/`Router` math. Traders holding the token before the freeze cannot sell out, and value already raised on the curve (LT) is stuck in the `Pair` with `BONDING_ROLE`-gated access only through the now-broken `Router`.

### Likelihood Explanation
The precondition is only that an unprivileged trader executes enough ordinary buy/sell pairs on the curve to accumulate slack past the point where a normal-sized trade underflows. Every leg uses standard `Bonding.buy` / `Bonding.sell`, both callable by any address (subject only to the anti-snipe launch delay, which lapses after 3 blocks). No admin privilege, no LT-specific behavior, and no HyperSwap interaction is required — this is purely curve-internal AMM math, reachable at any point during a token's `Curve` lifecycle.

### Recommendation
Tighten `Pair.swap`'s K-invariant check to the exact constant-product bound (`newTokenReserve * newAssetReserve >= k`, or an explicitly-bounded, non-compounding slack) so stored reserves can never drift below the value `k` guarantees, and add explicit bounds/guards in `Router._computeBuy` / `_computeSell` (e.g., saturating subtraction with a hard revert path distinct from a raw Panic, or an assertion that `k / newReserveX <= reserveY` before subtracting) so any future invariant violation fails safely and observably rather than permanently bricking the curve.

### Proof of Concept
Conceptual repro (would need to be run against the Foundry suite to confirm exact iteration count):
1. Launch a token via `Bonding.launch` and let trading open.
2. Repeatedly call `Bonding.buy(smallAmount, token, trader)` immediately followed by `Bonding.sell(receivedTokens, token, trader)` from the same unprivileged trader address, many times, each round trip nudging `_pool.tokenReserve` / `_pool.assetReserve` slightly below the value implied by the immutable `_pool.k` (permitted by `Pair.swap`'s `(x+1)(y+1) >= k` check rather than `x*y >= k`).
3. After sufficient iterations, call `Bonding.buy` or `Bonding.sell` with any ordinary amount and observe a raw arithmetic-underflow revert (Panic `0x11`) from `Router._computeBuy` / `_computeSell`'s `reserveToken - (k / newReserveAsset)` / `reserveAsset - (k / newReserveToken)`.
4. Confirm the token's curve is now permanently stuck in `Lifecycle.Curve` — every subsequent `buy`/`sell` on that token reverts identically, with no recovery function available in `Router`, `Pair`, or `Bonding`. [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** packages/contracts/src/Pair.sol (L58-61)
```text
    ) external onlyRouter returns (bool) {
        if (_pool.k != 0) revert AlreadyMinted();
        _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
        emit Mint(tokenReserve, assetReserve);
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
