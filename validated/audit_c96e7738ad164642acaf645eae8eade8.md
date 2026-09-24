### Title
Attacker-inflated HyperSwap V2 pre-seed reserves cause a `uint112` overflow revert that permanently bricks `finalizeGraduation`, freezing all curve-raised LT and 250M tokens in `Bonding` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.finalizeGraduation` deposits a fixed, once-computed `(tokensForLP, ltFromPair)` pair into a permissionlessly-creatable HyperSwap V2 pool whose reserves are packed into `uint112` slots. An unrelated wallet can pre-create that TOKEN/LT pair and mint (or repeatedly swap into) a reserve close to `type(uint112).max` before phase 2 runs. Every subsequent attempt at `_pairRebalance`'s direct `pair.swap` or `_routerDepositAndDispose`'s `addLiquidity` then pushes the pool's tracked balance past `type(uint112).max`, and UniswapV2's `_update()` reverts with an overflow. Because `PendingGraduation` is a fixed, already-committed snapshot and there is no retry path that shrinks it, the token is stuck in `Lifecycle.Graduating` forever — this is the exact bug class of CVE-2016-4809 (an attacker-controlled "size" value that is insufficiently bounded and crashes a downstream parser/consumer), mapped onto alt.fun's LP-seeding step.

### Finding Description
`Bonding._deployAndSeed` only bounds `virtualLtReserve` against `type(uint112).max / 4` at **launch time**, based on the assumption that the worst case reserve HyperSwap V2 will ever see is `3 × virtualLtReserve` (curve sellout) [1](#0-0) . That guard only protects `ltFromPair`/`tokensForLP`'s own magnitude — it says nothing about reserves an attacker adds directly to the destination HyperSwap pool before phase 2 executes.

`_ensureUniswapV2Pair` lets **any address** create the TOKEN/LT pair ahead of graduation (it's a plain `getPair`/`createPair` call with no access control), and `IUniswapV2Pair.mint` is a public function on that external pool [2](#0-1) . An attacker can `transfer` a very large amount of TOKEN (freely transferable ERC20) or LT to that pair and call `mint()` themselves, driving one reserve slot near `type(uint112).max`.

`finalizeGraduation` then runs the hostile-pre-seed handling in `_seedRebalancing` / `_pairRebalance` / `_routerDepositAndDispose` [3](#0-2) . These paths only defend against *ratio* imbalance (via `_swapBudget` capping the rebalance swap at 99% of Bonding's own budget, see natspec at lines 1356-1378) — they never check that `reserveIn/out + incoming transfer` stays under `type(uint112).max`. Both `pair.swap` in `_pairRebalance` (line 1425-1427) and `router.addLiquidity` in `_routerDepositAndDispose` (line 1466-1473) ultimately call the HyperSwap V2 pair's internal `_update`, which reverts on `balance > type(uint112).max`. Once the pre-seeded reserve is close enough to the cap, adding even the graduation's own deposit (already bounded up to `~0.75 × type(uint112).max` per the launch-time check) overflows the slot.

Because `PendingGraduation.tokensForLP`/`ltFromPair` are cached once in `_enterGraduating` and only deleted on a **successful** `finalizeGraduation` [4](#0-3) , and the lifecycle enum is strictly forward (`Curve → Graduating → Graduated`, no rollback), a reverting `finalizeGraduation` can be retried indefinitely with the exact same inputs and will revert every time. There is no admin escape hatch that can rewrite `pendingGraduation` or move the token out of `Graduating`.

### Impact Explanation
This permanently freezes:
- All curve-raised LT already pulled out of the `Pair` via `Router.graduate` inside `_prepareGraduationLiquidity` (line 1084-1087), which now sits untouchable in `Bonding`.
- Up to `LP_RESERVE` (250,000,000) launched tokens earmarked for LP that can never be deposited.
- The creator's and every buyer's exposure to that token, since trading is frozen the moment `Lifecycle.Graduating` is entered (`buy`/`sell` both revert with `TokenIsGraduating`) and can never resume (`Graduated` is unreachable, `Curve` is unreachable).

This is a permanent freezing of trader/creator funds, satisfying the "Validate" bar of concrete permanent freezing.

### Likelihood Explanation
Fully reachable by an unprivileged, unrelated wallet: pair creation on the referenced UniswapV2Factory and `mint`/`transfer` on the resulting pair are both public, permissionless calls, and cost is bounded by whatever amount of TOKEN/LT the attacker is willing to acquire and lock into the pool (TOKEN is cheaply obtainable pre-graduation on the curve, and no minimum reserve size is enforced by HyperSwap V2 pair creation). No special timing beyond "before the keeper's `finalizeGraduation` call for that token" is required, and the natspec at lines 1132-1200 already shows the authors are aware of and actively defend against *ratio*-based pre-seed attacks — but the mitigation only bounds swap sizing, not the absolute `uint112` capacity of the destination reserve, leaving this specific magnitude class unguarded.

### Recommendation
Before or during `_seedUniswapV2Direct`, read the live HyperSwap V2 pair reserves and abort/queue the deposit (rather than reverting into a stuck, un-retryable state) whenever `reserveToken + tokensForLP`, `reserveLT + ltFromPair`, or any intermediate `_pairRebalance` transfer would exceed `type(uint112).max`. Alternatively, add a rescue path (e.g., a keeper-callable function that can migrate `pendingGraduation` to a freshly created pair) so a hostile pre-seed cannot make graduation unconditionally and permanently unrecoverable.

### Proof of Concept
1. Attacker watches the mempool/chain for a token approaching `canGraduate(token) == true` on the bonding curve.
2. Attacker calls `Bonding._ensureUniswapV2Pair`-equivalent flow directly on the configured `IUniswapV2Factory.createPair(token, lt)` to create the TOKEN/LT pair ahead of time (or a pair may already exist).
3. Attacker acquires a large TOKEN balance (buying on the curve is permissionless) and/or LT (mint/purchase), then `transfer`s an amount close to `type(uint112).max` of one side to the pair and calls `IUniswapV2Pair.mint(attacker)`, minting themselves LP against a near-max reserve.
4. The curve reaches `canGraduate` (via `Zap.buy`/`triggerGraduation`) and `_enterGraduating` caches `tokensForLP`/`ltFromPair` in `pendingGraduation`, pulling the real raised LT into `Bonding` via `Router.graduate`.
5. Anyone calls `Bonding.finalizeGraduation(token)`. `_seedRebalancing` detects `totalSupply != 0`, attempts `_pairRebalance` (a `pair.swap` that adds to the already near-max reserve) or `_routerDepositAndDispose`'s `addLiquidity` (which transfers `tokensForLP`/`ltFromPair` into the pair and mints). Either call causes the underlying V2 pair's `_update` to revert on `uint112` overflow.
6. `finalizeGraduation` reverts unconditionally on every future call with the same cached `pendingGraduation` values — the token is permanently stuck in `Lifecycle.Graduating`, and the LT/tokens already escrowed in `Bonding` are permanently frozen.

### Citations

**File:** packages/contracts/src/Bonding.sol (L477-485)
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

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1121-1130)
```text
    function _ensureUniswapV2Pair(
        address tokenA,
        address tokenB
    ) internal returns (address pair) {
        IUniswapV2Factory v2Factory = IUniswapV2Factory(_s().uniswapV2Factory);
        pair = v2Factory.getPair(tokenA, tokenB);
        if (pair == address(0)) {
            pair = v2Factory.createPair(tokenA, tokenB);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1279-1354)
```text
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
```
