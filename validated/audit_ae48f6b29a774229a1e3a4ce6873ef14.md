### Title
Unvalidated arithmetic on `assetReserve - virtualLtReserve` reachable via the K-invariant's rounding slack causes a permanent underflow revert, DoSing buy/sell/graduation on the curve - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.canGraduate` / `previewLtUntilGraduation` / `_prepareGraduationLiquidity` all compute `realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair)` without validating that the live, rounding-affected `assetReserve` can never fall below the immutable `virtualLtReserve` floor it is being subtracted from. `_launchTimeVirtualLtReserve` is derived from the fixed `Pair.k()` [1](#0-0) , while the live `assetReserve` is mutated every trade only under `Pair.swap`'s `(newTokenReserve+1)*(newAssetReserve+1) >= k` check, which is a **rounded, +1-slack invariant**, not an exact one [2](#0-1) . This mirrors CVE-2019-10895's root cause: a parser (here, `canGraduate`'s reserve math) trusts a derived field to satisfy an implicit bound without validating it, and a boundary-condition input crashes the code path instead of failing gracefully.

### Finding Description
`canGraduate` is called on the hot path of every `Bonding.buy` and `Bonding.sell` (via `_executeBuy`/`sell`) and by the permissionless `triggerGraduation` [3](#0-2) . Its USD leg does:
```
uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
```
`_launchTimeVirtualLtReserve` is `k() / TOTAL_SUPPLY()`, an exact, immutable value fixed at `Pair.mint` [4](#0-3) . `assetReserve`, however, is only constrained per-trade by `Pair.swap`'s check:
```
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
```
This allows the *actual* stored product `tokenReserve * assetReserve` to be strictly **less** than `k` by up to `tokenReserve + assetReserve` per trade (rounding slack), because the check is evaluated against the padded `(+1, +1)` terms rather than the true product [5](#0-4) . Sells increase `tokenReserve` back toward `TOTAL_SUPPLY` (the virtual ceiling) while decreasing `assetReserve`; near that ceiling the K-check's floor on `assetReserve` converges to `virtualLtReserve` only up to this same rounding slack, meaning `assetReserve` can legitimately be pushed to a value marginally **below** `virtualLtReserve` by an ordinary, non-privileged sell that fully satisfies `Pair.swap`'s own check.

Once that happens, `assetReserve - _launchTimeVirtualLtReserve(...)` underflows and panics (`Panic(0x11)`), in:
- `canGraduate` (line 692) — called by every `buy`/`sell`/`triggerGraduation`,
- `previewLtUntilGraduation` (line 722) — called by every `Zap._executeBuy` on curve tokens to pre-size the LT mint [6](#0-5) ,
- `_prepareGraduationLiquidity` (line 1084), reachable from `_enterGraduating`.

Because `canGraduate`/`previewLtUntilGraduation` are unconditionally evaluated inside `Bonding.buy`, `Bonding.sell`, and `Zap._buyInternal`/`_sellInternal` with no `try/catch`, a single reserve state satisfying `assetReserve < virtualLtReserve` (by even 1 wei) makes **every subsequent buy and sell on that token's curve revert**, and `triggerGraduation` also reverts (`NotGraduatable` is never reached — the underflow panics first inside `canGraduate`). The token is permanently stuck in `Lifecycle.Curve` with no way to trade or graduate, freezing all funds already committed to that curve (creator's seed, all buyers' capital) with no recovery path, since none of these three call sites validate the subtraction or provide a fallback.

### Impact Explanation
This is a permanent freeze of funds for every trader/creator holding a position in the affected curve token: `Zap.buy`/`Zap.sell` (the only user-facing entry points pre-graduation) revert unconditionally once the underflow condition is hit, and `triggerGraduation` (the only path to unstick a `Curve`-stage token) also reverts because it calls the same `canGraduate` before its own explicit check. There is no owner/admin recovery function for a token stuck in `Lifecycle.Curve` — `Bonding` exposes no way to force-graduate or patch `assetReserve`. This satisfies "permanent freezing of trader, creator... funds" from the validation criteria.

### Likelihood Explanation
Reachable by any unprivileged trader submitting ordinary `Zap.sell` calls near the point where `tokenReserve` approaches `TOTAL_SUPPLY` (i.e., most curve tokens sold back into the pool) — no special privilege, upgrade, or off-chain component is required. The rounding slack that creates the underflow window is a direct, deterministic consequence of `Pair.swap`'s `(x+1)(y+1) >= k` check as written, so the condition is reachable purely through repeated ordinary sell traffic pushing reserves toward the boundary; an attacker can accelerate this deliberately by sequencing buys/sells to maximize the accumulated rounding drift before triggering the final sell.

### Recommendation
Replace the unchecked subtraction with a saturating computation (mirroring the pattern already used defensively elsewhere in `Bonding`, e.g. `finalizeGraduation`'s `ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0` at `Bonding.sol:1020`):
```solidity
uint256 virtualLt = _launchTimeVirtualLtReserve(token_, pair);
uint256 realLtRaised = assetReserve > virtualLt ? assetReserve - virtualLt : 0;
```
in `canGraduate`, `previewLtUntilGraduation`, and `_prepareGraduationLiquidity`. Additionally, tighten `Pair.swap`'s invariant check (or clamp `assetReserve` to never fall below the recoverable `virtualLtReserve`) so the rounding slack cannot push the live reserve below the value other contracts treat as an immutable floor.

### Proof of Concept
Exact PoC requires simulating `Pair`'s per-trade rounding drift across many sequential curve trades to reach the boundary where `assetReserve` dips below `virtualLtReserve` (derived as `k()/TOTAL_SUPPLY()`), which needs concrete numeric fuzzing/foundry execution against the deployed `Router._computeBuy`/`_computeSell` rounding behavior that I could not fully execute in this read-only review. Conceptually:
1. Launch a token via `Zap.createToken` (seeds the curve with `virtualLtReserve = VIRTUAL_LIQUIDITY_USD*1e18/exchangeRate`, `k = TOTAL_SUPPLY * virtualLtReserve`).
2. Execute a sequence of `Zap.buy`/`Zap.sell` calls that repeatedly exercise `Router._computeBuy`/`_computeSell`'s floor-division rounding (each round-trip trade can leave `tokenReserve*assetReserve` slightly below `k` due to `Pair.swap`'s `(x+1)(y+1)>=k` slack).
3. Once `tokenReserve` is driven close to `TOTAL_SUPPLY` (heavy net selling) and `assetReserve` has accumulated enough downward rounding drift, call `Zap.sell` (or `Bonding.triggerGraduation`) one more time — `canGraduate`'s `assetReserve - _launchTimeVirtualLtReserve(...)` underflows and reverts with `Panic(0x11)`.
4. From that reserve state onward, every `Zap.buy` and `Zap.sell` for that token reverts identically (both call `canGraduate`/`previewLtUntilGraduation` internally), and `triggerGraduation` also reverts before reaching its `NotGraduatable` check — permanently freezing the token's curve.

I recommend a background Devin session run a Foundry fuzz/invariant test directly against `Router._computeBuy`, `Router._computeSell`, and `Pair.swap` to confirm the exact drift magnitude per trade and construct a concrete failing sequence, since this requires numeric simulation beyond static code review.

### Citations

**File:** packages/contracts/src/Bonding.sol (L680-695)
```text
    function canGraduate(
        address token_
    ) public view returns (bool) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return false;
        if (info.lifecycle != Lifecycle.Curve) return false;

        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
    }
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

**File:** packages/contracts/src/Zap.sol (L324-326)
```text
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);

```
