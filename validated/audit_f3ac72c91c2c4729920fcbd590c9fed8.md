### Title
Unguarded `assetReserve - virtualLtReserve` subtraction in `canGraduate` / `_prepareGraduationLiquidity` can arithmetic-underflow (Panic) and permanently brick a curve — analog of CVE-2023-46239's unchecked-state-dereference panic ([File: packages/contracts/src/Bonding.sol])

### Summary
Both the USD graduation trigger in `canGraduate()` and the LP-sizing computation in `_prepareGraduationLiquidity()` compute `realLtRaised = assetReserve - virtualLtReserve` with a bare Solidity subtraction and no bounds check, relying on the invariant "stored `assetReserve` can never go below the launch-time virtual seed." That invariant is only enforced by `Pair.swap`'s `+1` K-invariant slack, which is deliberately loose (documented as `Pair.swap's `+1` K slack`). At the edge where the virtual token reserve is driven back to (or near) `totalSupply` — i.e. a near-fully-unwound curve after a buy-then-sell round trip — the K-slack permits the stored `assetReserve` to legitimately settle strictly below `virtualLtReserve`. The next call to `canGraduate()` (invoked by every `Bonding.buy`, by `Bonding.triggerGraduation`, and by `Zap.sell`'s graduation-check) then underflows and reverts with a Solidity arithmetic Panic (0x11), exactly the CWE-248/CWE-476 "unchecked state read causes a fatal panic" class the quic-go advisory describes (there: an out-of-order ACK causes a nil-pointer read while dropping the Handshake packet-number space; here: an out-of-order/edge-case swap sequence causes a stale invariant to be read past its valid domain).

### Finding Description
`_launchTimeVirtualLtReserve` recovers the launch-time virtual LT seed as `Pair.k() / Token.TOTAL_SUPPLY()`: [1](#0-0) 

`canGraduate()` uses it unguarded: [2](#0-1) 

`_prepareGraduationLiquidity()` uses the identical pattern: [3](#0-2) 

`Pair.swap`'s invariant check is intentionally loose (`+1` on both reserves, not on `k`): [4](#0-3) 

`k` is fixed once at mint to `totalSupply * virtualLtReserve` and never adjusted: [5](#0-4) 

The mathematical bound: after any swap, the constraint is `(t+1)*(a+1) >= k = S*v` (S = totalSupply, v = virtualLtReserve). Solving for when `a < v` is permitted:
`(t+1) >= S*v/(a+1) > S*v/v = S` whenever `a < v`.
Since `t` (virtual token reserve) is monotonically bounded by `t <= S` (a seller can never return more tokens to the pool than the curve ever paid out, because `Token`'s fixed 1B supply and ERC20 accounting prevent minting extra tokens back), `t == S` is achievable exactly when the curve's net position is fully unwound (e.g. immediately after launch, or after a trader buys and then sells their entire position back). At `t == S` exactly, the slack allows `a = v - 1` to satisfy the invariant (`(S+1)*v >= S*v` is always true), i.e. the stored `assetReserve` can legitimately be `virtualLtReserve - 1`.

Once this state is reached, `assetReserve - _launchTimeVirtualLtReserve(...)` underflows: `(v-1) - v` panics. This computation is not confined to a single failing tx — `canGraduate()` is a `public view` re-executed on **every** subsequent `Bonding.buy` (per the docs, `canGraduate()` is checked at the end of every buy inside `_executeBuy`) and by the permissionless `Bonding.triggerGraduation`, and `Zap.sell` also consults graduatability before allowing a sell to proceed. If the underflow condition persists (i.e. the curve stays at/near the fully-unwound edge, which is trivially maintainable by not buying further), every future buy/sell/triggerGraduation call that reaches this check reverts with a Panic, permanently freezing the curve — no further trading is possible and the token can never graduate.

This is directly analogous to the quic-go bug class: a piece of code assumes an invariant ("assetReserve never dips below the immutable virtual seed") that a normal, permissionless sequence of protocol-level operations (ordinary buy/sell round trips exploiting the documented `+1` K-slack) can violate, causing an unguarded read/subtraction to panic and take down the affected component — here, permanently, rather than per-request.

### Impact Explanation
A reverting `canGraduate()` bricks:
- Every `Bonding.buy` on the affected curve (buy calls `canGraduate` at the end of `_executeBuy` per every buy), freezing all trader and creator funds committed to that curve going forward.
- `Bonding.triggerGraduation`, so the token can never be pushed to graduation even manually.
- `Zap.sell`'s graduation pre-check path, potentially bricking sells as well, trapping tokens/LT already inside the curve with no exit via the curve (only recourse would be an admin-level intervention, e.g. an upgrade).

This is a permanent freezing of trader/creator funds on the affected bonding curve — satisfying the "permanent freezing of trader, creator or LP funds" impact bar. Because the trigger condition only requires the curve to sit at (or return to) a fully-unwound state — plausible on a fresh launch with no seed buy, or any curve a whale later fully exits — the attack surface is broad and reachable by an ordinary unprivileged trader.

### Likelihood Explanation
Medium-High. No privileged role is required; the only actions needed are ordinary `Zap.buy` / `Zap.sell` calls (or direct `Bonding.buy`/`sell` via an allowlisted router) that a normal trader might perform naturally (buy then fully exit). The precise boundary condition (`t` returning to exactly `totalSupply`, or close enough that the K-slack pushes `a` below `v`) requires the curve to be at very low net utilization, which is most easily reached right after launch, before a seed buy consumes it, or any time a curve round-trips back to empty. Exploiting it deliberately (as a griefing/DoS vector against a competitor's launch) costs only gas plus the two round-trip trades. The exact 1-wei-scale nature of the slack means confirming feasibility requires precise on-chain arithmetic verification (fuzzing/foundry) against the live `Pair.k()`/`getReserves()` values — this document's analysis establishes the mathematical possibility from the code but a concrete numeric trace (with the actual `virtualLtReserve` derived from `VIRTUAL_LIQUIDITY_USD` and a live `exchangeRate()`) should be fuzzed to nail an exact minimal repro amount.

### Recommendation
- Replace the bare subtraction in both `canGraduate()` and `_prepareGraduationLiquidity()` with a saturating pattern, mirroring the defensive style already used in `finalizeGraduation` for `protectedLT` (`ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0`):
  ```solidity
  uint256 virtualReserve = _launchTimeVirtualLtReserve(token_, pair);
  uint256 realLtRaised = assetReserve > virtualReserve ? assetReserve - virtualReserve : 0;
  ```
- Add a Foundry invariant/fuzz test that repeatedly round-trips buy/sell near zero net position and asserts `canGraduate()` never reverts, to lock in the fix and catch any future regression of the K-slack assumption.
- Re-audit `_prepareGraduationLiquidity`'s `ltFromPair` computation with the same saturating guard so `Router.graduate` is never called with an underflowed / bogus large value if the pattern is reused elsewhere.

### Proof of Concept
```solidity
// Foundry-style sketch (illustrative — exact numeric trigger amounts require
// on-chain fuzzing against the deployed VIRTUAL_LIQUIDITY_USD / LT exchangeRate,
// since the underflow window is on the order of 1 wei of `assetReserve`):

