### Title
Zero launch-time virtual LT reserve silently zeroes the pair's K-invariant, letting any trader drain the curve's real LT reserve on the first sell - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._deployAndSeed` derives the pair's launch-time virtual LT reserve as `virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate` and only validates an *upper* bound (`ExchangeRateTooLow` when `virtualLtReserve > type(uint112).max / 4`) plus `exchangeRate != 0`. It never checks that the resulting `virtualLtReserve` itself is non‑zero before seeding the pair. `Pair.mint` then uses `_pool.k = tokenReserve * assetReserve` both as the curve constant *and* as its own "already minted" sentinel (`if (_pool.k != 0) revert AlreadyMinted()`), exactly mirroring the pstore/ram CVE pattern of trusting a single derived/zero-able field as proof of valid initialization instead of validating the individual inputs that produce it. [1](#0-0) [2](#0-1) 

### Finding Description
`_deployAndSeed` computes:

```
virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
...
$.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
``` [3](#0-2) 

`exchangeRate` is read live from the external, unprivileged-selectable BounceTech LT (`IBounceLeveragedToken(ltAddress).exchangeRate()`). Because Solidity integer division truncates, if `exchangeRate` is large enough that `VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate` rounds down to `0`, `virtualLtReserve` becomes `0` — no revert occurs, since the only guards are `exchangeRate == 0` and the *upper*-bound check.

`Router.addInitialLiquidity` forwards this straight into `Pair.mint(totalSupply, 0)`:

```
function mint(uint256 tokenReserve, uint256 assetReserve) external onlyRouter returns (bool) {
    if (_pool.k != 0) revert AlreadyMinted();
    _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
    ...
}
``` [2](#0-1) 

With `assetReserve = 0`, `_pool.k = tokenReserve * 0 = 0`. The pair is now "minted" (reserves recorded, `AlreadyMinted` sentinel permanently satisfied for any hypothetical future call) but its core AMM invariant `k` is permanently zero. This directly corrupts every subsequent trade computation, which relies on `k` for the constant-product math rather than merely as a floor check:

```
// Router._computeBuy
uint256 newReserveAsset = reserveAsset + amountInUsed;
tokensOut = reserveToken - (k / newReserveAsset);   // k=0 -> tokensOut = reserveToken (capped by realBalance)

// Router._computeSell
uint256 newReserveToken = reserveToken + amountIn;
assetOut = reserveAsset - (k / newReserveToken);    // k=0 -> assetOut = reserveAsset (the ENTIRE LT balance)
``` [4](#0-3) [5](#0-4) 

`Pair.swap`'s own K-floor check is likewise defeated: `(newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k` can never be true when `_pool.k == 0`, so the one on-chain safety net for the swap math never binds. [6](#0-5) 

This is the same bug class as the CVE: init logic treats a state as "validly seeded" by checking only a coarse/derived signal (here, `k != 0` as the "already minted" gate, and only an upper-bound check on the seed value) instead of validating the individual field (`assetReserve`/`virtualLtReserve`) that must be non-zero for the invariant to hold — precisely as the pstore fix added a missing check on `start` rather than relying solely on `buffer_size == 0`.

### Impact Explanation
Once a token is launched against an LT whose `exchangeRate()` is high enough to round `virtualLtReserve` to `0`, the curve is permanently mispriced from creation:
- Any `Zap.sell`/`Bonding.sell` call computes `assetOut = reserveAsset - (0/newReserveToken) = reserveAsset`, letting the caller redeem the pair's *entire* real LT balance (all curve-raised funds) for a small amount of tokens sold in — a direct theft of trader/curve-raised funds.
- Any `Zap.buy`/`Bonding.buy` similarly computes `tokensOut = reserveToken - 0`, capped only by the real token balance, handing out the full remaining token supply for far less than the intended curve price — unbacked token payouts and immediate graduation/drain of the curve.
This is a permanent freezing/theft of curve-raised LT funds and an unbacked-token payout, both explicitly in scope as Critical/High-impact classes.

### Likelihood Explanation
Reachable purely through the standard unprivileged `Zap.createToken` → `Bonding.launch` → `_deployAndSeed` path — no privileged role or malicious LT contract is required, only selection of (or the natural appreciation over time of) an LT whose `exchangeRate()` has grown past `VIRTUAL_LIQUIDITY_USD` (i.e., ≥ $3000 in LT terms, scaled by `1e18`) at launch time. Because BounceTech LTs are rebasing/leveraged tokens whose `exchangeRate` is expected to appreciate, a long-lived or highly-leveraged LT reaching that exchange rate is a realistic condition, not a contrived one, and the resulting broken pair is then trivially exploitable by any subsequent trader/attacker.

### Recommendation
In `Bonding._deployAndSeed`, explicitly revert if `virtualLtReserve == 0` (in addition to the existing upper-bound check), and separately harden `Pair.mint`'s "already minted" sentinel so it does not rely on the derived `k` value (e.g., use a dedicated boolean/`minted` flag rather than `k != 0`), so a legitimately zero-valued seed can never be silently mistaken for "not yet minted" nor propagate a zero `k` into the swap math.

### Proof of Concept
1. Register (or wait for) an LT whose `exchangeRate()` ≥ `VIRTUAL_LIQUIDITY_USD * 1e18` (e.g., `3000e18` at 18 decimals) — a normal, unprivileged condition for an appreciated BounceTech LT.
2. Call `Zap.createToken(...)` / `Bonding.launch(...)` for that LT. `_deployAndSeed` computes `virtualLtReserve = 3000e18*1e18 / exchangeRate == 0` (rounds down), passes the `ExchangeRateTooLow` upper-bound check trivially, and calls `router.addInitialLiquidity(token, totalSupply, curveSupply, 0)`.
3. `Pair.mint(totalSupply, 0)` sets `_pool.k = totalSupply * 0 = 0`.
4. Any unprivileged trader calls `Zap.buy`/`Bonding.sell` on the resulting pair; `_computeSell`'s `assetOut = reserveAsset - (0 / newReserveToken)` returns the pair's entire LT balance for a minimal token amount sold in, draining all curve-raised funds.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-495)
```text
        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();

        IERC20(tokenAddr).forceApprove(address($.router), curveSupply);
        // Virtual tokenReserve = full totalSupply; only curveSupply (75%) actually transferred.
        // The launch-time `virtualLtReserve` is recoverable later as
        // `Pair.k() / Token.TOTAL_SUPPLY()`: `Pair.mint` sets `_pool.k =
        // tokenReserve * assetReserve = totalSupply * virtualLtReserve` once
        // and `Pair.swap` never modifies `_pool.k`. That identity is what
        // `_launchTimeVirtualLtReserve` exploits to derive donation-immune
        // raised-LT in `canGraduate` and `_prepareGraduationLiquidity`.
        $.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
    }
```

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
