### Title
Arithmetic underflow in `canGraduate`/`previewLtUntilGraduation`/`_prepareGraduationLiquidity` from `assetReserve - virtualLtReserve` can permanently brick a curve's buy path - (File: `packages/contracts/src/Bonding.sol`, `packages/contracts/src/Pair.sol`)

### Summary
`Bonding.canGraduate`, `Bonding.previewLtUntilGraduation` and `Bonding._prepareGraduationLiquidity` all compute `realLtRaised`/`ltFromPair` as `assetReserve - _launchTimeVirtualLtReserve(token_, pair)` [1](#0-0) [2](#0-1) . The code implicitly assumes the pair's stored `assetReserve` can never fall below the launch-time virtual LT reserve recovered from `Pair.k() / Token.TOTAL_SUPPLY()` [3](#0-2) . That assumption relies on `Pair.swap`'s K-invariant always holding at least as `tokenReserve*assetReserve == k`, but `Pair.swap` only enforces a weakened check with a `+1` slack on both reserves: `(newTokenReserve + 1) * (newAssetReserve + 1) < k` reverts [4](#0-3) . This lets the true product `tokenReserve * assetReserve` drift strictly below `k` over repeated buy/sell round trips (each sell's `assetOut = reserveAsset - (k / newReserveToken)` rounds in the trader's favor via integer floor division) [5](#0-4) . Enough such round trips can push the stored `assetReserve` below the launch-time virtual LT reserve, causing the unsigned subtraction to underflow and revert.

### Finding Description
At launch, `Pair.mint` sets `_pool.k = tokenReserve_init * assetReserve_init = TOTAL_SUPPLY * virtualLtReserve_init`, and `assetReserve_init` (the launch-time virtual LT reserve) is exactly `virtualLtReserve` [6](#0-5) . `Bonding` later recovers this same value with `_launchTimeVirtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()`, relying on the invariant that `Pair.swap` "never modifies `_pool.k`" and, implicitly, that `assetReserve` never drops below its initial value net of raised LT [7](#0-6) .

However, `Pair.swap`'s invariant check uses a `+1` tolerance on each side of the product:
```solidity
uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
``` [4](#0-3) 
This permits the *actual* `tokenReserve * assetReserve` to end up strictly less than `k`, because the check only requires the `+1`-padded product to clear `k`, not the raw product. Combined with `Router._computeSell`'s floor-rounded `assetOut = reserveAsset - (k / newReserveToken)` [5](#0-4) , each sell can hand the seller marginally more LT than the exact curve price would dictate, silently reducing `assetReserve` relative to the "ideal" curve trajectory. Any unprivileged trader can drive this by repeatedly calling `Zap.buy`/`Zap.sell` (which route to `Bonding.buy`/`Bonding.sell` → `Router.buy`/`Router.sell` → `Pair.swap`) in small round trips. Given enough iterations, the stored `assetReserve` can be pushed below the immutable `virtualLtReserve` recovered from `k`.

Once that happens:
- `canGraduate` underflows and reverts at `realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair)` [1](#0-0) .
- Per the protocol's own documentation, `canGraduate()` is checked "at the end of every buy inside `_executeBuy`" [8](#0-7) , so every subsequent `Bonding.buy` call on that token permanently reverts.
- `previewLtUntilGraduation` and `_prepareGraduationLiquidity` (used by phase-1 `_enterGraduating`) share the identical subtraction and revert the same way [9](#0-8) [2](#0-1) , so the curve can never legitimately graduate either.

The curve is permanently frozen for buys/graduation (sells may remain reachable since they don't call `canGraduate`), which is a denial-of-service that permanently locks the token's ability to raise further funds or graduate to the HyperSwap LP.

### Impact Explanation
This breaks a core invariant the protocol depends on (`assetReserve ≥ virtualLtReserve`) and, once violated, makes `Bonding.buy` unconditionally revert for the affected token because `canGraduate` is invoked at the end of every buy. This is a permanent freezing of the bonding curve's trading/graduation functionality — new buyers can never purchase on the curve again and the token can never reach the dynamic-LP-seeding graduation path, matching the "permanent freezing of trader/creator funds or unbacked payouts" impact bar (funds already deposited become unable to progress to graduation, and future buyers are blocked entirely).

### Likelihood Explanation
The attack requires no privileged role and no capital loss beyond gas — an attacker (or even an unwitting sequence of ordinary traders) can perform many small buy/sell round trips through the public `Zap.buy`/`Zap.sell` entry points. Because the leaked amount per round trip is bounded by integer-rounding (at most ~1 wei of LT per sell) and the `+1` K-slack tolerance, a large number of iterations is needed to fully erode a multi-thousand-dollar-equivalent virtual reserve, but each iteration is cheap (HyperEVM gas) and, due to the favorable rounding, imposes no economic loss on the attacker — only gas cost. This makes it a plausible, low-cost, systematic griefing vector for anyone motivated to permanently disable a specific token's curve, rather than a one-shot exploit.

### Recommendation
- Tighten `Pair.swap`'s K-invariant check to require the raw (unpadded) product `newTokenReserve * newAssetReserve >= _pool.k` rather than a `+1`-padded version, eliminating the systematic rounding drift.
- Make the `assetReserve - virtualLtReserve` (and analogous `tokenReserve`-based) subtractions in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity` saturating (`assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`) so that residual rounding drift produces `0` raised-LT instead of an underflow revert, consistent with the "saturating subtract" pattern already used elsewhere in `Bonding.sol` (e.g. `finalizeGraduation`'s `protectedLT` computation) [10](#0-9) .

### Proof of Concept
Conceptual sequence (exact numeric parameters would need to be derived from the deployed `VIRTUAL_LIQUIDITY_USD`/exchange-rate constants and validated with `forge test`):
1. Launch a token via `Bonding.launch`/`Zap.createToken`, establishing `Pair.k = TOTAL_SUPPLY * virtualLtReserve` and initial `assetReserve = virtualLtReserve`.
2. An unprivileged trader repeatedly calls `Zap.buy` followed by `Zap.sell` for the same small token amount, driving `Bonding.buy`/`Bonding.sell` → `Router.buy`/`Router.sell` → `Pair.swap`. Each sell's floor-rounded `assetOut = reserveAsset - (k / newReserveToken)` extracts marginally more LT than ideal, and `Pair.swap`'s `+1`-padded K check permits the resulting state [11](#0-10) .
3. After sufficient iterations, `assetReserve` (as read via `IPair(pair).getReserves()`) drops below `Pair.k() / Token.TOTAL_SUPPLY()`.
4. The next `Bonding.buy` call reaches the internal `canGraduate` check inside `_executeBuy` and reverts with an arithmetic underflow at `assetReserve - _launchTimeVirtualLtReserve(...)`, permanently bricking further buys on this token's curve.

### Citations

**File:** packages/contracts/src/Bonding.sol (L691-694)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L722-722)
```text
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
```

**File:** packages/contracts/src/Bonding.sol (L1014-1020)
```text
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
```

**File:** packages/contracts/src/Bonding.sol (L1084-1084)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
```

**File:** packages/contracts/src/Bonding.sol (L1098-1119)
```text
    /// @dev Recovers the launch-time virtual LT reserve from immutable
    ///      identities: `Pair._pool.k = tokenReserve_init * assetReserve_init
    ///      = TOTAL_SUPPLY * virtualLtReserve_init` is set ONCE in
    ///      `Pair.mint` and never modified by `Pair.swap` (swap only
    ///      mutates `tokenReserve` / `assetReserve` and asserts K-floor).
    ///      So `Pair.k() / Token.TOTAL_SUPPLY()` returns the exact
    ///      `virtualLtReserve` that was passed to `addInitialLiquidity` at
    ///      launch — for any pair, in any phase, with no storage of our own.
    ///
    ///      Going through this derivation rather than a stored mirror
    ///      eliminates an admin-writable economic-state slot and makes the
    ///      donation-immunity property a pure consequence of the pair's
    ///      already-immutable accounting. The `TOTAL_SUPPLY`-equality check
    ///      in `setTokenImplementation` keeps the divisor consistent across
    ///      impl rotations, so tokens launched under different
    ///      `tokenImplementation` versions still derive the same way.
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
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

**File:** docs/contracts-scope.md (L73-73)
```markdown
Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)
```
