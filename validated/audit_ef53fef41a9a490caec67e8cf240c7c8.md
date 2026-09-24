## Analysis

The report's bug class — funds that enter a contract's accounting window but are permanently excluded from every future distribution/settlement path with no rollover or rescue mechanism — has a direct analog in alt.fun's bonding-curve `Pair`/`Router`/`Bonding` graduation flow.

### Title
Direct LT donations to a bonding-curve `Pair` become permanently and irrecoverably locked once the token graduates - (File: `packages/contracts/src/Bonding.sol`, `packages/contracts/src/Router.sol`, `packages/contracts/src/Pair.sol`)

### Summary
Any unprivileged wallet can `IERC20.transfer` BounceTech LT directly to a `Pair` contract while its token is still on the `Lifecycle.Curve`. That LT is deliberately excluded from graduation ("donation resistance") and is only ever movable out of the `Pair` via `Pair.transferAsset`, which is `onlyRouter`-gated and in turn requires `BONDING_ROLE` on `Router`, held solely by `Bonding`. `Bonding` only ever calls `Router.graduate` once per token, from inside `_prepareGraduationLiquidity`, which fires exactly once during the `Curve → Graduating` transition and explicitly passes `ltFromPair` (excluding any donated amount) rather than the pair's full asset balance. Once the token's lifecycle advances past `Curve`, there is no other code path anywhere in the protocol that invokes `Router.graduate` or otherwise calls `Pair.transferAsset` for that pair. The donated LT is therefore permanently stranded in the `Pair` contract with no admin rescue, no future rollover into the LP, and no way for the donor (or anyone) to ever retrieve it.

