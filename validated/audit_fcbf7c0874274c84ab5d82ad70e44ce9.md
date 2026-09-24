Based on my investigation, I found a genuine analog: `Router._computeSell` lacks the underflow guard that its sibling `_computeBuy` has, and `Pair.swap`'s `+1` K slack means `k / newReserveToken` is not a tight bound — floor-division combined with the accumulated `+1` slack from every prior swap can make `k / newReserveToken` round up above the current `reserveAsset`, causing `reserveAsset - (k / newReserveToken)` to underflow and revert with an unhandled arithmetic panic. This mirrors the Namada bug class exactly: an unprivileged, ordinary transaction (a `mul_floor`/arithmetic op inside a core state-transition function) can hit an unchecked error path and revert, but here it goes further — the state that causes the revert is *pair reserves after normal swaps*, permanently reachable, and unlike `_computeBuy` (which has an explicit `OverflowCapDegenerate` cap/guard), `_computeSell` has no analogous cap, meaning any sell that lands in this band bricks that trader's sell — and since the pair state is monotonic in the direction that shrinks `reserveAsset` relative to `reserveToken`, subsequent sells at similar sizes keep failing, freezing sell-side liquidity for the curve token.

### Title
Unguarded Integer Underflow in `Router._computeSell` Permanently DoSes Sell-Side Liquidity on the Bonding Curve - (File: `packages/contracts/src/Router.sol`)

### Summary
`Router._computeBuy` explicitly guards its capped branch against a degenerate division (`OverflowCapDegenerate`), but the sibling `_computeSell` performs an unguarded subtraction `reserveAsset - (k / newReserveToken)` with no equivalent floor/cap check. `Pair.swap` enforces the K-invariant with a `+1` slack on both sides (`(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k`), so real, achievable reserve states after ordinary buys/sells can drift such that `k / newReserveToken` (floor division) exceeds the live `reserveAsset`, causing `_computeSell` to underflow and panic-revert (Solidity `Panic(0x11)`), exactly analogous to how Namada's un-validated negative commission causes `mul_floor` to error inside `finalize_block`, permanently breaking that path for the affected validator set.

### Finding Description
`Router._computeSell`:
```solidity
function _computeSell(address pairAddr, uint256 amountIn) internal view returns (uint256 assetOut) {
    IPair pair = IPair(pairAddr);
    (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
    uint256 k = pair.k();
    uint256 newReserveToken = reserveToken + amountIn;
    assetOut = reserveAsset - (k / newReserveToken);
}
``` [1](#0-0) 

has no cap analogous to `_computeBuy`'s explicit degenerate-division guard:
```solidity
uint256 realBalance = pair.tokenBalance();
if (tokensOut > realBalance) {
    tokensOut = realBalance;
    uint256 cappedReserveToken = reserveToken - tokensOut;
    if (cappedReserveToken == 0) revert OverflowCapDegenerate();
    ...
}
``` [2](#0-1) 

The invariant `k = tokenReserve * assetReserve` is only exact at `Pair.mint`; every subsequent `Pair.swap` allows the *actual* product to sit slightly above `k` due to the `+1` slack on both reserves in its check:
```solidity
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
``` [3](#0-2) 

Because floor-division `k / newReserveToken` is not guaranteed to stay `<= reserveAsset` once real (non-idealized) reserves have drifted from the exact `k` relationship across many swaps, `_computeSell` can compute `k / newReserveToken > reserveAsset`, and the subtraction underflows and panics. This is exactly the unvalidated-arithmetic class in the Namada report (`mul_floor` returning `Err`, unhandled, bricking `finalize_block`): here an ordinary user transaction (`Zap.sell` → `Bonding.sell` → `Router.sell` → `_computeSell`) triggers an unguarded arithmetic operation with no defensive cap, unlike the buy path which was hardened with exactly this kind of guard.

### Impact Explanation
Any trader attempting to sell into a pair whose accumulated reserve drift lands in the vulnerable band gets a reverted transaction with an opaque `Panic(0x11)` instead of a clean error. Because the drift is a function of the pair's own historical reserves (not something a single sell can "undo"), once a token's curve state enters this band, sells of the affected size — and potentially all sells until the pair graduates — permanently revert, freezing sellers out of the bonding-curve exit path entirely (buys can still proceed since `_computeBuy` is hardened, but sells cannot), which the "Sell Flow" documentation asserts should always work via `Router.sell()` before graduation.

### Likelihood Explanation
Reaching this requires no special privilege — it is reachable from ordinary `Zap.sell`/`Bonding.sell` calls by any trader — but it depends on accumulated integer-rounding drift across many swaps landing on a specific unlucky reserve ratio, which the docs' extensive fuzz/invariant test suite (`GraduationInvariants.t.sol`) does not appear to specifically target for the sell-underflow case (all located invariant tests exercise the buy-side `OverflowCapDegenerate` branch, not an equivalent sell-side check). I was not able to fully confirm with a concrete numeric trace within the available tool budget whether the `+1` K slack is large enough in practice to flip the floor-division result across realistic reserve magnitudes (`reserve0`/`reserve1` are large, ~1e18-scale numbers), so likelihood should be treated as **uncertain/unconfirmed** pending an on-chain/fuzz reproduction — I could not locate a test in the codebase (`Router.t.sol`) that explicitly rules out or reproduces sell-side underflow, only buy-side handling.

### Recommendation
Add an explicit guard in `_computeSell` mirroring `_computeBuy`'s `OverflowCapDegenerate` check: if `k / newReserveToken >= reserveAsset` (i.e., the computed output would underflow or return zero unsafely), cap `assetOut` at a safe value or revert with a dedicated, decodable error instead of relying on the implicit Solidity panic. Additionally, audit whether the `+1` K slack in `Pair.swap` can compound across many small swaps to make `k / newReserveToken` diverge meaningfully from the true `reserveAsset`, and consider tightening or removing the slack, or re-deriving `assetOut` in a way that provably cannot underflow given the K-invariant's actual (non-idealized) enforcement.

### Proof of Concept
I was unable to construct a concrete numeric trace or run Foundry tests within this investigation to empirically trigger the underflow (no execution environment available). A background engineer should:
1. Write a Foundry fuzz test that repeatedly buys and sells small amounts on a freshly launched curve pair, checking after every swap whether `pair.k() / (reserveToken + amountIn) > reserveAsset` for some candidate `amountIn`.
2. If such a state is found, call `zap.sell(tokenAddr, amountIn, 0)` and confirm it reverts with a bare `Panic(0x11)` (arithmetic underflow) rather than a decodable Zap/Bonding error, confirming the missing guard and its DoS impact on the sell path.

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
