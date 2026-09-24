#No vulnerability found for this question.

The `checkpoint.count`-based keeper-fee-dilution bug class does not map onto alt.fun's architecture. Perennial's `Vault` splits a shared keeper/settlement fee across all users who deposit/redeem within the same oracle epoch, tracked via `checkpoint.count`, which a free `update(user,0,0,0)` call can inflate to shrink an attacker's own fee share.

alt.fun has no equivalent shared-fee-pool-divided-by-participant-count mechanism anywhere in scope. Fees in `Zap` are computed and charged per-trade as an exact percentage (`sellFeeBps`/buy fee) of that trade's gross amount, then forwarded and recorded exactly via `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)` [1](#0-0) . There is no per-epoch batching, no "checkpoint" counter, and no fee-per-participant division that a free, funds-less call could dilute.

The permissionless entry points that exist — `FeeVault.claimProtocol()` and `FeeVault.sweepDonations()` — pay out the *entire* stored balance to the fixed admin-set `feeTo` regardless of who calls or how many times, with no count-based fee-shrinking effect [2](#0-1) . Similarly, `Bonding.triggerGraduation` is a state-transition trigger, not a fee-splitting mechanism, and repeated calls don't change any per-user fee calculation [3](#0-2) . Since no analog of the shared/diluted fee-accounting structure exists in the in-scope contracts, this report's bug class has no reachable counterpart here.

### Citations

**File:** packages/contracts/src/Zap.sol (L476-487)
```text
    function _accrueFee(
        address token,
        address creator,
        uint256 feeAmount,
        bool isBuy
    ) internal {
        ZapStorage storage $ = _s();
        uint256 creatorShare = (feeAmount * $.creatorFeeBps) / BPS_DENOM;
        uint256 protocolShare = feeAmount - creatorShare;
        $.usdc.safeTransfer(address($.feeVault), feeAmount);
        $.feeVault.accrue(token, creator, creatorShare, protocolShare, isBuy);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L137-160)
```text
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

**File:** docs/contracts-scope.md (L66-77)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)

**Exchange-rate freshness on the USD trigger.** The USD trigger reads the LT's `exchangeRate()`, a view that reports `totalAssets / totalSupply` *without* settling the LT's accrued streaming fee — that fee is only realised when a `mint` / `redeem` / agent checkpoint runs on the LT. The view therefore sits marginally above the post-checkpoint rate, by at most the pending fee (`≈ streamingFee × leverage × time-since-last-checkpoint`; sub-cent for the actively-traded LTs supported here). The effect is benign and one-directional: a token can enter `Graduating` a touch before its settled reserve value crosses the threshold. The threshold-crossing buy path is unaffected — every buy mints LT and `mint` checkpoints the LT in the same tx, so `canGraduate` reads a freshly-settled rate there; only th ... (truncated)

**Retired LTs.** The reserve asset is an external BounceTech LT. If BounceTech de-registers it (it redeploys a fresh LT at a new address and flips the old address's `ltExists` to `false`), bonding curves already pointing at the old LT keep trading — `mint` / `redeem` / `exchangeRate` still work — but its `exchangeRate` stops tracking the underlying, so leverage is effectively frozen. The USD trigger above then can't ripen further; the supply trigger still graduates the token, and holders can always exit via `redeem`, so no funds are stranded. `Bonding.launch` rejects new bonding curves against a retired LT (its `ltExists` gate), so only pre-existing bonding curves are affected. See root `AGENTS.md` for the full note.
```