### Finding Description
`Router.graduate` is documented as intentionally donation-resistant: [1](#0-0) 

Its own natspec states the "locked" claim is a trust assumption, contingent on `BONDING_ROLE` never being granted elsewhere and `Bonding` never calling `graduate` again post-lifecycle-flip. The call site backs this up: `_prepareGraduationLiquidity` computes `ltFromPair = assetReserve - virtualLtReserve` from the pair's *stored* reserves (which donations never touch) and drains only that amount: [2](#0-1) 

This function is only invoked once, from `_enterGraduating`, itself only reachable while `info.lifecycle == Lifecycle.Curve` (via `_executeBuy`'s inline check or the permissionless `triggerGraduation`, which explicitly reverts once `Lifecycle.Graduating`/`Graduated`): [3](#0-2) [4](#0-3) 

`Pair.transferAsset` itself has no other caller — it is a bare `onlyRouter` passthrough with no accounting of "excess" balance versus stored reserves, and `Pair.sol` exposes no skim/rescue function for its asset side (unlike the `PairSkim` behavior used defensively for *donated Token* on the token side during hostile-pre-seed handling): [5](#0-4) 

The project's own docs and test suite confirm the donated LT stays locked in the pair after a legitimate graduation, framing it as accepted behavior rather than treating it as a recoverable balance: [6](#0-5) [7](#0-6) 

There is no `notifyRewardAmount`-style mechanism, no admin sweep, and no later graduation event for that same `Pair` (a `Pair` is bound 1:1 to one `Token`/`Bonding` lifecycle and is never re-minted) that could ever "roll over" that stranded LT into the LP or return it to anyone — it is permanently orphaned ERC20 balance sitting at the `Pair` address, exactly analogous to the referenced report's un-rolled-over reward accrual that sits unusable in `StakingRewards` with no path to reclaim it in a future `notifyRewardAmount`.

### Impact Explanation
Any LT sent directly to a curve `Pair` — whether by user error, a well-meaning "tip", a bot misfire, or an integrator bug — becomes permanently frozen the moment (or before) the token graduates. This is a permanent freezing-of-funds condition matching the Validate criteria: real, external-value LT is locked with no recovery path for the sender, for `Bonding`, or for the protocol owner. Because `Bonding.owner()` has no function to call `Router.graduate` again or to otherwise pull from a post-graduation `Pair`, even the admin cannot make the depositor whole. The size of loss scales with however much LT is mistakenly or intentionally donated to any of the potentially many per-token pairs across the protocol's lifetime — unbounded per-donation, and cumulative across every launched token.

### Likelihood Explanation
Reaching this state requires only a single unprivileged ERC20 `transfer` call by any wallet to a known, permissionlessly-discoverable `Pair` address (available from `Bonding.tokenInfo(token).pair` or the `PairCreated` event) at any point before or during that token's `Curve` lifecycle, followed by the token's normal, permissionless graduation (`triggerGraduation`/buy-triggered `_enterGraduating` + anyone-callable `finalizeGraduation`). No special timing, front-running, or privileged role is needed — the donation-resistance design that intentionally excludes the LT from the USD trigger and from `ltFromPair` is precisely what guarantees the funds are excluded from the one-and-only sweep path. This is a near-certainty outcome any time a user donates by mistake (e.g., pastes the pair address instead of `Zap`, or a bot/integration sends LT to the pair thinking it funds the curve).

### Recommendation
Add an owner-gated (or otherwise access-controlled) rescue path — e.g. a `Bonding`/`Router` function usable only when a token's lifecycle is `Graduated` (or, better, at any lifecycle, capped at `assetBalance() - ltFromPair`-style accounting) that allows sweeping any LT balance in the `Pair` beyond what is tracked by stored reserves/`ltFromPair`, to `feeTo` or the owner, mirroring the existing `_sweepLTToOwner`/`LTRescued` pattern already used for post-graduation LT residue in `Bonding`. Alternatively, extend `_prepareGraduationLiquidity` to also drain any pair asset-balance surplus over `assetReserve` (the donation) into the same sweep destination used for `protectedLT`, rather than leaving it inside the `Pair` with no further owner of the call path.

### Proof of Concept
1. `Zap.createToken` launches a token; `Bonding` creates its `Pair` at address `P` with `Lifecycle.Curve`.
2. Any wallet (no role required) calls `IERC20(lt).transfer(P, X)`, donating `X` LT directly to the pair. `Pair.assetBalance()` increases by `X`; `Pair.getReserves()` (the stored `assetReserve`) is unchanged.
3. The token graduates normally — either via a threshold-crossing buy (`_executeBuy` → `_enterGraduating`) or via the permissionless `triggerGraduation`. `_prepareGraduationLiquidity` computes `ltFromPair` from stored reserves only, and `Router.graduate(token, ltFromPair)` drains exactly that amount, leaving `X` behind in `P` (verified by `test_inv_donation_zeroGapPreserved`'s `assertEq(IPair(pairAddr).assetBalance(), donation, ...)`, `packages/contracts/test/GraduationInvariants.t.sol:533`).
4. `finalizeGraduation` is called (anyone), completing the `Graduating → Graduated` transition and deleting `pendingGraduation[token]`.
5. From this point on, no function in `Bonding`, `Router`, or `Pair` can ever move `P`'s LT balance again: `Router.graduate` is unreachable (no code path calls it for a `Graduated` token), and `Pair.transferAsset` has no other caller. The donated `X` LT is permanently stuck in `P`, unrecoverable by the donor, `Bonding`'s owner, or the protocol.

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

**File:** packages/contracts/src/Bonding.sol (L938-953)
```text
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
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

**File:** packages/contracts/src/Pair.sol (L81-86)
```text
    function transferAsset(
        address recipient,
        uint256 amount
    ) external onlyRouter {
        IERC20(assetToken).safeTransfer(recipient, amount);
    }
```

**File:** docs/contracts-scope.md (L88-92)
```markdown
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
4. Compute `tokensForLP = (ltFromPair × reserve0) / reserve1` — the unique amount that sets the LP price `ltFromPair / tokensForLP` equal to the last curve price `reserve1 / reserve0`. Capped at `lpReserveTotal` as a defensive guard (parabola math proves `tokensForLP ≤ lpReserveTotal` by construction).
5. Burn `lpReserveTotal − tokensForLP` from `Bonding`'s held reserve (`lpBurned`).
6. `addLiquidity(tokensForLP, ltFromPair)` on HyperSwap V2 → LP tokens go to `LPLock`.
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
