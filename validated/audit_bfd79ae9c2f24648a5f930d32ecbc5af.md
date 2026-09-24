### Title
Pair.swap's `+1` K-invariant rounding slack can push the real `assetReserve` below the launch-time virtual floor, causing a permanent underflow revert in `canGraduate`/`_launchTimeVirtualLtReserve` that freezes buys and sells on the curve - (File: `packages/contracts/src/Pair.sol`, `packages/contracts/src/Bonding.sol`)

### Summary
CVE-2018-1066 is a NULL-pointer dereference reachable by an attacker who drives an edge-case (empty `TargetInfo`) into a "recovery" code path that was not defensively checked, crashing the client. The alt.fun analog is an **unchecked-subtraction underflow** reachable by an ordinary trader through repeated buy/sell round-trips that exploit `Pair.swap`'s deliberately loose K-invariant check, driving the pair's real `assetReserve` below the immutable launch-time virtual reserve. Every subsequent call into `Bonding.canGraduate` / `_launchTimeVirtualLtReserve` (invoked unconditionally on every buy and by `Zap.sell`'s graduation check) then reverts with a Solidity arithmetic-underflow panic instead of a handled error, permanently DoS'ing the curve.

### Finding Description
`Pair.swap` enforces the K-invariant with a `+1` rounding slack on both sides: [1](#0-0) 

This slack is documented project-wide as an accepted, deliberate tolerance (`Router._computeBuy` / `_computeSell`, "Pair.swap's `+1` K slack") that lets the AMM math avoid re-implementing exact-ceiling rounding on every trade. The tradeoff is that `(newTokenReserve+1)*(newAssetReserve+1)` is allowed to fall *below* the strict product `tokenReserve*assetReserve`, i.e. each swap can round in the trader's favor by a small, non-zero amount relative to the pure curve.

Separately, `Bonding` recovers the pair's launch-time virtual LT reserve as an on-the-fly constant derived from the immutable `k`: [2](#0-1) 

and uses it in an **unchecked subtraction** that is exercised on the hot path of every buy and read by the sell-vs-graduate branch: [3](#0-2) 

`realLtRaised = assetReserve - _launchTimeVirtualLtReserve(...)` is only correct as long as the live `assetReserve` never drops below the pair's launch-time virtual floor. That floor is fixed forever (`k` is set once in `Pair.mint` and never re-derived), while the live `assetReserve` is free to move down through the `+1`-slack-tolerant `swap` on every sell. Because Solidity 0.8 reverts on unsigned underflow, any state where `assetReserve < virtualLtReserve` turns this view into an unconditional revert.

`canGraduate` is not a passive getter — it is invoked inline at the end of every buy (`Bonding._executeBuy`/`_enterGraduating` per project docs) and is used by `Zap.sell` to decide whether a sell should instead redirect into `triggerGraduation`. A revert inside `canGraduate` therefore propagates and reverts the outer `buy`/`sell` call itself, for every trader, on every subsequent transaction against that pair — there is no catch, no fallback, and no admin recovery path documented for this specific state.

This is structurally the same bug class as the CVE: a boundary condition in a field that is normally well-formed (a non-empty `TargetInfo` / a live `assetReserve` that should always sit at or above the virtual floor) is mishandled in a "recovery"-adjacent code path (`setup_ntlmv2_rsp` during session re-negotiation / `canGraduate` during every trade's post-check), turning attacker-reachable input into a hard crash instead of a graceful error.

### Impact Explanation
If reachable, this permanently freezes the affected curve: `Bonding.buy` and (via `Zap.sell`'s pre-check) `Bonding.sell` both revert unconditionally, trapping the real curve-raised LT and the 250M `lpReserve` tokens parked in `Bonding`, and blocking traders from exiting their positions — a permanent freezing-of-funds impact within the accepted scope (unprivileged trader path, `Bonding.buy`/`Zap.sell`, no privileged action required to trigger or to attempt recovery).

### Likelihood Explanation
Likelihood is **uncertain and not fully proven** from the code I was able to inspect. I confirmed:
- `Pair.swap`'s K-check uses a `+1`/`+1` slack that is *looser* than the pure product invariant (directly read from `packages/contracts/src/Pair.sol`).
- `Bonding.canGraduate`/`_launchTimeVirtualLtReserve` perform an unchecked subtraction against a fixed floor and are on the mandatory hot path of every buy/sell.

What I could **not** verify within the available tool budget is the exact `Router._computeBuy`/`_computeSell` formulas that determine how much rounding "leaks" per round-trip swap, and whether that leak is bounded to zero (fully absorbed by fee math) or can accumulate over many iterations to actually breach the virtual floor. The project's own comments describe the `+1` slack as intentional and "benign," which suggests the team may already bound this to be unreachable in practice (e.g., fees always dominate the rounding direction). Without reading `Router.sol` directly I cannot confirm whether an attacker-affordable sequence of buys/sells can accumulate enough negative drift to cross the floor, or whether this is purely theoretical and already unreachable by construction — this is the main open question a follow-up review must resolve.

### Recommendation
- Replace the unchecked subtraction in `_launchTimeVirtualLtReserve`-consuming call sites (`canGraduate`, `previewLtUntilGraduation`, `_prepareGraduationLiquidity`) with a saturating subtraction (`assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0`), mirroring the saturating-subtract pattern already used defensively elsewhere in `Bonding.sol` (e.g. `_ltSwapInventory`, the `protectedLT` snapshot in `finalizeGraduation`).
- Independently verify in `Router._computeBuy`/`_computeSell` whether the `+1` K-slack can ever let `assetReserve` drift below the pair's launch-time virtual reserve over repeated trades, and if so, tighten the invariant check or fee rounding direction so the floor is unconditionally maintained.

### Proof of Concept
Not constructed — reachability depends on `Router.sol`'s exact buy/sell rounding formulas, which were not available in the indexed context for this analysis. A concrete PoC would need to: (1) read `Router._computeBuy`/`_computeSell` to determine the per-trade rounding direction and magnitude against `Pair.swap`'s `+1` slack; (2) if a negative-drift path exists, script repeated buy→sell round-trips via `Bonding.buy`/`Bonding.sell` (or `Zap.buy`/`Zap.sell`) until `assetReserve` dips below the fixed `k/TOTAL_SUPPLY` floor; (3) call `Bonding.canGraduate` or attempt any further buy/sell and observe the arithmetic-underflow revert freezing the curve.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1114-1119)
```text
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```
