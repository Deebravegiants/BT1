### Title
Donated LT sent to a graduated `Pair` is permanently stuck with no recovery path - ([File: packages/contracts/src/Pair.sol](), [File: packages/contracts/src/Router.sol](), [File: packages/contracts/src/Bonding.sol]())

### Summary
Any unrelated wallet can `IERC20(lt).transfer(pair, amount)` directly to a bonding-curve `Pair` at any time before or during the curve's life. `Pair` only exposes two outbound-asset functions — `transferAsset` and `transferToken` — both gated `onlyRouter`, and `Router`'s only caller-side entry point that invokes `transferAsset` is `graduate(token, amount)`, itself gated to `Bonding`'s `BONDING_ROLE` and called exactly once, with an explicit `amount` argument, during `Bonding.finalizeGraduation` → `_prepareGraduationLiquidity` / `_graduate`. That call deliberately drains only `ltFromPair = assetReserve − virtualLtReserve` — the LT actually raised by the curve — and leaves any donated LT behind in the `Pair` "under the trust assumption that BONDING_ROLE is only ever held by Bonding." [1](#0-0)  Once the token's lifecycle flips to `Graduated`, `Bonding` never calls `Router.graduate` for that token again, and there is no other function anywhere in `Pair`, `Router`, or `Bonding` that can move the pair's residual `assetToken` balance out. The donation is therefore permanently locked in a contract that no longer serves any purpose in the protocol's post-graduation flow (trading has moved to the HyperSwap V2 TOKEN/LT pool).

### Finding Description
`Pair.transferAsset`/`transferToken` are the only withdrawal primitives on the curve `Pair`, and both are `onlyRouter`. [2](#0-1)  `Router.graduate` (invoked once from `Bonding._prepareGraduationLiquidity`) transfers only the curve-computed `ltFromPair` amount out of the pair, explicitly leaving any excess/donated LT balance behind — confirmed by the protocol's own tests, which assert the "donation" remains in the pair after `graduate()` runs. [3](#0-2)  The design docs describe this explicitly: "Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`." [1](#0-0)  After `finalizeGraduation` runs, `info.lifecycle` becomes `Graduated` and the pair's role in the protocol ends — `Router.graduate` is a one-shot call gated to the graduation flow and is never invoked again for that token, so the "reachable via Router's BONDING_ROLE" path referenced in the docs does not actually exist post-graduation. The LT donation is unconditionally and permanently locked, exactly analogous to `donateETH` funds that could never be reclaimed from `OptimismPortal`.

### Impact Explanation
Any unrelated wallet, trader, or creator who mistakenly sends the paired LT directly to a curve `Pair` address (rather than routing through `Zap.buy`/`sell`) has those funds permanently and irrecoverably frozen once the token graduates (or indefinitely if it never graduates). There is no sweep, no rescue, and no owner escape hatch comparable to `FeeVault.sweepDonations()` [4](#0-3)  or the `Bonding`-side `_sweepLTToOwner` used during LP-seeding rebalances. [5](#0-4)  This is a permanent freeze of value that could otherwise be swept to the protocol owner or refunded, mirroring the "stuck ETH" class in the source report.

### Likelihood Explanation
Trivial to trigger — a single unprivileged `IERC20.transfer(pair, amount)` call to a publicly known `Pair` address is sufficient. Since `Pair` addresses are discoverable from `Bonding.getTokenInfo(token).pair`, any wallet holding the LT can reach this at any time, either accidentally (sending to the wrong address) or via wallets/aggregators that don't recognize the curve `Pair` as a non-standard recipient.

### Recommendation
Add a permissionless (or owner-gated) sweep function analogous to `FeeVault.sweepDonations()` that computes `assetBalance() − ltFromPair`-equivalent surplus for a graduated pair and forwards it to the protocol owner, or extend `Router` with a post-graduation `BONDING_ROLE`-gated `sweepResidual(token)` that calls `Pair.transferAsset` for any balance beyond what graduation accounted for.

### Proof of Concept
1. `Bonding.launch(...)` creates `token` and its `Pair` (`pairAddr`).
2. An unrelated wallet calls `IERC20(lt).transfer(pairAddr, X)` — a pure donation, not a curve buy.
3. The token eventually graduates: the threshold-crossing buy fires `Bonding._enterGraduating`, then `finalizeGraduation` runs, calling `Router.graduate(token, ltFromPair)` which drains only the curve-raised LT, per `test_graduate_leavesDonationBehind`. [3](#0-2) 
4. `info.lifecycle` is now `Graduated`; `pairAddr` is never touched again by any contract in the system.
5. `IERC20(lt).balanceOf(pairAddr) == X` forever — no function exists to move it out.

### Citations

**File:** docs/contracts-scope.md (L88-90)
```markdown
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
```

**File:** packages/contracts/src/Pair.sol (L81-93)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }

    function transferToken(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(launchedToken).safeTransfer(recipient, amount);
    }
```

**File:** packages/contracts/test/Router.t.sol (L345-357)
```text
    function test_graduate_leavesDonationBehind() public {
        // The whole point of the new signature: passing an explicit amount
        // means anything `IERC20.transfer`-donated to the pair stays put.
        uint256 raised = 4000 ether;
        uint256 donated = 1500 ether;
        asset.mint(pairAddr, raised + donated);

        vm.prank(bondingRole);
        router.graduate(address(token), raised);

        assertEq(asset.balanceOf(bondingRole), raised, "Only the requested amount is drained");
        assertEq(IPair(pairAddr).assetBalance(), donated, "Donation remains locked in pair");
    }
```

**File:** packages/contracts/src/FeeVault.sol (L147-160)
```text
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
