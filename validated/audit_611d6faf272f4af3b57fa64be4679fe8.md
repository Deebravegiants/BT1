## Analysis

CVE-2018-12459 is a bug class about an **inconsistent internal value that a downstream routine implicitly assumes is bounded relative to another value**, causing that routine's core invariant to silently break. The alt.fun analog is in the `Pair`/`Router`/`Bonding` triangle: `Pair.tokenReserve` (the AMM's virtual accounting state) is only ever kept in lock-step with `Pair.tokenBalance()` (the live ERC20 balance) through the `Router.buy`/`sell` code paths — but `tokenBalance()` is a raw `balanceOf` read that any unprivileged holder can move directly with `Token.transfer(pair, amount)`. [1](#0-0) 

`Router._computeBuy`'s overflow-cap logic assumes `tokenBalance() ≤ tokenReserve` (this is asserted as a hard invariant in `test_inv_virtualReserveAlwaysExceedsRealBalance`), and uses that assumption to size the "last buy" that empties the curve: [2](#0-1) 

`Bonding.canGraduate`'s supply trigger relies on the same real balance eventually hitting exactly `0`: [3](#0-2) 

### Title
Direct token donation to the curve `Pair` permanently disables the supply-exhaustion graduation trigger, freezing curve LT and the 250M LP reserve — ([File: packages/contracts/src/Router.sol, packages/contracts/src/Bonding.sol])

### Summary
`Router._computeBuy`'s overflow-cap logic and `Bonding.canGraduate`'s supply trigger both assume `Pair.tokenBalance() ≤ Pair.tokenReserve` at every point of a token's `Lifecycle.Curve` life. This is true only because the virtual-reserve seeding at launch guarantees `tokenReserve - tokenBalance() == LP_RESERVE (250M)` for as long as the only mutations to both values come from matched `transferToken` + `swap()` calls inside `Router.buy`/`sell`. Any unprivileged holder can break that pairing by simply calling `Token.transfer(pairAddr, amount)` directly on the launched ERC20 — this raises `tokenBalance()` without touching the stored `tokenReserve`. Once the donated amount exceeds `LP_RESERVE`, `tokenBalance()` permanently exceeds `tokenReserve` for the remainder of the curve's life, because the constant per-trade offset never resets. From then on `Router._computeBuy`'s uncapped `tokensOut` (which is always `< reserveToken`) can never exceed the inflated `realBalance`, so the `tokensOut > realBalance` branch that is supposed to fire on the curve's final buy never fires again — `tokenBalance()` can never return to `0`.

### Finding Description
At launch, `Bonding._deployAndSeed` mints `Pair.tokenReserve = totalSupply (1e9)` while transferring only `curveSupply = 750M` real tokens to the pair, leaving `LP_RESERVE = 250M` inside `Bonding`: [4](#0-3) 

Every legitimate `Router.buy`/`sell` moves `tokenReserve` and the real token balance by the exact same delta (`transferToken`/`transferAsset` alongside `Pair.swap`), so `tokenReserve - tokenBalance() = 250M` is a hard invariant of the honest flow, confirmed by the project's own regression test: [5](#0-4) 

But `Pair.sol` places no restriction on raw ERC20 transfers into itself — `tokenBalance()` is a plain `balanceOf` read: [6](#0-5) 

An attacker can:
1. Buy `X ≥ 250,000,001` tokens off the curve via `Bonding.buy`/`Zap.buy` (paying real LT/USDC at the curve price — a fraction of the curve's ~$3K virtual-liquidity seed since `X` is well inside the 750M sellable supply).
2. Call `Token(tokenAddr).transfer(pairAddr, X)` directly (not through `Router.sell`), which increases `Pair.tokenBalance()` by `X` without touching `_pool.tokenReserve`.

After this, `tokenBalance() = tokenReserve + (X - 250M) > tokenReserve` permanently, because every subsequent honest buy/sell still moves both quantities by the same delta, preserving the now-negative gap. Since `Router._computeBuy`'s unconstrained `tokensOut` satisfies `tokensOut < reserveToken` always (see `_computeBuy`), and `reserveToken < tokenBalance()` now holds forever, the condition `tokensOut > realBalance` that triggers the overflow cap (and thus the eventual `tokenBalance() == 0` supply trigger) can never be true again: [2](#0-1) 

`Bonding.canGraduate`'s supply leg (`IPair(pair).tokenBalance() == 0`) is therefore permanently unreachable for this token: [7](#0-6) 

If the paired LT's `exchangeRate()` never appreciates enough to cross the USD trigger (a realistic market condition — flat or declining leveraged-token price), the token can never enter `Lifecycle.Graduating`/`Graduated`. It is stuck in `Lifecycle.Curve` forever: the `LP_RESERVE` (250M tokens) stays locked in `Bonding`, all LT raised by the curve stays locked in the `Pair`, and the token can never migrate to the HyperSwap V2 pool.

### Impact Explanation
This is a permanent, unprivileged, low-cost freeze of both curve-raised LT (trader/creator funds) and the 250M `LP_RESERVE` token allocation. It also permanently disables the "flat/bear market" backstop trigger the protocol's own documentation says exists specifically to guarantee graduation always eventually happens (`docs/contracts-scope.md` / `AGENTS.md`: "the supply trigger fires... handles flat/bear markets where $9K is never reached"). Breaking that backstop converts a documented safety net into a permanently disabled one for any token an attacker chooses to target, which is a direct violation of the Validate criterion "permanent freezing of trader, creator or LP funds."

### Likelihood Explanation
Reachable by any unprivileged wallet using only `Bonding.buy`/`Zap.buy` and a plain `IERC20.transfer` on the launched `Token` (no privileged role, no upgrade, no external LT bug required). Cost is bounded by buying ~33% of the curve's real 750M supply at curve price (a few hundred to low-thousand dollars depending on the LT's exchange rate at attack time), which is affordable griefing for a creator-hostile actor, a competitor, or anyone wanting to permanently strand a token pre-graduation. The condition for lasting harm (USD trigger never independently crossing threshold) depends on the external LT's price path, but the attacker can choose to strike right after a token launches, when `realLtRaised` is small and the USD trigger is far from tripping, maximizing the freeze window.

### Recommendation
`Router._computeBuy`'s overflow-cap decision and `Bonding.canGraduate`'s supply trigger must not rely on the raw `tokenBalance()` read being bounded by `tokenReserve`. Either:
- Change the supply trigger to compare against a value that donations cannot desynchronize (e.g., track real tokens sold as a `Router`/`Pair`-internal counter mutated only by `Router.buy`/`sell`, mirroring the `_launchTimeVirtualLtReserve`-style stored-state approach already used to make the USD trigger donation-immune), or
- In `Router._computeBuy`, detect and burn (or otherwise neutralize) any `tokenBalance() > tokenReserve` excess before evaluating the cap, restoring the `tokenBalance() ≤ tokenReserve` invariant on every buy rather than only at graduation time.

### Proof of Concept
1. Launch a token via `Zap.createToken` (curve seeded at `tokenReserve = 1e9`, `tokenBalance() = 750,000,000`).
2. Attacker calls `Bonding.buy`/`Zap.buy` (or accumulates via multiple buys) until they hold `X = 260,000,000` tokens; at this point curve state is `tokenReserve = 740,000,000`, `tokenBalance() = 490,000,000` (gap still 250M).
3. Attacker calls `Token(tokenAddr).transfer(pairAddr, 260_000_000e18)` directly (plain ERC20 transfer, bypassing `Router`/`Bonding`).
4. Now `tokenBalance() = 750,000,000` while `tokenReserve = 740,000,000` — `tokenBalance() > tokenReserve`, breaking `test_inv_virtualReserveAlwaysExceedsRealBalance`'s asserted invariant.
5. Any subsequent buy computes `tokensOut < tokenReserve < tokenBalance()`, so `Router._computeBuy`'s `tokensOut > realBalance` branch never engages again; `tokenBalance()` can never reach `0`, so `Bonding.canGraduate`'s supply leg is permanently `false`.
6. If the paired LT's `exchangeRate()` stays below the level needed to cross `graduationThresholdUsd` on the USD leg, the token remains in `Lifecycle.Curve` indefinitely — curve LT and the 250M `LP_RESERVE` are permanently unreachable.

### Citations

**File:** packages/contracts/src/Pair.sol (L88-105)
```text
    function transferToken(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(launchedToken).safeTransfer(recipient, amount);
    }

    function getReserves() external view returns (uint256, uint256) {
        return (_pool.tokenReserve, _pool.assetReserve);
    }

    function k() external view returns (uint256) {
        return _pool.k;
    }

    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
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

**File:** packages/contracts/src/Bonding.sol (L481-494)
```text
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

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-377)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
    function test_inv_virtualReserveAlwaysExceedsRealBalance() public {
        (address tokenAddr, address pairAddr) = _launchNoSeed();

        // Right after launch.
        assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "post-launch invariant");

        // After a series of buys the property must continue to hold while
        // the curve is still trading.
        for (uint256 i = 0; i < 10; i++) {
            if (!bonding.isTrading(tokenAddr)) break;
            _buy(tokenAddr, trader, 100 ether);
            if (bonding.isTrading(tokenAddr)) {
                assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "invariant must hold after every buy");
            }
        }
    }
```
