Based on thorough review of the graduation/LP-seeding subsystem — the part of alt.fun's contracts structurally closest to the Galaxy CVE's "attacker overwrites/replaces protected data" bug class (pre-seeding or pre-creating the HyperSwap TOKEN/LT pair before the protocol writes its own state into it) — I did not find a reachable, currently-unmitigated analog.

The exact attack shape the CVE maps onto (an unprivileged actor front-running/tampering with data that the protocol later relies on as authoritative) is `Bonding.finalizeGraduation`'s HyperSwap V2 pair seeding, which is explicitly documented and tested as hardened against every pre-seed shape:

- Pre-creating the pair and donating/minting dust at a hostile ratio is handled by the three-regime defense in `_seedUniswapV2Direct` (empty/dust-sync, pure-donation via `skim`, and hostile-mint via `_pairRebalance` + `_routerDepositAndDispose`), which is proven brick-proof and bounded on attacker P&L. [1](#0-0) 
- `finalizeGraduation` snapshots `protectedLT` before touching the balance, so cross-token/concurrent-graduation LT residue can't be swept or deposited into the wrong graduation's LP — the exact "data belonging to someone else gets silently consumed/overwritten" failure mode. [2](#0-1) 
- `LPLock.recordLock` is a one-shot sentinel (`lockedAt != 0` guard) callable only by allowlisted lockers, so a token's LP lock record can never be overwritten once set. [3](#0-2) 
- These properties are covered by an extensive regression suite (`test/TwoPhaseGraduation.t.sol`) including dust-mint, sync-dust, concurrent-graduation, and meaningful-pre-seed shapes. [4](#0-3) [5](#0-4) 

Other in-scope surfaces (`FeeVault.claim`/`claimProtocol`/`sweepDonations`, `Zap.createToken`/`buy`/`sell`, `Bonding.transferCreator`, `Factory.createPair`) either enforce strict one-shot/underfund/ownership invariants or are gated by permissions that make the CVE's "replace shared data" pattern unreachable by an unprivileged caller. [6](#0-5) [7](#0-6) 

#No Vulnerability found for this question.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1010-1025)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1132-1183)
```text
    /// @dev LP-seeding into the HyperSwap pair, hardened against hostile
    ///      pre-seeds. Three regimes:
    ///
    ///        1. **No LP minted yet — `totalSupply == 0` (~99% of
    ///           graduations).** A pristine empty pair, or a dust pre-seed
    ///           (`transfer(pair, dust) + sync()` leaves `reserves > 0` but
    ///           `totalSupply == 0`). Direct mint at exactly
    ///           `(tokensForLP, ltFromPair)` — V2's first-liquidity branch
    ///           makes those amounts the sole price input, so the pool opens
    ///           at the curve-close ratio and any dust becomes reserves with
    ///           no LP claim.
    ///        2. **Pure-donation pre-seed.** Attacker `transfer`'d to the
    ///           pair without `mint` (balance > 0, reserves == 0).
    ///           `pair.skim(address(this))` pulls the donation into
    ///           `Bonding`; path then collapses to (1). Donated TOKEN is
    ///           burned alongside the empty-pair mint; donated LT is
    ///           handled by `finalizeGraduation`'s post-bookend
    ///           `_sweepLTToOwner` (which uses `protectedLT` snapshotted
    ///           BEFORE skim, so the donation is correctly classified as
    ///           rebalance residue rather than concurrent-graduation
    ///           escrow). NEVER routed to `LPLock` — `LPLock` has no
    ///           rescue path in v1, so anything that lands there is
    ///           permanently stuck.
    ///        3. **Mint pre-seed.** Attacker called `pair.mint` against a
    ///           self-funded seed, baking a hostile (TOKEN, LT) ratio into
    ///           the pool. Without intervention `pair.mint(lpLock)`'s
    ///           `min(amount0·S/r0, amount1·S/r1)` formula would (a) open
    ///           the LP off curve-close-price and (b) donate the larger arm
    ///           to the attacker's pre-existing LP. We rebalance via a
    ///           direct `pair.swap` toward the curve-close ratio, then
    ///           deposit the remaining inventory via the router's
    ///           `quote()`-based `addLiquidity` — which only pulls the
    ///           optimal amounts at the post-swap ratio, so neither side
    ///           becomes a `min()` donation. Off-ratio TOKEN remainder is
    ///           burned; off-ratio LT remainder is auto-swept to the owner
    ///           by `finalizeGraduation`'s post-bookend (see its natspec).
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
    ///      Brick resistance: the rebalance swap input is capped at our
    ///      per-side budget; a swap whose fee-charging `getAmountOut` would
    ///      round to zero (which would otherwise revert `pair.swap` with
    ///      `INSUFFICIENT_OUTPUT_AMOUNT`) is replaced by the direct-mint
    ///      fallback; the deposit uses `addLiquidity(min=1, min=1)`; and the
    ///      empty/donation regimes don't touch the router or `pair.swap`. So
    ///      a hostile pre-seed of any shape cannot DoS `finalizeGraduation`.
```

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L243-289)
```text
    function test_brick_resistance_frontRun_dust_seed() public {
        (address tokenAddr,) = _launchToken();

        // Griefer buys some tokens on the curve to use as ammo for the
        // dust-seed attack later. Modest amount so they remain a holder
        // without graduating the curve themselves.
        if (!bonding.isRouter(griefer)) bonding.addRouter(griefer);
        uint256 grieferBuy = _smallBuyLt();
        lt.mintDirect(griefer, grieferBuy);
        vm.startPrank(griefer);
        lt.approve(address(curveRouter), grieferBuy);
        bonding.buy(grieferBuy, tokenAddr, 0, griefer);
        vm.stopPrank();
        uint256 grieferTokens = Token(tokenAddr).balanceOf(griefer);
        assertTrue(grieferTokens > 0);

        // Drive the curve into the `Graduating` window.
        _enterGraduating(tokenAddr);

        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);
        assertTrue(tokensForLP > 0 && ltFromPair > 0);

        // Pre-create the HyperSwap pair, deposit dust from both sides, mint LP
        // to the griefer's address. The pair now has non-zero reserves at a
        // skewed (and ultimately economically-destructive-to-the-griefer)
        // price. Under the OLD `_requirePairEmpty` design this would brick
        // finalize forever.
        MockHyperswapFactory hsFactory = MockHyperswapFactory(hyperswapRouter.factory());
        address hyperPair = hsFactory.createPair(tokenAddr, address(lt));
        lt.mintDirect(griefer, 1 ether);

        vm.startPrank(griefer);
        // Use a tiny fraction of griefer's curve-bought tokens as dust.
        IERC20(tokenAddr).transfer(hyperPair, 1 ether);
        lt.transfer(hyperPair, 1 ether);
        MockHyperswapPair(hyperPair).mint(griefer);
        vm.stopPrank();

        // The protocol must still be able to finalize despite the dust.
        bonding.finalizeGraduation(tokenAddr);

        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed despite front-run dust seed");
        assertEq(bonding.graduatedPair(tokenAddr), hyperPair, "must reuse the front-run pair");

        uint256 lockedLp = MockHyperswapPair(hyperPair).balanceOf(address(lpLockContract));
        assertTrue(lockedLp > 0, "lpLock must hold the protocol LP");
    }
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L291-343)
```text
    /// @notice A pre-created pair flipped to `reserves > 0 && totalSupply == 0`
    ///         via `transfer(pair, 1 wei) + sync()` must still graduate at the
    ///         cached curve-close ratio, not the attacker's synced 1:1. The
    ///         `totalSupply() == 0` regime gate routes this shape to the direct
    ///         mint; the attacker, having minted no LP, holds none.
    function test_syncDust_preseed_opensAtCurveRatio() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);
        assertTrue(tokensForLP > 0 && ltFromPair > 0);
        assertNotEq(tokensForLP, ltFromPair, "test setup should have non-1:1 target ratio");

        MockHyperswapFactory hsFactory = MockHyperswapFactory(hyperswapRouter.factory());
        address hyperPair = hsFactory.createPair(tokenAddr, address(lt));

        lt.mintDirect(griefer, 1);
        deal(tokenAddr, griefer, 1);
        vm.startPrank(griefer);
        IERC20(tokenAddr).transfer(hyperPair, 1);
        lt.transfer(hyperPair, 1);
        MockHyperswapPair(hyperPair).sync();
        vm.stopPrank();

        // Sanity-check the attack precondition: reserves non-zero but no
        // LP minted — the gap the fix closes.
        (uint112 preR0, uint112 preR1,) = MockHyperswapPair(hyperPair).getReserves();
        assertGt(uint256(preR0), 0);
        assertGt(uint256(preR1), 0);
        assertEq(MockHyperswapPair(hyperPair).totalSupply(), 0);

        bonding.finalizeGraduation(tokenAddr);

        (uint112 r0, uint112 r1,) = MockHyperswapPair(hyperPair).getReserves();
        bool tokenIs0 = MockHyperswapPair(hyperPair).token0() == tokenAddr;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

        // Pool MUST open at the curve-close ratio (`tokensForLP : ltFromPair`),
        // NOT at the attacker's synced 1:1. The 1-wei dust contributes at most
        // 1 wei of skew vs. the target reserves, well inside `1e12` (= 1e-6).
        assertApproxEqRel(
            reserveToken * ltFromPair,
            reserveLT * tokensForLP,
            1e12,
            "pool must open at curve-close ratio despite sync-dust pre-seed"
        );

        // Protocol LP is locked.
        uint256 lockedLp = MockHyperswapPair(hyperPair).balanceOf(address(lpLockContract));
        assertGt(lockedLp, 0, "lpLock must hold the protocol LP");
        // Attacker holds no LP — they gifted dust to the locked LP.
        assertEq(MockHyperswapPair(hyperPair).balanceOf(griefer), 0, "attacker must hold no LP");
    }
