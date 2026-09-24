### Title
Permanent DoS of protocol fee collection if the admin-set `feeTo` address becomes an unbacked/blocked recipient of the reserve asset - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claimProtocol` and `FeeVault.sweepDonations` are permissionless functions that unconditionally push the pooled protocol balance (and any USDC donations) to a single stored `feeTo` address via `$.usdc.safeTransfer(feeTo_, amount)`. Just like the Elys Network bug where `CollectGasFees`/`CollectDEXRevenue` `panic`ed if the hard-coded protocol revenue address was blocklisted by the bank module, these functions have no fallback if the transfer to `feeTo_` reverts — every call to either function will unconditionally revert until an admin transaction fixes the recipient, leaving accrued protocol revenue permanently stuck and the anyone-can-call sweep function permanently broken in the interim.

### Finding Description
`claimProtocol()` and `sweepDonations()` both read the single admin-configured recipient `$.feeTo` and perform an unconditional `safeTransfer` to it: [1](#0-0) 

Both functions zero out or recompute the accrued/backed balance state (`$.protocolBalance = 0` in `claimProtocol`) *before* or independent of any external revert-safety consideration, and neither wraps the `safeTransfer` in a `try/catch` nor offers an alternate recipient path. If `feeTo_` becomes a recipient the reserve asset (USDC, a real-world centralized stablecoin with an on-chain denylist/blacklist capability controlled by its issuer) refuses to receive — whether via a Circle-side blacklist action, a sanctions freeze, or any other externally imposed block on that specific address — every subsequent call to `claimProtocol()` and `sweepDonations()` reverts unconditionally. This mirrors exactly the root cause in the referenced Elys Network report: a hard funds-transfer call to a single configured "revenue" address, with no error handling for the case where that address becomes unable to receive funds.

The only recovery path is the owner calling `setFeeTo()`: [2](#0-1) 

which is a privileged action — until that intervention happens, the accrued `protocolBalance` (and any sweepable donation surplus) is completely frozen and unclaimable by anyone, and the permissionless `sweepDonations()` function — whose entire design intent is that "anyone can trigger the payout" (per `docs/contracts-scope.md`) — is bricked.

### Impact Explanation
`claimProtocol()` and `sweepDonations()` are explicitly documented as permissionless, callable by anyone, with funds always routed to the admin-set `feeTo`: [3](#0-2) 

If `feeTo` ever becomes a blocked recipient of USDC, the entire protocol-revenue collection path freezes: `protocolBalance` accumulates indefinitely (every buy/sell continues accruing 0.5% protocol fee into the vault via `Zap._accrueFee` → `FeeVault.accrue`) but can never be paid out, and any USDC donated directly to the vault (`sweepDonations`) is similarly stuck. This is a freezing-of-protocol-funds condition with no automatic recovery — it requires an out-of-band admin `setFeeTo` transaction to unblock, during which window the protocol's own revenue is fully inaccessible.

### Likelihood Explanation
The reserve/fee asset here is USDC, whose issuer (Circle) has a live, exercised blacklist mechanism that can target arbitrary addresses (e.g., due to sanctions/compliance actions, or if `feeTo` is later reassigned to a multisig/contract address that gets flagged for unrelated reasons). This is not a hypothetical: USDC blacklisting of specific addresses has occurred in production before. Because `feeTo` is a long-lived, publicly known, frequently-interacted-with address (every `claimProtocol` call references it on-chain), it is a natural target, and the failure mode requires no attacker action at all beyond the external blacklist event — matching the "blocked recipient breaks fund transfer" bug class from the referenced report closely enough to be a credible risk in production.

### Recommendation
- Do not unconditionally revert the whole function on transfer failure. Wrap the `safeTransfer` to `feeTo_` in a `try/catch` (or a low-level call with return-value handling) and, on failure, keep the funds accounted for `feeTo_` reachable and log/emit an event rather than reverting the whole call.
- Alternatively, decouple accounting from payout: keep `protocolBalance` un-zeroed until the transfer actually succeeds, and provide a permissionless retry mechanism, or allow the owner to redirect and permissionless callers to retry once `feeTo` has been rotated to a non-blocked address — this at least matches the current design's manual-fix path.
- Consider allowing `claimProtocol`/`sweepDonations` to accept a caller-specified destination the owner has pre-approved, or a pull-based claim by `feeTo` itself instead of a push, so a single blocked address cannot brick the sweep/claim entirely for all past-and-future accrual.

### Proof of Concept
1. Owner deploys `FeeVault` with `feeTo = A` (a normal EOA/contract).
2. Protocol operates normally; `Zap._accrueFee` repeatedly calls `FeeVault.accrue`, growing `$.protocolBalance`.
3. USDC's issuer blacklists address `A` (independently of the protocol, via Circle's denylist mechanism baked into the real USDC contract).
4. Any address calls `FeeVault.claimProtocol()`. `$.usdc.safeTransfer(feeTo_, amount)` at [4](#0-3)  reverts because USDC refuses to credit a blacklisted recipient; the whole `claimProtocol` transaction reverts.
5. Any address calls `FeeVault.sweepDonations()`; the analogous `safeTransfer` at [5](#0-4)  reverts identically.
6. Both permissionless entry points remain permanently broken — and all newly accrued protocol fees pile up unclaimable — until the owner submits a `setFeeTo` transaction pointing to a non-blacklisted address.

### Citations

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

**File:** packages/contracts/src/FeeVault.sol (L179-193)
```text
    /// @notice Set the protocol fee recipient.
    /// @dev Protocol fees are pooled and paid to whoever is `feeTo` at claim
    ///      time, so rotating here redirects the entire outstanding
    ///      `protocolBalance` — and any sweepable donations — to `feeTo_`. Call
    ///      `claimProtocol()` (and `sweepDonations()`) first to settle the
    ///      pending balance to the current recipient before rotating.
    function setFeeTo(
        address feeTo_
    ) external onlyOwner {
        if (feeTo_ == address(0)) revert ZeroAddress();
        FeeVaultStorage storage $ = _s();
        address old = $.feeTo;
        $.feeTo = feeTo_;
        emit FeeToUpdated(old, feeTo_);
    }
```

**File:** docs/contracts-scope.md (L118-118)
```markdown
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
```