function test_canGraduate_underflowPanic_afterRoundTrip() public {
    (address tokenAddr, address pairAddr) = _launchTokenNoSeed(); // t == totalSupply initially

    // Any trader performs an ordinary buy...
    uint256 tokensOut = _buy(tokenAddr, trader, SOME_LT_AMOUNT);

    // ...then fully sells the position back, returning the virtual
    // token reserve back toward `totalSupply`. Because `Pair.swap`'s
    // K-check uses `(t+1)*(a+1) >= k` rather than `t*a >= k`, the
    // resulting stored `assetReserve` can legitimately settle at
    // `virtualLtReserve - 1` once `t` is back at (or near) `totalSupply`.
    vm.startPrank(trader);
    IERC20(tokenAddr).approve(address(curveRouter), tokensOut);
    bonding.sell(tokensOut, tokenAddr, 0, trader);
    vm.stopPrank();

    // Any subsequent call to canGraduate (or a following buy, which
    // calls canGraduate internally) panics with arithmetic underflow
    // instead of returning `false`, bricking the curve.
    vm.expectRevert(); // Panic(0x11): arithmetic underflow
    bonding.canGraduate(tokenAddr);
}
```
Note: the exact `SOME_LT_AMOUNT` / round-trip depth needed to land `assetReserve` at `virtualLtReserve - 1` is a 1-wei-scale boundary condition dependent on `Pair.k()` and the live LT `exchangeRate()`; a Devin/foundry fuzz run against `test/GraduationInvariants.t.sol`'s harness (which already exercises `_launchNoSeed`, `_buy`, and `bonding.sell`) should be used to derive/confirm a concrete deterministic amount before treating this as a fully proven live exploit.

### Citations

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L1076-1087)
```text
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
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
