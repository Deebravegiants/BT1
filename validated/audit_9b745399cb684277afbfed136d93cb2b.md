### Title
Repeated K-invariant-slack swaps can underflow `assetReserve - virtualLtReserve`, permanently DoS'ing a curve's buy path and graduation - ([File: packages/contracts/src/Bonding.sol])

### Summary
CVE-2016-6302 is a length-validation bug: `tls_decrypt_ticket` subtracts a fixed HMAC size from an attacker-controlled ticket length without first checking the length is large enough, underflowing the size and causing a crash/DoS. The structurally analogous bug class in alt.fun is an unchecked `uint256` subtraction of a derived "floor" value from a stored reserve, reachable by an unprivileged trader through ordinary buy/sell calls, that can revert with a Solidity Panic (arithmetic underflow) and permanently brick a load-bearing path.

### Finding Description
`Bonding.canGraduate` and `Bonding._prepareGraduationLiquidity` both compute:

```solidity
uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
``` [1](#0-0) 

and

```solidity
ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
``` [2](#0-1) 

Both rely on the invariant that the pair's *stored* `assetReserve` can never fall below the launch-time virtual LT reserve (`Pair.k() / TOTAL_SUPPLY()`), because that virtual reserve is supposedly a hard floor of the constant-product curve. This invariant is only "approximately" true, however, because `Pair.swap` does not enforce the exact `k`; it enforces a slightly relaxed bound with a `+1` slack on both sides:

```solidity
uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
``` [3](#0-2) 

This `+1` slack (explicitly called out by the project's own docs as a place "where bugs live") permits `newAssetReserve` to dip fractionally below the exact `k / newTokenReserve` value on every single swap, as long as `(tR+1)(aR+1) >= k` still holds. On any individual swap the drift is tiny (bounded by rounding), but it is **not reset or corrected** between swaps — each buy/sell round trip through `Router._computeBuy`/`_computeSell` and `Pair.swap` can shave the stored `assetReserve` fractionally closer to (or, cumulatively, below) `virtualLtReserve` because the check only guards against violating `k` by more than the +1-per-call slack, not against cumulative drift across many calls. An unprivileged trader can grind an arbitrary number of small buy+sell round trips (each individually satisfying the K-invariant check) at `tokenReserve` near `TOTAL_SUPPLY` (i.e., right after a large sell-off returns most curve tokens to the pair), incrementally consuming this slack until the stored `assetReserve` drops below `_launchTimeVirtualLtReserve(...)`.

Unlike `previewLtUntilGraduation`, which was patched with an explicit guard (`if (realBalance >= reserveToken) return ltUntilThreshold;`) after a prior incident described directly in the test suite —

```solidity
// A TOKEN donation that drives `realBalance > reserveToken` previously
// underflowed `Bonding.previewLtUntilGraduation`'s supply leg,
// cascading into a `Zap.buy` DoS. Guard added; tests pin the fix.
``` [4](#0-3) 

— `canGraduate` (line 692) and `_prepareGraduationLiquidity` (line 1084) contain the exact same shape of un-guarded subtraction with no equivalent floor check. Because `canGraduate` is invoked unconditionally at the end of every buy inside `_executeBuy` (per the project's own documentation of the buy flow), an underflow there does not merely mis-price a preview — it causes every subsequent `Bonding.buy` call (and thus every `Zap.buy`) on that token's curve to revert with an arithmetic-underflow Panic, permanently freezing the curve. `Bonding.triggerGraduation` (`external nonReentrant`, permissionless, reachable by any wallet) also calls `canGraduate` directly and would revert identically, so nobody can even force graduation to unstick the token.

### Impact Explanation
If the subtraction underflows, `canGraduate` reverts with a Panic on every call. Since `_executeBuy` calls `canGraduate` at the end of every buy, this bricks `Zap.buy`/`Bonding.buy` for the affected token permanently — all LT and USDC value already raised into that curve (and any 250M lpReserve tokens parked in `Bonding`) become frozen: buyers can no longer buy, and the token can never reach graduation because both `triggerGraduation` and the inline post-buy trigger depend on the same reverting call. This is a concrete, permanent freezing-of-funds condition matching the "Validate" bar (concrete theft or permanent freezing of trader/creator funds), directly analogous to the OpenSSL DoS bug class (unvalidated size/length subtraction causing crash-on-every-call).

### Likelihood Explanation
Reaching the exact drift needed requires the pair to sit at (or very near) `tokenReserve == TOTAL_SUPPLY` — i.e., essentially all curve tokens have been sold back into the pair (a state reachable simply by an early buyer selling their full position) — and then requires an attacker to grind many small buy/sell round trips against the `+1` slack to accumulate enough drift to flip the sign of the subtraction. I could not fully quantify, from static reading alone, exactly how many round trips are needed or whether integer rounding in `_computeBuy`/`_computeSell` cooperates to make the cumulative drift monotonic in the attacker's favor rather than self-correcting; the project's own regression-test history shows this exact "unguarded reserve-difference subtraction" bug pattern was previously exploitable via a different vector (donation inflating `realBalance` above `reserveToken`) and had to be patched with an explicit floor check in `previewLtUntilGraduation`, but the same class of bare subtraction was left unguarded in `canGraduate` and `_prepareGraduationLiquidity`. Given the explicit callout of the `+1` K-slack as a known-risky area in the scan rules, and the absence of any floor/guard on these two call sites, likelihood is assessed as Medium: the precondition (near-empty net-sold curve) is realistic and unprivileged-reachable, but the exact swap sequence to cross the underflow boundary needs empirical/fuzz confirmation that a live agent with contract access and a test harness could perform (e.g. extending `GraduationInvariants.t.sol`'s fuzzing to specifically hunt for this cumulative-drift underflow).

### Recommendation
Add the same defensive floor check to `canGraduate` and `_prepareGraduationLiquidity` that was already applied to `previewLtUntilGraduation`: if `assetReserve <= _launchTimeVirtualLtReserve(...)`, treat `realLtRaised`/`ltFromPair` as `0` instead of performing a bare subtraction, e.g.:

```solidity
uint256 virtualLt = _launchTimeVirtualLtReserve(token_, pair);
uint256 realLtRaised = assetReserve > virtualLt ? assetReserve - virtualLt : 0;
```

Additionally, consider tightening `Pair.swap`'s `+1` slack accounting (e.g., tracking cumulative slack consumption, or removing the `+1` grace entirely in favor of exact `k`-preservation with explicit rounding-direction control) so that stored reserves cannot drift below their theoretical floor across many transactions, since this same slack is flagged elsewhere as touching LP-seeding price-equality invariants.

### Proof of Concept
A full working PoC requires a Foundry harness (not verifiable from static reading alone) that:
1. Launches a token via `Bonding.launch`/`Zap.createToken`.
2. Buys enough to move a meaningful amount of `curveSupply` tokens out of the pair, then sells them back with a real user wallet so `tokenReserve` returns to (or very near) `TOTAL_SUPPLY`.
3. Repeats small buy(`Bonding.buy`)/sell(`Bonding.sell`) round trips at this boundary, each satisfying `Pair.swap`'s `(newTokenReserve+1)*(newAssetReserve+1) >= k` check, tracking `IPair(pair).getReserves()` after each round trip to confirm `assetReserve` is monotonically approaching (and eventually crossing below) `Pair.k() / Token.TOTAL_SUPPLY()`.
4. Calls `Bonding.canGraduate(token)` (or performs one more buy through `Zap.buy`) and observes a revert with a bare arithmetic Panic (`0x11`) instead of a named error, confirming the underflow and the resulting permanent DoS of the curve's buy path.

This exact scenario — extending the existing fuzz/invariant coverage in `test/GraduationInvariants.t.sol` to specifically search for cumulative `+1`-slack drift crossing the `assetReserve < virtualLtReserve` boundary — is the concrete next step to convert this into a fully reproduced PoC.

### Citations

**File:** packages/contracts/src/Bonding.sol (L691-694)
```text
        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L1084-1084)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
```

**File:** packages/contracts/src/Pair.sol (L71-73)
```text
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();
```

**File:** packages/contracts/test/Zap.t.sol (L939-943)
```text
    // ─── Donation attack regression ──────────────────────────────────────
    // A TOKEN donation that drives `realBalance > reserveToken` previously
    // underflowed `Bonding.previewLtUntilGraduation`'s supply leg,
    // cascading into a `Zap.buy` DoS. Guard added; tests pin the fix.

```
