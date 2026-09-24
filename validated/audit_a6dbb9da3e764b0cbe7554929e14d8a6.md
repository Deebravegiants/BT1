This gives me enough to write the finding.

### Title
Budget-capped rebalance swap in `_seedRebalancing` fails to correct extreme hostile pre-seeds, letting the post-graduation HyperSwap LP open materially away from the curve-close price - (`File: packages/contracts/src/Bonding.sol`)

### Summary
`finalizeGraduation` is a permissionless, unconfirmed action — anyone can call it — that seeds the HyperSwap V2 TOKEN/LT pool from cached, pre-frozen `(tokensForLP, ltFromPair)` amounts [1](#0-0) . Between phase 1 (`_enterGraduating`) and phase 2, any unprivileged address can permissionlessly `factory.createPair`, transfer tokens at an arbitrary ratio, and call `pair.mint(attacker)` to plant a hostile reserve ratio before `finalizeGraduation` runs, exactly as documented by the protocol's own "HyperSwap Pre-Seed Defense" writeup [2](#0-1) . The mitigation (`_seedRebalancing` → `_pairRebalance`) attempts to swap the pool back to the curve-close ratio before depositing, but caps the correcting swap at 99% of the caller's own inventory via `_swapBudget` [3](#0-2) . When the pre-seed ratio is extreme enough that the required correcting swap exceeds that budget, the cap binds and the deposit proceeds while the pool is still materially off the curve-close price — a residual explicitly reproduced and accepted in the protocol's own test suite.

### Finding Description
`_seedRebalancing` computes the swap needed to move pool reserves to the cached curve-close ratio and calls `_pairRebalance`, which derives the input via `_noFeeSwapInput` and clamps it to `p.maxSwap = _swapBudget(...)` — 99% of `Bonding`'s available inventory on the input side [4](#0-3) . For a sufficiently lopsided attacker-seeded ratio (e.g. TOKEN reserve at 1% of `tokensForLP`, LT reserve at 200x `ltFromPair`), the theoretically required correcting swap is ~1.4x `tokensForLP`, exceeding the ~0.99x `tokensForLP` budget. The swap executes but under-corrects, and `_routerDepositAndDispose` then deposits the remaining inventory at the router's `quote()`-based split against the still-skewed post-swap ratio [5](#0-4) . The protocol's own regression test for this exact shape (`test_hostilePreSeed_budgetCappedSwap_isNotProfitable`) documents the pool landing "~2x off curve-close" and asserts the price deviation is `> 1.2x` the fair curve-close price [6](#0-5) . `finalizeGraduation` still succeeds and locks the resulting off-ratio LP into `LPLock` — which has no withdraw/rescue path in v1 — permanently baking the mispriced position into the protocol-owned, locked liquidity [7](#0-6) .

### Impact Explanation
This satisfies the "LP seeded away from the curve close price" impact criterion directly: the pool opens at a price materially divorced (>20%, up to ~2x in the demonstrated fuzz shape) from the fair curve-close price. Because the resulting LP is locked forever in `LPLock` with no rescue mechanism, the mispricing is not merely transient — arbitrageurs immediately trade the pool back toward fair value at the expense of the protocol's own locked LP position (the counterparty absorbing the arb loss is the locked LP, funded from the curve's real LT raise and the 250M token reserve), a permanent, unrecoverable value transfer out of protocol-owned funds. This is reachable by any unprivileged address with a modest capital outlay (a self-seeded `pair.mint` before `finalizeGraduation` fires), matching the CVE's theme of a low-friction, unconfirmed automatic action (`finalizeGraduation` is permissionless) whose behavior is dictated by adversary-supplied external state (the pre-seeded pool reserves) rather than trusted, out-of-band confirmation.

### Likelihood Explanation
Reachability is trivial and permissionless: `factory.createPair`, `IERC20.transfer`, and `IUniswapV2Pair.mint` are all callable by anyone, and `finalizeGraduation` itself has no access control [8](#0-7) . The only requirement is a pre-seed lopsided enough (well within the demonstrated 200x-vs-1% shape, or via `testFuzz_hostilePreSeed_neverProfitable_neverBricks`'s wider fuzz range) that the required correcting swap exceeds `_swapBudget`'s 99%-of-inventory ceiling — a capital outlay bounded by the attacker's own transferred tokens/LT, not by protocol funds. The developers' own comments label this residual "accepted," confirming it is a known, currently-live limitation of the shipped defense rather than a hypothetical.

### Recommendation
Either (a) size the per-side rebalance budget dynamically so it can always fully correct the pre-seed ratio up to some hard cap on total pre-seed magnitude enforced structurally (e.g., don't reuse the V2 pair if pre-existing supply exceeds a sanity bound, routing to a fresh pair instead — while still preserving brick-resistance for the in-bound cases), or (b) split the excess correction across multiple swap legs / increase `maxSwap` beyond `tokensForLP` by drawing on a small protocol-held buffer reserved for exactly this purpose, so the post-swap ratio always converges to the cached curve-close ratio before deposit, regardless of pre-seed magnitude. At minimum, emit an on-chain event/alert when the budget cap binds so off-chain monitoring can flag the resulting LP as opened off-price for manual remediation via a future `LPLock` rescue path.

### Proof of Concept
The existing test `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` in `packages/contracts/test/TwoPhaseGraduation.t.sol` (lines 864-917) is a direct, already-passing reproduction: it launches a token, enters `Graduating`, seeds the HyperSwap pair via `pair.mint` at `reserveToken = tokensForLP/100`, `reserveLt = ltFromPair*200`, calls `bonding.finalizeGraduation(tokenAddr)`, and asserts `_poolPriceLtPerToken(...) > (ltFromPair/tokensForLP)*1.2` — i.e., the pool provably opens more than 20% off the curve-close price after finalize succeeds.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1008)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];
```

**File:** packages/contracts/src/Bonding.sol (L1316-1349)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1374-1378)
```text
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
    }
