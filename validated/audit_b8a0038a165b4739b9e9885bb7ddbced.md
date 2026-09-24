This confirms the analog: LT donated directly to a curve `Pair` before graduation is explicitly designed to remain permanently locked in the pair, with no rescue path at all — even weaker than the original M-7 bug's "cancel the stream" escape hatch. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Accidental/donated LT sent directly to a pre-graduation curve `Pair` is permanently unrecoverable — no rescue path exists at all - ([File: packages/contracts/src/Router.sol], [File: packages/contracts/src/Pair.sol])

### Summary
Anyone can send extra LT directly to a token's curve `Pair` via `IERC20(lt).transfer(pair, amount)` before the token graduates. Unlike NounsDAO's `rescueERC20`, alt.fun's `Pair`/`Bonding`/`Router` stack has **no rescue function of any kind** for LT sitting in a not-yet-graduated `Pair`. The only path that can ever move LT out of the `Pair` is `Router.graduate`, callable exclusively from `Bonding._prepareGraduationLiquidity` during `finalizeGraduation`, and even then it deliberately excludes any donated LT (it drains only `ltFromPair = assetReserve - virtualLtReserve`, the stored-reserve amount, leaving the donated surplus behind in the `Pair` forever).

### Finding Description
`Router.graduate` is `onlyRole(BONDING_ROLE)` and is only ever invoked once per token, from `_prepareGraduationLiquidity`, with an `amount` computed purely from the pair's *stored* reserves, never its live balance: [4](#0-3) 

`Pair.transferAsset` (the only function capable of moving LT out of the pair) is gated `onlyRouter`, and `Router` exposes it solely via `sell` and `graduate` — both requiring `BONDING_ROLE`: [5](#0-4) 

Because `graduate` intentionally computes `amount` from `assetReserve - virtualLtReserve` (stored state) rather than `assetBalance()` (live balance), any LT donated directly to the pair is excluded from the drain by design, and is asserted by the test suite to remain in the pair permanently: [6](#0-5) 

There is no `rescueERC20`/admin-sweep function anywhere in `Bonding`, `Router`, or `Pair` that can reach a live `Pair` balance directly — the only sweep-like functions in the codebase (`FeeVault.sweepDonations`, `Bonding._sweepLTToOwner`) operate on `Bonding`'s own balance, not the `Pair`'s. Consequently, LT sent to a pre-graduation `Pair` — whether by mistake (a user fat-fingering a transfer to the pair address instead of using `Zap.buy`) or by a third party — is locked in the `Pair` contract with zero recovery mechanism, for the entire lifetime of the token if it never graduates, and permanently even after graduation (the docs/tests explicitly state the donated LT "must remain locked in the curve pair").

### Impact Explanation
This is a stricter version of the reported bug class: NounsDAO's Payer at least had the disruptive option of cancelling the stream to recover accidental funds. Here, there is **no option at all** — not even a disruptive one — to recover LT accidentally or maliciously donated to a curve `Pair`. If a token never meets a graduation trigger (e.g., a low-volume/dead token that never sells out its 750M curve supply and never reaches the $9K USD threshold), any LT sent to its `Pair` is frozen indefinitely with total finality. Even for tokens that do graduate, the donated LT is explicitly excluded from the LP and stays locked in the (now-inert) curve `Pair` forever, unreachable by any function in the codebase. This is a permanent freezing of third-party or creator funds.

### Likelihood Explanation
Reachable by any unprivileged wallet via a single `IERC20(lt).transfer(pairAddr, amount)` call — no special access, timing, or front-running required. Users can trivially mis-target this transfer instead of calling `Zap.buy`, and the protocol's own documentation/tests confirm this is an anticipated, tested-for scenario that is deliberately left unrecovered rather than treated as a bug.

### Recommendation
Add a permissioned or permissionless rescue path analogous to `FeeVault.sweepDonations()` for the `Pair` contract: expose a `Router`-mediated (or `Bonding`-mediated) function that computes `assetBalance() - assetReserve` (the true donation surplus over stored reserves) and sweeps it to a designated recipient (e.g., protocol owner or original sender, if trackable) — without needing to touch `assetReserve`, `tokenReserve`, or trigger/alter graduation. This mirrors the fix pattern the report recommends for NounsDAO's `rescueERC20`, adapted to alt.fun's stored-reserve vs. live-balance donation-detection pattern already used elsewhere (e.g., `Bonding._sweepLTToOwner`, `FeeVault.sweepDonations`).

### Proof of Concept
1. `Bonding.launch(...)` creates `tokenAddr` paired against `lt`, creating `pairAddr` via `Factory`.
2. A user, intending to buy, mistakenly calls `IERC20(lt).transfer(pairAddr, 1000e18)` directly instead of `Zap.buy(tokenAddr, ...)`.
3. `Pair.getReserves()` / `assetReserve` is unchanged (no `mint`/`swap` was called), so the transferred LT sits as pure excess balance: `Pair.assetBalance() > assetReserve`.
4. If the token never reaches `canGraduate()` (e.g., trading dies out), there is no function anywhere — not `Router.graduate` (unreachable, gated to post-`Curve` lifecycle and driven only by `Bonding`), not `Pair.transferAsset` (only callable by `Router`), not any admin function — that can move this LT out. It is provably permanently frozen, confirmed by `test_inv_donation_zeroGapPreserved` in `packages/contracts/test/GraduationInvariants.t.sol`, which asserts `IPair(pairAddr).assetBalance() == donation` even *after* legitimate graduation completes.

### Citations

**File:** docs/contracts-scope.md (L89-89)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
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

**File:** packages/contracts/test/GraduationInvariants.t.sol (L512-534)
```text
    /// @dev When graduation eventually fires legitimately on a curve that
    ///      has been donated to, the LP must still open at the curve's last
    ///      marginal price (zero-gap), and the donation must remain locked
    ///      in the curve pair (not flow into the LP).
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

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```

**File:** packages/contracts/src/Pair.sol (L81-86)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }
```
