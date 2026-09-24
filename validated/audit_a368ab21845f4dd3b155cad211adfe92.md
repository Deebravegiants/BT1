## Finding: Direct LT donations to a bonding-curve `Pair` are permanently unrecoverable

The reported bug class — value sent to a strategy contract that has no mechanism to retrieve it — has a direct analog in `Pair.sol`.

### Root cause

`Pair.sol` exposes only two outbound-asset functions, both gated `onlyRouter`: [1](#0-0) 

Unlike a real UniswapV2 pair, `Pair.sol` has **no `skim()` / `sync()`** and no owner-rescue function — `transferAsset`/`transferToken` are its only exits, and both require `msg.sender == router`.

`Router.sol` only ever calls `Pair.transferAsset` from `Router.graduate`, gated by `BONDING_ROLE`: [2](#0-1) 

`Bonding` only calls `Router.graduate` from `_prepareGraduationLiquidity`, which is reachable exactly once per token, while `Lifecycle == Curve`, and it deliberately drains only `ltFromPair` (the curve-raised amount), excluding any donated LT by design: [3](#0-2) 

Once a token's lifecycle advances past `Curve` (i.e., it enters `Graduating`/`Graduated`), `_prepareGraduationLiquidity` can never run again for that token, so `Router.graduate` — the only function on the entire call graph capable of invoking `Pair.transferAsset` — becomes permanently unreachable for that pair.

### Why this is a real stuck-funds bug

Any unprivileged wallet can call `IERC20(lt).transfer(pairAddress, amount)` directly on the LT contract (or send a launched `Token`, though that side is at least burned during graduation). This is explicitly acknowledged in the docs as intentional/trusted behavior: [4](#0-3) 

But "trust assumption" here just means "we chose not to build a recovery path" — it is not an on-chain guarantee of eventual recovery. Contrast this with the two other places in the codebase where the exact same donation problem is explicitly solved with a sweep:
- `FeeVault.sweepDonations()` for stray USDC — [5](#0-4) 
- `Bonding._sweepLTToOwner` for LT residue picked up during HyperSwap LP-seeding rebalancing — [6](#0-5) 

`Pair.sol` received no equivalent treatment. Any LT donated to a curve `Pair` — whether donated before graduation (in which case `_prepareGraduationLiquidity` computes the exact curve-raised amount and leaves the donation behind by design) or after graduation (once the pair is drained and `Lifecycle` has moved past `Curve`) — is **permanently locked** in the `Pair` contract with zero recovery path for the depositor, the protocol owner, or any future keeper, since `onlyRouter` on `Pair` and the one-shot `BONDING_ROLE`-gated, lifecycle-gated `Router.graduate` are the only doors and both are closed.

### Impact

Permanent freezing of any LT accidentally or intentionally sent directly to a bonding-curve `Pair`. This is a Medium-severity fund-freezing issue: no privileged action, upgrade, or off-chain step is required — a plain unprivileged `IERC20.transfer` to a discoverable public address (`Bonding.tokenInfo(token).pair` or similar) is enough to trigger it, and the funds are unrecoverable for the lifetime of the contracts as currently written.

### Recommendation

Add a permissionless (or owner-gated) `skim`/`sweep` function to `Pair.sol` — analogous to `FeeVault.sweepDonations()` — that can transfer any LT/token balance in excess of the pool's tracked reserves to a designated recipient (e.g., the protocol owner or `FeeVault`), callable regardless of the pair's lifecycle state, so donated assets are never permanently stranded.

### Citations

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

**File:** docs/contracts-scope.md (L71-73)
```markdown
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)
```

**File:** docs/contracts-scope.md (L88-89)
```markdown
2. Burn any unsold real curve tokens from the pair (`unsoldBurned`). This also burns any tokens donated to the pair via direct ERC20 transfer.
3. Recover `virtualLtReserve = Pair.k() / Token.TOTAL_SUPPLY()` and compute `ltFromPair = reserve1 - virtualLtReserve` — the real LT raised by the curve, excluding the launch-time virtual seed AND any LT donated to the pair. Drain exactly that amount via `Router.graduate(token, ltFromPair)`. Donated LT remains in the curve pair, reachable only via `Pair.transferAsset` which is gated by `Router`'s `BONDING_ROLE`.
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

**File:** packages/contracts/src/Bonding.sol (L1036-1051)
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
```
