### Title
Unbounded round-trip drain via `Pair.swap`'s `+1` K-slack causes permanent underflow-revert bricking in `Bonding.canGraduate` - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Pair.swap` enforces the constant-product invariant with a loosened `+1` slack rather than the exact product, letting every buy/sell drain the pair of a small amount of value beyond what a true zero-slack constant-product curve would allow. `Bonding.canGraduate` recovers the launch-time virtual LT reserve from the *immutable* `Pair.k()` and subtracts it from the live, mutable `assetReserve` without a floor check. Because `k` never changes after `Pair.mint` while `assetReserve` can be walked down below the nominal floor by repeated slack-exploiting round trips, the subtraction can underflow and revert with a Solidity Panic. `canGraduate` is called unconditionally at the end of every buy and inside the permissionless `triggerGraduation`, so once the underflow condition is reached, it reverts on every subsequent invocation — permanently bricking further buys and permanently preventing the token from ever graduating.

### Finding Description
`Pair.swap` checks:
```solidity
uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
``` [1](#0-0) 

The `+1` on both reserves means the *actual* post-trade product `newTokenReserve * newAssetReserve` is allowed to fall strictly below `_pool.k` (by up to roughly `newTokenReserve + newAssetReserve`), because the check is performed on the shifted product, not the raw one. `_pool.k` itself is set once in `mint` and is never updated by `swap` [2](#0-1) .

`Bonding._launchTimeVirtualLtReserve` recovers the launch-time virtual LT reserve purely from this immutable `k`:
```solidity
function _launchTimeVirtualLtReserve(address token_, address pair_) internal view returns (uint256) {
    return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
}
``` [3](#0-2) 

`canGraduate` then does an unchecked subtraction of this constant from the live, mutable `assetReserve`:
```solidity
(, uint256 assetReserve) = IPair(pair).getReserves();
uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
``` [4](#0-3) 

Because every swap is permitted to leak a small amount of value to the trader relative to the true (non-slack) invariant, repeated buy→sell round trips through `Zap`/`Bonding.buy`/`Bonding.sell` on the same token can progressively pull `assetReserve` down toward (and eventually below) the fixed floor `k / TOTAL_SUPPLY`. Once `assetReserve` dips below that floor, the subtraction in `canGraduate` underflows and reverts with a Solidity `Panic(0x11)`.

`canGraduate` is not a passive view called only off-chain — it is invoked unconditionally at the end of every successful buy:
```solidity
function _executeBuy(...) internal returns (...) {
    (amountInUsed, tokensOut) = _s().router.buy(amountIn, tokenAddress, tokenHolder);
    ...
    if (canGraduate(tokenAddress)) {
        _enterGraduating(tokenAddress);
    }
}
``` [5](#0-4) 

and inside the permissionless `triggerGraduation`:
```solidity
function triggerGraduation(address tokenAddress) external nonReentrant {
    ...
    if (!canGraduate(tokenAddress)) revert NotGraduatable();
    _enterGraduating(tokenAddress);
}
``` [6](#0-5) 

Once the underflow condition is reached, *every future call* to `canGraduate` (and therefore every future `buy`, and every `triggerGraduation` call) reverts. The token becomes permanently stuck in `Lifecycle.Curve`: it can never reach the graduation threshold, `_enterGraduating`/`finalizeGraduation`/`LPLock.recordLock` can never run, and any real LT raised plus the 250M `LP_RESERVE` tokens earmarked for the token remain locked inside `Bonding` forever with no rescue path (only `sell` on the raw `Router` remains reachable, but the token's normal buy-side economics and its entire graduation path are permanently dead).

This is the same bug class as the CVE (a missing bounds/NULL check before a dereference/operation that a remote, unprivileged actor can trigger to permanently crash the affected code path), mapped onto alt.fun's virtual-reserve bonding-curve math and its `Pair.swap` `+1` K-slack, exactly the areas the scope calls out as bug-prone.

### Impact Explanation
This is a permanent denial-of-service / freezing-of-funds bug reachable by any unprivileged trader:
- All future `Zap.buy` (and `Bonding.buy`) calls on the affected token revert forever once triggered.
- The token can never graduate: `triggerGraduation` reverts forever, so the curve-raised LT and the 250M `LP_RESERVE` tokens locked in `Bonding` for that token are permanently stranded, and no `HyperSwap V2` pool is ever seeded.
- Creator/protocol fee accrual on that token effectively halts since no further buys can execute.

This satisfies "permanent freezing of trader, creator or LP funds" from the validation criteria and is High severity given it is triggerable purely through public `Zap`/`Bonding` buy/sell calls with no privileged role required.

### Likelihood Explanation
The precondition requires enough cumulative slack-exploiting round trips to erode `assetReserve` down to the fixed floor `k / TOTAL_SUPPLY`. Each individual trade's slack margin is small (bounded by `newTokenReserve + newAssetReserve` in the `+1` relaxation), so the number of round trips needed scales with the reserve magnitudes; however, since the attacker only pays gas and a `Zap` fee per round trip and extracts value each time regardless of trade size, this is economically and mechanically executable by a single unprivileged wallet with no cooperation from anyone else, and is most exploitable early in a token's life when `realLtRaised` (the margin above the floor) is smallest — e.g., shortly after the mandatory `$20` seed buy, before other traders raise the buffer. The exact number of round trips required needs on-chain/fork simulation to pin down precisely, but the underlying rounding-slack root cause is directly present and unguarded in the reachable code paths cited above.

### Recommendation
- Tighten `Pair.swap`'s invariant check to avoid a persistent one-directional value leak — e.g., require the raw product `newTokenReserve * newAssetReserve >= _pool.k` (no `+1` relaxation), or bound the allowed slack to a fixed, non-cumulative amount that cannot be exploited via repeated round trips.
- Make `canGraduate`'s subtraction defensive: clamp `realLtRaised` to `0` when `assetReserve <= _launchTimeVirtualLtReserve(...)` instead of subtracting unconditionally, so a floor breach degrades gracefully (treats the token as "not yet graduatable") rather than reverting and bricking every subsequent buy.
- Add an invariant/regression test that performs many buy/sell round trips against a fresh curve and asserts `canGraduate` never reverts and `assetReserve` never drops below `Pair.k()/TOTAL_SUPPLY()`.

### Proof of Concept
1. Launch a token via `Zap.createToken` with the minimum `$20` seed, establishing `Pair.mint(TOTAL_SUPPLY, virtualLtReserve)` and `_pool.k = TOTAL_SUPPLY * virtualLtReserve` (immutable thereafter) [2](#0-1) .
2. As an unprivileged trader, repeatedly call `Zap.buy` followed by `Zap.sell` on the same token in small amounts. Each round trip goes through `Router.buy`/`Router.sell` → `Pair.swap`, which permits the actual post-trade product to fall slightly below `_pool.k` due to the `+1` slack [7](#0-6) , extracting marginally more LT value than a strict-invariant curve would.
3. Continue round trips until the live `assetReserve` (read via `IPair.getReserves()`) drops to/below the fixed floor `_pool.k / Token.TOTAL_SUPPLY()`.
4. The next call to `canGraduate(token)` — triggered either by any subsequent `Bonding.buy` (via `_executeBuy`) or directly via `triggerGraduation` — executes `assetReserve - _launchTimeVirtualLtReserve(...)` [8](#0-7)  and underflows, reverting with `Panic(0x11)`.
5. From this point on, every `Bonding.buy` call on this token reverts inside `_executeBuy`'s `canGraduate` check [9](#0-8) , and `triggerGraduation` reverts as well, permanently freezing the token's buy path and graduation.

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

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
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

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1114-1119)
```text
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```
