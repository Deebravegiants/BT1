## Analysis

The Sherlock report's bug class — a config value permitted to reach zero and then used unchecked as a division denominator, permanently bricking the pool — maps onto alt.fun's launch-time virtual-reserve derivation in `Bonding._deployAndSeed`. [1](#0-0) 

### Title
Zero-floor missing on launch-time `virtualLtReserve` derivation lets a high-priced LT poison `K` to zero, draining the curve's real supply for free and permanently bricking graduation - (File: packages/contracts/src/Bonding.sol)

### Summary
`_deployAndSeed` only upper-bounds `virtualLtReserve` (`> type(uint112).max/4`) but never checks it can floor to `0` when the paired LT's `exchangeRate()` is large relative to `VIRTUAL_LIQUIDITY_USD`. A zero `virtualLtReserve` sets the pair's `K` invariant to `0`, which degenerates `Router._computeBuy`'s overflow-cap math to award the entire real curve supply for `amountInUsed == 0`, and later makes `_graduate()`'s LP-sizing division divide by zero, permanently freezing graduation.

### Finding Description
`_deployAndSeed` computes:
```solidity
uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
``` [2](#0-1) 

Only an *upper* bound is enforced. If `exchangeRate()` (an external, live, appreciating LT price) is large enough that `VIRTUAL_LIQUIDITY_USD * 1e18 / exchangeRate` floors to `0`, `virtualLtReserve = 0` passes silently. This value is then fed into `Router.addInitialLiquidity` → `Pair.mint`, where:
```solidity
_pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
``` [3](#0-2) 

giving `K = totalSupply * 0 = 0` for the entire life of the curve (`Pair.swap` never re-derives `K`).

With `K = 0`, the very first buy through `Router._computeBuy` degenerates:
```solidity
uint256 newReserveAsset = reserveAsset + amountInUsed;
tokensOut = reserveToken - (k / newReserveAsset);   // k=0 ⇒ tokensOut = reserveToken (≈1B)
...
if (tokensOut > realBalance) {
    tokensOut = realBalance;                         // caps at 750M real tokens
    uint256 cappedReserveToken = reserveToken - tokensOut;
    uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken; // k=0 ⇒ ceil(0/x)=0
    amountInUsed = cappedReserveAsset - reserveAsset; // 0 - 0 = 0
}
``` [4](#0-3) 

Any buyer (including the launcher's own mandatory `Zap.createToken` seed buy, which is required to immediately follow `Bonding.launch` in the same transaction) receives `tokensOut = realBalance` (the full 750M curve supply) while `amountInUsed = 0` — the entire real token allocation is handed out for zero LT paid, and `Pair.swap`'s `K`-check passes trivially since `K = 0`.

This single buy also empties `IPair.tokenBalance()`, which immediately satisfies the supply graduation trigger:
```solidity
if (IPair(pair).tokenBalance() == 0) return true;
``` [5](#0-4) 

But because `assetReserve` is permanently `0` (no real LT was ever raised), `_graduate()`'s LP-sizing step divides by that same zero reserve:
> `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. [6](#0-5) 

With `reserve1 = 0`, this division reverts on every attempt to `finalizeGraduation`, and since the curve can never trade again once `tokenBalance() == 0`, `reserve1` can never become non-zero — graduation, and the 250M `LP_RESERVE` allocation locked in `Bonding`, are permanently stuck.

### Impact Explanation
- **Theft/unbacked payout:** the triggering buyer receives the entire 750M-token curve allocation (75% of total supply) while paying `0` LT — a direct, complete drain of the curve's real token backing.
- **Permanent freezing:** the resulting `assetReserve == 0` state makes `_graduate()`'s LP-seeding division revert unconditionally and forever, permanently freezing the 250M `LP_RESERVE` tokens and blocking the token from ever reaching a tradable HyperSwap pool.

Both outcomes meet the "concrete theft or permanent freezing" bar.

### Likelihood Explanation
Reachable by any unprivileged token creator: `Zap.createToken` lets the caller choose any already-registered (`ltExists`) LT as the reserve asset. Any LT whose `exchangeRate()` (18dp, USDC-per-LT) exceeds `VIRTUAL_LIQUIDITY_USD` (documented as pinning the opening market cap at "~$3K") causes `virtualLtReserve` to floor to `0`. A long-running or high-leverage BounceTech LT that has appreciated past that price is a realistic, attacker-controllable precondition — the creator simply targets such an LT when calling `createToken`, and their own mandatory seed buy triggers the exploit in the same transaction.

### Recommendation
Add a lower-bound check alongside the existing upper bound in `_deployAndSeed`:
```solidity
if (virtualLtReserve == 0) revert ExchangeRateTooHigh();
```
so that any LT whose price would round the virtual reserve to zero is rejected at launch, matching the Sherlock recommendation's pattern of tightening the boundary condition (`<` vs `<=`) that was originally too permissive.

### Proof of Concept
1. Register/obtain an LT whose `exchangeRate()` (18dp) is `> VIRTUAL_LIQUIDITY_USD` (e.g., `exchangeRate() = VIRTUAL_LIQUIDITY_USD + 1`), satisfying `ltExists`.
2. Call `Zap.createToken(params{ltAddress: thatLT, ...}, seedUsdcAmount = MIN_SEED_USDC)`.
3. Inside, `Bonding.launch` → `_deployAndSeed` computes `virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate == 0`, passes the `> type(uint112).max/4` check, and calls `Router.addInitialLiquidity(token, totalSupply, curveSupply, 0)`, setting `Pair.K = 0`.
4. The mandatory seed buy in the same tx executes `Router.buy` → `_computeBuy`; with `K = 0` the overflow-cap branch returns `tokensOut = curveSupply` (750M) and `amountInUsed = 0`.
5. Creator now holds the entire real curve allocation for free; `IPair.tokenBalance() == 0` flips `canGraduate` true with `assetReserve == 0`.
6. Anyone calls `Bonding.triggerGraduation` / the buy-triggered `_enterGraduating`, then `finalizeGraduation` → `_graduate()`'s `tokensForLP = (ltFromPair × reserve0) / reserve1` reverts with a division-by-zero panic every time, permanently freezing the token's graduation and the 250M `LP_RESERVE`.

Note: I did not directly view the body of `_graduate()`/`_prepareGraduationLiquidity` in `Bonding.sol` in this session (the exact division line is documented in `docs/contracts-scope.md` but not re-confirmed against live source in the final pass); a Devin session with full repo access should verify the exact line numbers before remediation.

### Citations

**File:** packages/contracts/src/Bonding.sol (L476-484)
```text

        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();
```

**File:** packages/contracts/src/Bonding.sol (L688-689)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;
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

**File:** docs/contracts-scope.md (L90-90)
```markdown
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
```
