### Title
Direct token/LT donations to a curve `Pair` are unrecoverably burned or permanently locked when `Bonding.finalizeGraduation` fires, with no balance-check gate analogous to `closeOngoing` - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The external report's bug class — a state-closing function (`closeOngoing`) that transitions status without checking whether the contract still holds a balance, permanently stranding funds — maps onto alt.fun's two-phase graduation flow. `Bonding.finalizeGraduation` and its helper `_prepareGraduationLiquidity` unconditionally burn any real TOKEN balance sitting in the curve `Pair` and exclude any donated LT from the LP, all without any check for whether that balance belongs to a legitimate depositor rather than curve inventory.

### Finding Description
Any unprivileged address can send TOKEN or LT directly to a live curve `Pair` via a plain ERC20 `transfer` (a reachable path explicitly in scope: "direct ERC20 transfers of a launched Token or an LT into Pair, Bonding, Zap or FeeVault").

When graduation later finalizes:
- `_prepareGraduationLiquidity` reads `unsoldBurned = IPair(pairAddr).tokenBalance()` and burns the entire live TOKEN balance of the pair unconditionally [1](#0-0) . This includes any TOKEN a user mistakenly or intentionally transferred directly to the pair — it is burned along with genuine unsold curve inventory, with no distinction and no recovery path.
- For the LT side, `Router.graduate` drains only the curve-computed `ltFromPair`, deliberately leaving any donated LT behind in the pair [2](#0-1) . The documentation for this function states plainly that the leftover LT is "unreachable" once the token's lifecycle passes `Curve`, because the only caller of `Router.graduate` (`Bonding._prepareGraduationLiquidity`) is itself gated to the `Curve` lifecycle stage [3](#0-2) .
- `finalizeGraduation` transitions `info.lifecycle` to `Graduated` and deletes `pendingGraduation` without any check that the pair's real balances are fully accounted for or drained back to their rightful owner [4](#0-3) .

This exactly mirrors the reported bug class: a terminal state transition (`closeOngoing` → `Graduated`) proceeds without verifying/handling any residual balance, and once the transition completes, there is no code path left to reach or recover that balance — `Bonding.buy`/`sell` revert post-`Curve`, and `Router.graduate`/`Pair.transferAsset` are unreachable once the lifecycle has advanced past `Curve`.

### Impact Explanation
Confirmed by the project's own invariant tests (`test_inv_donation_zeroGapPreserved`, `GraduationInvariants.t.sol`), any LT sent directly to a curve pair before graduation remains stuck in the pair after graduation completes, and any TOKEN sent directly to the pair is unconditionally burned [5](#0-4) . This is a genuine permanent loss/freezing of funds for whoever made that transfer — matching the Medium-severity "permanent freezing of funds" impact class from the rules.

### Likelihood Explanation
Reaching this state requires nothing more than a plain `ERC20.transfer` to a publicly-known `Pair` address by any unprivileged wallet (accidental or deliberate), followed by the token eventually graduating (which happens automatically via `triggerGraduation`/buy-triggered `_enterGraduating` and is itself permissionless). No special privileges, timing races, or contract interactions are required, making this readily reachable, though the loss is limited to whatever amount was donated (self-inflicted for TOKEN donations, or an LT sent in error).

### Recommendation
Add an explicit sweep/rescue path, mirroring the report's suggested fix of gating the terminal state transition on a zero-balance check (or, symmetrically, adding a recovery mechanism): before/at `finalizeGraduation`, allow the protocol (or the depositor, if attributable) to reclaim any TOKEN/LT balance in the curve `Pair` that exceeds the curve's own accounted reserves, rather than unconditionally burning TOKEN and silently stranding LT. At minimum, document this as an accepted, permanent loss for careless direct transfers (which the code comments partially do already) — but since the project's own design intentionally treats this as "locked" rather than recoverable, it should be evaluated by the team as an accepted risk vs. a fix, given it fits the audit's "permanent freezing of funds" impact class.

### Proof of Concept
1. Launch a token via `Bonding.launch`, obtaining `tokenAddress` and its curve `Pair` at `pairAddr`.
2. From any unprivileged EOA, mint/hold LT and call `IERC20(lt).transfer(pairAddr, X)` — a pure donation with no `Pair.mint` call, matching the documented and tested "pure LT donation" scenario [6](#0-5) .
3. Drive the curve to graduation via ordinary buys (`Bonding.buy` / `Zap.buy`) until `canGraduate` is true, then call `triggerGraduation` and `finalizeGraduation`.
4. Post-graduation, assert `IPair(pairAddr).assetBalance() == X` — exactly as the existing test `test_inv_donation_zeroGapPreserved` verifies [5](#0-4)  — confirming the donated LT sits, permanently unreachable, in a `Pair` that no longer accepts any `Router`-mediated interaction because `Bonding`'s lifecycle has advanced past `Curve`.
5. Symmetrically, transferring TOKEN directly to `pairAddr` before graduation results in it being counted into `unsoldBurned` and unconditionally destroyed at finalize time [1](#0-0) .

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1073-1080)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
```

**File:** packages/contracts/src/Router.sol (L184-211)
```text
    /// @notice Transfer exactly `amount` of LT out of the pair to the caller.
    ///         Called by `Bonding._prepareGraduationLiquidity` during graduation
    ///         with `amount = stored assetReserve - virtualLtReserve` (i.e. the
    ///         real LT raised by the curve, excluding the virtual seed).
    /// @dev    Donation-resistant: passing an explicit `amount` instead of
    ///         draining `assetBalance()` ensures any LT that was donated
    ///         directly to the pair via `IERC20.transfer` is left behind and
    ///         excluded from LP seeding.
    ///
    ///         "Locked" here is a trust-assumption claim, not an on-chain
    ///         guarantee. `Pair.transferAsset` is gated by `onlyRouter`, and
    ///         `Router` only exposes it via this function and `sell`. Both
    ///         require `BONDING_ROLE`, which only `Bonding` holds. `Bonding`
    ///         in turn only calls `graduate` from
    ///         `_prepareGraduationLiquidity` — which is unreachable once the
    ///         token's lifecycle has flipped past `Curve`. So the leftover
    ///         is unreachable as long as (a) `BONDING_ROLE` is not granted
    ///         to any other address, and (b) future `Bonding` upgrades
    ///         preserve the lifecycle gate.
    function graduate(
        address token,
        uint256 amount
    ) external onlyRole(BONDING_ROLE) {
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        IPair(pairAddr).transferAsset(msg.sender, amount);
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L481-489)
```text
        uint256 donation = _ltForUsd(thresholdUsd * 5);

        address attacker = makeAddr("attacker");
        lt.mintDirect(attacker, donation);
        vm.prank(attacker);
        IERC20(address(lt)).transfer(pairAddr, donation);

        assertFalse(bonding.canGraduate(tokenAddr), "fresh curve must not be graduatable from a pure LT donation");
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L516-534)
```text
    function test_inv_donation_zeroGapPreserved() public {
        (address tokenAddr, address pairAddr) = _launchToken(_defaultSeedLt());
        _buy(tokenAddr, trader, _ltStageBeforeGraduation());

        uint256 donation = _ltForUsd(bonding.graduationThresholdUsd());
        address attacker = makeAddr("attacker");
        lt.mintDirect(attacker, donation);
        vm.prank(attacker);
        IERC20(address(lt)).transfer(pairAddr, donation);

        lt.setExchangeRate(_ratePumpForStagedGraduation());
        GraduationSnapshot memory s = _graduateAndCapture(tokenAddr, pairAddr, trader2, _ltGraduationTrigger());

        _assertZeroGap(s);
        _assertParabolaCap(s);
        _assertConservation(s);

        assertEq(IPair(pairAddr).assetBalance(), donation, "donated LT must remain locked in the curve pair");
    }
```
