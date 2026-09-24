This confirms the analog: any LT directly donated to a curve `Pair` (before graduation) is deliberately excluded from graduation drain and becomes permanently unreachable once the token's lifecycle passes `Curve`, since `Router.graduate` is the only caller of `Pair.transferAsset` gated by `BONDING_ROLE`, and `Bonding` only invokes it once from `_prepareGraduationLiquidity`.### Title
Direct LT donations to a bonding-curve `Pair` become permanently frozen once the token graduates - ([File: packages/contracts/src/Router.sol])

### Summary
Any unrelated wallet can `IERC20.transfer` a BounceTech LT directly to a token's curve `Pair` before graduation. That donated LT is intentionally excluded from the graduation drain and LP seeding, and after graduation there is no remaining code path that can ever move it out of the `Pair` — the funds are permanently locked, mirroring the reported "claimed value has no withdraw path" bug class.

### Finding Description
`Pair.transferAsset` (the only function that can move the LT reserve asset out of a `Pair`) is gated `onlyRouter`, and `Router.sol` only exposes it through two callers: `sell()` and `graduate()`, both restricted to `BONDING_ROLE`. [1](#0-0) [2](#0-1) 

`Router.graduate(token, amount)` is called by `Bonding._prepareGraduationLiquidity` with an *explicit* amount — `ltFromPair = storedAssetReserve - virtualLtReserve` — deliberately excluding anything donated directly to the pair via `IERC20.transfer`, so donated LT is left behind in the pair rather than drained or folded into the LP: [3](#0-2) 

This is confirmed by the test suite itself, which explicitly asserts the donation "remains locked in pair": [4](#0-3) 

`Router.graduate` is only ever invoked once per token, from `_prepareGraduationLiquidity` in phase 1 of graduation (`_enterGraduating`), which is unreachable once the token's `lifecycle` state has moved past `Curve`. The project's own documentation acknowledges this is a one-shot, non-recoverable state: [5](#0-4) 

Once the token graduates (`lifecycle: Curve → Graduating → Graduated`), no further code path in `Bonding`, `Router`, or `Pair` can ever call `Pair.transferAsset` for that pair again — `BONDING_ROLE` is (per design and deploy assumption) never granted to anyone else, and `Bonding` itself has no post-graduation sweep/rescue function targeting the exhausted curve `Pair`. The donated LT is therefore permanently stranded in a contract that has no withdrawal mechanism whatsoever, exactly analogous to `QuailFinance.claimMyContractGas()` depositing funds into a contract with no corresponding withdraw function.

### Impact Explanation
This is a permanent freezing of funds bug (not theft): any LT sent directly to a curve `Pair` — whether by accidental user error, a well-meaning "donation," or a griefing action — is locked forever the moment the token graduates, with zero recovery path anywhere in the deployed contract set. The magnitude is unbounded: an attacker or a mistaken user can send an arbitrary amount of LT (which itself represents real leveraged, appreciating collateral) to any pre-graduation pair, and it is gone permanently once that token's curve exhausts and graduates. This matches the report's "medium risk, funds locked forever" classification, and the project's own AGENTS.md/tests explicitly document (rather than fix) this as an accepted trust-based limitation ("Locked here is a trust-assumption claim, not an on-chain guarantee").

### Likelihood Explanation
Reachable by any unprivileged wallet with a single `IERC20.transfer(pairAddress, amount)` call to a live curve `Pair` — no special permissions, no timing games, and no interaction with `Bonding`/`Zap`/`Router` required. Every bonding-curve token eventually graduates (via the USD trigger or the deterministic supply-exhaustion trigger), so the "lock" condition is not a rare edge case — it fires on every token that ever donates LT and later graduates, which per the docs happens for essentially all successful tokens.

### Recommendation
Add a post-graduation, permissioned or permissionless sweep function (e.g., `Bonding.sweepPairDonation(token, recipient)`) that reads the leftover `Pair.assetBalance()` after `lifecycle == Graduated` and transfers it out via a new `Router` function gated the same way `graduate()` is, directing the funds to a designated recipient (protocol treasury, or ideally the original donor if attributable via event logs). Alternatively, disallow/detect pre-graduation donations more proactively (e.g., periodic sync/sweep during the `Curve` phase) so stranded LT never survives into the post-graduation dead state.

### Proof of Concept
1. `Zap.createToken(...)` launches a token; its `Pair` is created and enters `Lifecycle.Curve`.
2. Any wallet (not a trader on the curve) calls `IERC20(lt).transfer(pairAddr, DONATION_AMOUNT)` directly against the LT contract, as demonstrated in `test_graduate_leavesDonationBehind`: [4](#0-3) 
3. Trading continues normally; eventually the curve hits the USD or supply graduation trigger, and `Bonding._enterGraduating` → `_prepareGraduationLiquidity` computes `ltFromPair` (excluding the donation) and calls `Router.graduate(token, ltFromPair)`, draining only the curve-raised LT.
4. `Bonding.finalizeGraduation` seeds the HyperSwap LP and flips `lifecycle` to `Graduated`. `DONATION_AMOUNT` of LT remains sitting in `pairAddr`.
5. From this point forward, no function anywhere in `Bonding.sol`, `Router.sol`, or `Pair.sol` can call `Pair.transferAsset` for this pair again (its only two gated callers — `sell()` and `graduate()` — are dead for a graduated curve pair), so `DONATION_AMOUNT` is permanently unrecoverable.

### Citations

**File:** packages/contracts/src/Pair.sol (L81-86)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }
```

**File:** packages/contracts/src/Router.sol (L184-202)
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
```

**File:** packages/contracts/src/Router.sol (L203-211)
```text
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

**File:** packages/contracts/AGENTS.md (L88-89)
```markdown
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
```
