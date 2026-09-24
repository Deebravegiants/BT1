### Title
Donated LT Permanently Locked in Graduated `Pair` Contracts With No Rescue Path - ([File: packages/contracts/src/Pair.sol, packages/contracts/src/Router.sol, packages/contracts/src/Bonding.sol])

### Summary
Any unprivileged actor can send LT directly to a token's `Pair` contract via `IERC20.transfer`. This donated LT never enters the `Pair`'s stored `assetReserve`, so it is excluded from graduation's `ltFromPair` calculation and never drained by `Router.graduate`. Once the token graduates (`Bonding.finalizeGraduation` flips `lifecycle` to `Graduated`), the only code path capable of pulling LT out of the `Pair` — `Router.graduate`, gated to `BONDING_ROLE` and callable only from `Bonding._prepareGraduationLiquidity` — becomes permanently unreachable for that token. The donated LT is stuck in the abandoned curve `Pair` forever, exactly analogous to the reported `LiquidationRow` issue where non-liquidatable reward tokens have no function to distribute or rescue them.

### Finding Description
Direct LT donations to a `Pair` are explicitly excluded from graduation accounting by design. `Router.graduate` is defined with a donation-resistant explicit `amount` parameter: [1](#0-0) 

The natspec on `graduate` itself states the leftover is "locked" only as a trust assumption, not an on-chain guarantee, and is only reachable via `Bonding._prepareGraduationLiquidity`, which is "unreachable once the token's lifecycle has flipped past `Curve`": [2](#0-1) 

`Bonding._prepareGraduationLiquidity` computes `ltFromPair` purely from the stored `assetReserve` minus the recovered virtual reserve — donated LT (which only changes real balance, not stored reserve) is mathematically excluded from the amount drained: [3](#0-2) 

Once `finalizeGraduation` runs, `info.lifecycle` is set to `Lifecycle.Graduated` and `pendingGraduation` is deleted, permanently closing off the only code path (`triggerGraduation`/`_enterGraduating` → `_prepareGraduationLiquidity` → `Router.graduate`) that could ever call `Pair.transferAsset` for that token: [4](#0-3) 

The project's own documentation and tests confirm this is a known, accepted design gap rather than a defended invariant — donated LT "remains locked in the curve pair" and is "reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`": [5](#0-4) [6](#0-5) 

There is no `sweep`, `rescue`, or `skim`-equivalent function exposed on `Pair` or `Bonding` for a token that has already graduated — `_sweepLTToOwner` only operates on `Bonding`'s own balance during `finalizeGraduation`, not on LT sitting inside a graduated `Pair`: [7](#0-6) 

`Pair.transferAsset` itself is gated by `onlyRouter`, with no owner/creator escape hatch: [8](#0-7) 

### Impact Explanation
Any LT donated (accidentally or intentionally) to a curve `Pair` after the token has already graduated (or more generally, LT that lands in the pair and is never captured by a subsequent `ltFromPair` calculation because the pending graduation snapshot is already frozen) becomes permanently frozen with no recovery mechanism whatsoever. This is a permanent freezing of funds — LT that could belong to the depositor, the protocol, or downstream LP participants is trapped in an inert contract forever, matching the "permanent freezing of trader, creator or LP funds" impact bar. LT is itself a valuable, appreciating leveraged asset (not a worthless dust token), so this is a real economic loss, not a no-impact quirk.

### Likelihood Explanation
Reaching this state requires only a standard unprivileged `IERC20.transfer` of LT to a known `Pair` address — no special role, no timing precision beyond "after this token has graduated," and no interaction with any other privileged component. Because `Pair` addresses are permanently associated with a specific graduated token and remain live ERC20-holding contracts indefinitely, this can happen at any point post-graduation via user error (e.g., mistakenly sending LT to the old curve pair instead of the new HyperSwap pair) or deliberate griefing, and once it happens it is irreversible.

### Recommendation
Add a permissionless-but-safe sweep function reachable after a token's lifecycle is `Graduated` (e.g., on `Bonding` or `Pair`) that transfers any LT balance in the `Pair` beyond its now-permanently-zero stored reserves to a designated recipient (protocol owner, or split to LP/creator), mirroring the `_sweepLTToOwner` pattern already used inside `finalizeGraduation`, but scoped to post-graduation `Pair` balances rather than only `Bonding`'s own balance.

### Proof of Concept
1. Launch a token via `Bonding.launch`, creating `Token`/`Pair` as usual.
2. Trade the curve up to graduation and call `finalizeGraduation` — `info.lifecycle` becomes `Graduated`, `pendingGraduation` is deleted (`packages/contracts/src/Bonding.sol:1000-1034`).
3. Any address (no role required) calls `IERC20(lt).transfer(pairAddr, X)`, sending LT directly into the now-graduated, abandoned `Pair` contract.
4. Attempt to recover `X`: `Router.graduate` can only be called from `Bonding._prepareGraduationLiquidity`, which is gated by `info.lifecycle != Lifecycle.Curve` checks in `triggerGraduation`/`_executeBuy` and is therefore unreachable for a `Graduated` token; `Pair.transferAsset` is `onlyRouter`-gated with no other caller; no sweep function targeting a graduated `Pair`'s LT balance exists anywhere in `Bonding.sol`, `Router.sol`, or `Pair.sol`.
5. `X` LT is permanently stuck in `pairAddr` with no possible on-chain retrieval path.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1036-1052)
```text
    /// @dev Send LT held by this contract above `keep` to the owner,
    ///      emitting `LTRescued`. Called at the end of
    ///      `finalizeGraduation` with `keep = protectedLT` (any escrow
    ///      that doesn't belong to this graduation), so only THIS
    ///      graduation's rebalance residue lands on the owner. No-op on
    ///      the empty-pair fast path (nothing to sweep).
    function _sweepLTToOwner(
        address lt,
        uint256 keep
    ) internal {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        if (bal <= keep) return;
        uint256 amount = bal - keep;
        address recipient = owner();
        IERC20(lt).safeTransfer(recipient, amount);
        emit LTRescued(lt, recipient, amount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
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

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

**File:** docs/contracts-scope.md (L89-89)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
```

**File:** docs/contracts-scope.md (L103-103)
```markdown
| 4 | Pair drained | `tokenBalance() == 0` post-graduation. `assetBalance() == 0` only when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair. |
```

**File:** packages/contracts/test/Pair.t.sol (L152-164)
```text
    function test_transferAsset_sendsAssetToken() public {
        vm.prank(routerAddr);
        uint256 amount = 100 ether;
        pair.transferAsset(recipient, amount);

        assertEq(asset.balanceOf(recipient), amount);
    }

    function test_transferAsset_revertsForNonRouter() public {
        vm.prank(stranger);
        vm.expectRevert(Pair.OnlyRouter.selector);
        pair.transferAsset(recipient, 100 ether);
    }
```
