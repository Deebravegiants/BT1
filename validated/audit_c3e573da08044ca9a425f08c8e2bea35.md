### Title
Direct LT donations to the curve `Pair` become permanently unrecoverable once the token graduates - ([File: packages/contracts/src/Router.sol])

### Summary
Any unrelated wallet can `transfer` (donate) the reserve LT directly to a token's curve `Pair` contract. That donated LT is intentionally excluded from the graduation drain and LP seeding (by design, to be donation-resistant on price), but once the token's lifecycle flips past `Curve`, there is no remaining code path capable of moving that LT out of the `Pair`. The funds are permanently frozen in the `Pair` contract, mirroring the reported bug class of "increased/excess balance locked in the pool with no recovery function."

### Finding Description
`Bonding._prepareGraduationLiquidity` computes the real LT raised by the curve using the pair's **stored** reserve minus the launch-time virtual seed, not the live LT balance: [1](#0-0) 

It then drains exactly `ltFromPair` via `Router.graduate`, which is the only production entry point that can move asset tokens out of the `Pair` outside of a `sell`: [2](#0-1) 

`Router.graduate` and `Pair.transferAsset` are both gated by `BONDING_ROLE`/`onlyRouter`, and `Bonding` only calls `graduate` from `_prepareGraduationLiquidity`, which is unreachable once `info.lifecycle` has advanced past `Curve` (checked in `canGraduate`/the graduation flow): [3](#0-2) 

The Router source itself documents this as an accepted trust assumption rather than an enforced on-chain guarantee: "Locked" here is a trust-assumption claim, not an on-chain guarantee... So the leftover is unreachable as long as (a) `BONDING_ROLE` is not granted to any other address, and (b) future `Bonding` upgrades preserve the lifecycle gate" (see the `graduate` natspec above, lines 192-202). This is precisely the pattern in the external report: a value that accrues on/inside the pool beyond the amount the withdrawal/drain logic accounts for (`poolAmount`/`ltFromPair`) becomes permanently stuck because the only withdrawal function is capped at the tracked amount and the surplus has no rescue path.

The invariant tests explicitly confirm the trapped state post-graduation: `assetBalance() == 0` only holds "when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair" (docs/contracts-scope.md invariant #4, corroborated by `GraduationInvariants.t.sol`).

### Impact Explanation
Any wallet — attacker, well-meaning donor, or someone fat-fingering a direct ERC20 transfer to the `Pair` address instead of through `Zap`/`Bonding.buy` — permanently loses those LT funds once the associated token graduates. This is a genuine, unbounded, unrecoverable freezing of funds inside a production contract (`Pair`), satisfying the "permanent freezing of trader, creator or LP funds" acceptance criterion. Because `Pair` is per-token and has no owner-sweep/rescue function analogous to `Bonding._sweepLTToOwner` (which only sweeps LT held by `Bonding` itself, not by `Pair`), there is no admin remediation path either.

### Likelihood Explanation
Reaching this state requires only a standard ERC20 `transfer` call to a publicly known, permissionless address (`Pair`) — no privileged role, no unusual timing needed beyond the token eventually graduating (which is expected to happen for any successful token). Accidental donations (e.g., a user or bot sending LT to the wrong address, or a well-intentioned "reward for the curve" style donation) are plausible; this is the same failure mode Sherlock's referenced report calls out for rebase-like assets whose balance in a pool can silently exceed the tracked accounting variable.

### Recommendation
Add a permissionless recovery function analogous to `FeeVault.sweepDonations()` for the curve `Pair`/`Bonding` — e.g., a `Bonding.sweepPairDonation(token)` that computes `IPair(pair).assetBalance() - trackedAssetReserve` (or, post-graduation, the full residual `assetBalance()`), calls a new `Router`/`Pair` function gated the same way as `graduate` but reachable regardless of lifecycle, and forwards the surplus to a safe destination (e.g., burn, or `owner()`/`feeTo`, mirroring `FeeVault`'s donation-sweep pattern). This preserves the existing donation-resistance property for graduation pricing while eliminating the permanent-freeze outcome.

### Proof of Concept
1. `Zap.createToken(...)` launches a token; `Bonding` creates a curve `Pair` paired with LT `lt`.
2. Attacker/donor calls `IERC20(lt).transfer(pairAddress, X)` directly (bypassing `Zap`/`Bonding`). This increases `Pair`'s live LT balance (`assetBalance()`) by `X` but does **not** change the pair's stored `assetReserve` used by `canGraduate`/`_prepareGraduationLiquidity`.
3. Normal buys continue until the token graduates via either trigger in `Bonding.canGraduate`.
4. `_enterGraduating` → `finalizeGraduation` → `_prepareGraduationLiquidity` computes `ltFromPair = assetReserve - virtualLtReserve` (stored reserve only) and drains exactly that via `Router.graduate`; the donated `X` LT is left behind in `Pair`.
5. `info.lifecycle` flips to `Graduated`. Any subsequent call into `Router.graduate` for this token is unreachable (`_prepareGraduationLiquidity` is only invoked once, from the Curve-lifecycle graduation path), and `Router.sell`/`Pair.transferAsset` require a live curve token balance/`BONDING_ROLE` flow that no longer applies to a graduated token.
6. The donated `X` LT remains stuck in `Pair` forever — confirmed by `GraduationInvariants.t.sol`'s documented invariant that `assetBalance() == 0` post-graduation holds only in the no-donation case.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
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