```

**File:** packages/contracts/src/FeeVault.sol (L101-160)
```text
    function accrue(
        address token,
        address creator,
        uint256 creatorAmount,
        uint256 protocolAmount,
        bool isBuy
    ) external onlyDepositor {
        FeeVaultStorage storage $ = _s();
        if (creatorAmount > 0) {
            if (creator == address(0)) revert ZeroAddress();
            $.creatorBalance[creator] += creatorAmount;
            $.totalAccruedCreator += creatorAmount;
            $.lifetimeCreatorEarned[creator] += creatorAmount;
        }
        if (protocolAmount > 0) {
            $.protocolBalance += protocolAmount;
            $.lifetimeProtocolEarned += protocolAmount;
        }
        if ($.usdc.balanceOf(address(this)) < $.totalAccruedCreator + $.protocolBalance) {
            revert UnderfundedAccrual();
        }
        emit FeeAccrued(token, creator, creatorAmount, protocolAmount, isBuy);
    }

    // ─── Claims ──────────────────────────────────────────────────────────

    function claim() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.creatorBalance[msg.sender];
        if (amount == 0) revert NothingToClaim();
        $.creatorBalance[msg.sender] = 0;
        $.totalAccruedCreator -= amount;
        $.usdc.safeTransfer(msg.sender, amount);
        emit CreatorFeesClaimed(msg.sender, amount);
    }

    function claimProtocol() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.protocolBalance;
        if (amount == 0) revert NothingToClaim();
        $.protocolBalance = 0;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit ProtocolFeesClaimed(feeTo_, amount);
    }

    /// @notice Sweep unbacked USDC (donations) to `feeTo`. Required because
    ///         direct USDC transfers would otherwise inflate `balanceOf` above
    ///         the accrual tally and silently mask the `accrue` underfund
    ///         check. Permissionless — funds always go to the admin-set `feeTo`.
    function sweepDonations() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        uint256 backed = $.totalAccruedCreator + $.protocolBalance;
        uint256 balance = $.usdc.balanceOf(address(this));
        if (balance <= backed) revert NothingToClaim();
        amount = balance - backed;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit DonationsSwept(feeTo_, amount);
    }
```

**File:** packages/contracts/src/Factory.sol (L38-55)
```text
    function createPair(
        address tokenA,
        address tokenB
    ) external onlyRole(BONDING_ROLE) returns (address) {
        if (tokenA == address(0) || tokenB == address(0)) revert ZeroAddress();
        if (router == address(0)) revert NoRouter();
        if (_pairs[tokenA][tokenB] != address(0)) revert PairExists();

        Pair pair = new Pair(router, tokenA, tokenB);
        _pairs[tokenA][tokenB] = address(pair);
        _pairs[tokenB][tokenA] = address(pair);

        pairFor[tokenA] = address(pair);
        ltFor[tokenA] = tokenB;

        emit PairCreated(tokenA, tokenB, address(pair), ++pairCount);
        return address(pair);
    }
```
