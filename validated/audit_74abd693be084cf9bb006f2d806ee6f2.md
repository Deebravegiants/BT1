### Title
Directly-donated LT sitting in a graduated (or never-graduating) curve `Pair` is permanently unrecoverable - ([File: packages/contracts/src/Pair.sol])

### Summary
`Pair.transferAsset` is the only way to move the reserve asset (LT) out of a bonding-curve pair, and it is gated `onlyRouter`. `Router.sell` and `Router.graduate` are the only two callers, and both require `BONDING_ROLE`, which only `Bonding` holds [1](#0-0) [2](#0-1) . Once a token's lifecycle leaves `Curve` (either it graduates, or it is stuck in `Graduating` awaiting `finalizeGraduation`), `Bonding` never calls `Router.sell` or `Router.graduate` for that pair again. Any LT sent directly to the `Pair` contract via a plain ERC20 `transfer` — a donation, a mis-sent transaction, or dust left behind by the graduation math — is therefore permanently stranded with no on-chain path to withdraw it, structurally analogous to the Sherlock report's reward tokens that become unretrievable once `rewardsDistribution` ends and no leftover-sweep function exists.

### Finding Description
`Pair.transferAsset(recipient, amount)` is the sole function capable of moving `assetToken` (the LT) balance out of the pair [1](#0-0) . It is restricted with `onlyRouter`, and the `Router` contract exposes it through exactly two paths: `sell()`, used during normal curve trading, and `graduate()`, used exactly once by `Bonding._prepareGraduationLiquidity` to drain the curve's real LT raise at graduation time [3](#0-2) . Both require `BONDING_ROLE`, held only by `Bonding`.

Two windows close off any recovery of donated LT:
1. **Before/at graduation:** `Router.graduate` is called with an *explicit amount* — `ltFromPair = storedAssetReserve - virtualLtReserve` — deliberately excluding any LT donated to the pair beyond the curve's tracked reserves, by design ("donation-resistant" per the code comment) [4](#0-3) . The docs explicitly acknowledge the donated LT "remains in the curve pair" and is "reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`" [5](#0-4) .
2. **After graduation:** `Bonding` flips the token's `lifecycle` to `Graduated` and never issues another `Router.sell` or `Router.graduate` call against that pair — trading on that token moves to the HyperSwap pool via `Zap`, and `Bonding.sell`/`buy` revert once the lifecycle is not `Curve` (documented via `TokenNotTrading` reverts once graduated, matching the repository's own regression tests) [6](#0-5) .

Because `BONDING_ROLE` is never exercised against that pair again, any LT balance sitting in `Pair` beyond what graduation math accounted for — whether donated pre-graduation, donated post-graduation, or a token that never reaches the graduation threshold and is simply abandoned — has no code path back out. This mirrors the report's root cause exactly: a resource (rewards there, LT here) accrues in a contract whose only extraction function is deliberately scoped to a fixed, non-donation amount, and once the relevant lifecycle window closes, there is no sweep/rescue function to recover the residue.

### Impact Explanation
Any LT transferred directly into a `Pair` contract (a fully permissionless, unprivileged action reachable by any wallet holding LT) becomes permanently locked. This is a genuine, avoidable freezing of trader/donor funds — not a griefing-only or no-impact issue, since real economic value (LT, itself pegged to an underlying leveraged asset) is destroyed from a wallet's perspective with no recovery mechanism, matching the "permanent freezing of trader ... funds" acceptance criterion. Unlike `FeeVault`, which was explicitly hardened against exactly this class of donation-residue bug with a dedicated `sweepDonations()` permissionless sweep [7](#0-6) , `Pair` has no equivalent function — `assetBalance()` is exposed as a view but nothing can drain a discretionary surplus above the tracked reserve/graduation amount.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: LT donations to the curve pair are explicitly anticipated and discussed in the protocol's own documentation and invariant tests ("Donation resistance" invariant #7) [8](#0-7) , meaning the team already knows users/bots will send LT directly to `Pair` addresses (accidentally or as a griefing/dust vector), yet the recovery half of that scenario (getting the LT back out) was never built, unlike the symmetric `FeeVault` case.

### Recommendation
Add an owner- or permissionless-gated sweep function on `Pair` (or routed through `Router`/`Bonding` with `BONDING_ROLE`) analogous to `FeeVault.sweepDonations()`: compute `surplus = assetBalance() - trackedAssetReserve` (or, post-graduation, the full residual `assetBalance()`), and transfer it to a designated recipient (e.g., protocol owner or, ideally, back to the original token's creator/FeeVault) once the pair's lifecycle can no longer trade. This closes the same class of bug the external report flagged in `VirtualStakingRewards.notifyRewardAmount`.

### Proof of Concept
1. Launch a token via `Bonding.launch`, creating `Pair` P with `assetToken = LT`.
2. Anyone (an unprivileged wallet) calls `LT.transfer(address(P), X)` directly — a plain ERC20 transfer, one of the explicitly in-scope reachable actions.
3. Continue trading normally; when the token graduates, `Bonding._prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` from the pair's internally tracked `_pool.assetReserve`, which is unaffected by the raw ERC20 transfer (`Pair.swap`/`mint` are the only writers to `_pool`) — so `X` is excluded from the drained amount in `Router.graduate` [9](#0-8) .
4. `Bonding.finalizeGraduation` completes, flips `lifecycle` to `Graduated`. `LPLock.recordLock` finalizes the LP; `Router.sell`/`buy` for this token are no longer invoked against `P` (they revert with `TokenNotTrading` on the pre-graduation path, and post-graduation trading routes through `Zap`/HyperSwap instead) [6](#0-5) .
5. `X` LT remains in `P` forever — `Pair.transferAsset` can never be invoked again for that pair by any account, since `BONDING_ROLE` is never re-exercised against it, and no permissionless sweep exists.

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

**File:** packages/contracts/src/Router.sol (L172-182)
```text
    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
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

**File:** docs/contracts-scope.md (L89-89)
```markdown
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
```

**File:** docs/contracts-scope.md (L103-106)
```markdown
| 4 | Pair drained | `tokenBalance() == 0` post-graduation. `assetBalance() == 0` only when no donations occurred — any LT donated directly to the pair is excluded from LP seeding and remains locked in the pair. |
| 5 | Both triggers work | Supply trigger fires below `$9K`; USD trigger fires with supply remaining |
| 6 | Overflow refund | Oversized buys charge only `amountInUsed`, not requested amount |
| 7 | Donation resistance | Direct LT donations to the pair don't trigger graduation and don't skew LP open price; donated LT stays locked in the curve pair |
```

**File:** packages/contracts/test/Bonding.t.sol (L901-912)
```text
        (address tokenAddr,) = _launchToken();
        uint256 tokensOut = _buyTokens(tokenAddr, trader, _ltStageBeforeGraduation());
        lt.setExchangeRate(_ratePumpForStagedGraduation());
        _buyTokens(tokenAddr, trader2, _ltGraduationTrigger());
        assertTrue(bonding.isGraduated(tokenAddr));

        vm.startPrank(trader);
        Token(tokenAddr).approve(address(curveRouter), tokensOut);
        vm.expectRevert(Bonding.TokenNotTrading.selector);
        bonding.sell(tokensOut, tokenAddr, 0, trader);
        vm.stopPrank();
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