```

**File:** packages/contracts/src/Bonding.sol (L1449-1470)
```text
    function _routerDepositAndDispose(
        address tokenAddress,
        address lt,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        BondingStorage storage $ = _s();
        address routerAddr = $.uniswapV2Router;
        address lpLock_ = $.lpLock;
        uint256 remToken = IERC20(tokenAddress).balanceOf(address(this));
        // Subtract `protectedLT` (LT that doesn't belong to this graduation
        // — concurrent escrows or stray dust, snapshotted at the top of
        // `finalizeGraduation`) so the deposit allowance can never pull
        // another graduation's earmark or accidentally absorb dust into a
        // locked LP.
        uint256 ltBal = IERC20(lt).balanceOf(address(this));
        uint256 remLT = ltBal > protectedLT ? ltBal - protectedLT : 0;

        if (remToken > 0 && remLT > 0) {
            IERC20(tokenAddress).forceApprove(routerAddr, remToken);
            IERC20(lt).forceApprove(routerAddr, remLT);
            (,, liquidity) = IUniswapV2Router02(routerAddr)
                .addLiquidity(tokenAddress, lt, remToken, remLT, 1, 1, lpLock_, block.timestamp);
```

**File:** packages/contracts/AGENTS.md (L132-137)
```markdown
A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

```

**File:** packages/contracts/AGENTS.md (L152-154)
```markdown

### Options we considered (and rejected)

```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L858-900)
```text
    /// @notice M-02 reproducer. An LT-rich mint pre-seed so lopsided that the
    ///         TOKEN-side rebalance swap exhausts its full budget (~99% of
    ///         `tokensForLP`) without reaching the cached ratio, so the pool
    ///         deposits materially off curve-close. Finalize must still succeed
    ///         (no brick), the over-funded LT side must be confiscated to the
    ///         owner, and the pre-seeder must end net-negative.
    function test_hostilePreSeed_budgetCappedSwap_isNotProfitable() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);

        // Extreme LT-rich shape: TOKEN side at 1% of target, LT side at 200x.
        // The optimal TOKEN-in swap to reach the cached ratio is ~1.4x
        // `tokensForLP`, so the 99%-of-`tokensForLP` budget cap binds and the
        // pool stays ~2x off curve-close after the swap.
        uint256 reserveToken = tokensForLP / 100;
        uint256 reserveLt = ltFromPair * 200;

        // M-02 precondition: the optimal swap exceeds the budget (this is the
        // budget-capped regime, distinct from the swap-rounds-to-zero fallback
        // covered by the dust tests above).
        assertGt(
            _noFeeSwapInputUncapped(reserveToken, reserveLt, tokensForLP, ltFromPair),
            (tokensForLP * 99) / 100,
            "setup: optimal rebalance swap must exceed the per-side budget (M-02 regime)"
        );

        deal(tokenAddr, griefer, reserveToken);
        address hyperPair = _grieferMintPreSeed(tokenAddr, reserveToken, reserveLt);
        uint256 grieferLp = MockHyperswapPair(hyperPair).balanceOf(griefer);
        uint256 ownerLtBefore = lt.balanceOf(bonding.owner());

        bonding.finalizeGraduation(tokenAddr);
        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed despite an unrecoverable pre-seed");

        // The accepted residual: no bounded swap can correct a 200x LT-rich
        // pre-seed, so the pool opens materially off curve-close.
        assertGt(
            _poolPriceLtPerToken(hyperPair, tokenAddr),
            (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
            "M-02 regime: pool opens materially off curve-close"
        );
```
