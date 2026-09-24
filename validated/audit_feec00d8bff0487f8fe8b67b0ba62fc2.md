### Title
`FeeVault.claimProtocol()` / `sweepDonations()` are permissionless, letting a front-runner force payout to a compromised or stale `feeTo` before rotation - (File: `packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claimProtocol()` and `FeeVault.sweepDonations()` can be called by any address, and both unconditionally pay out to the currently-configured `feeTo`. If `feeTo` is ever compromised, or the team is in the process of rotating it away from a leaked/stale key, an attacker can force an immediate payout to the old/compromised address before the admin's `setFeeTo` transaction lands, permanently diverting protocol fees.

### Finding Description
`claimProtocol()` reads `$.protocolBalance`, zeroes it, and transfers the full amount to `$.feeTo` — with no access control: [1](#0-0) 

`sweepDonations()` similarly computes any USDC surplus above backed balances and pays it to `$.feeTo`, also with no access control: [2](#0-1) 

`setFeeTo()` is `onlyOwner`, but the contract's own doc comment acknowledges the race: rotating `feeTo` does not automatically flush the pending `protocolBalance` (or sweepable donations) to the *old* recipient — the admin must remember to call `claimProtocol()`/`sweepDonations()` *first*: [3](#0-2) 

Because `claimProtocol()`/`sweepDonations()` are permissionless, any address — not just the admin — can win this race in either direction:
- If `feeTo`'s key is compromised, the attacker (as the new controller of that address) doesn't even need special access: anyone can trigger `claimProtocol()`/`sweepDonations()` to push accumulated protocol fees straight to the compromised address at any time, repeatedly, for as long as the admin has not yet called `setFeeTo`.
- When the admin does submit `setFeeTo(newFeeTo)` to rotate away from a compromised/stale address, an attacker who is watching the mempool can front-run it with a higher-gas `claimProtocol()` (and/or `sweepDonations()`) call so the pending `protocolBalance`/surplus is paid to the old address before the rotation transaction executes, exactly as described in the original `AvailBridge.withdrawFees` report.

This directly mirrors the reported bug class: a permissionless payout function whose destination is an admin-set variable, with no pause/guard preventing a payout to a soon-to-be-revoked or already-compromised recipient.

### Impact Explanation
Protocol fees (`protocolBalance`) accumulated from every buy/sell across all bonding curves (0.5% of the 0.75% total fee) can be permanently diverted to a compromised `feeTo` address, and the same is true for any sweepable USDC surplus via `sweepDonations()`. This is a direct, permanent loss of protocol funds with no on-chain remediation once the transfer completes (`safeTransfer` is final; there is no pause or blacklist mechanism on `FeeVault`).

### Likelihood Explanation
`feeTo` key compromise is an external, low-cost precondition already contemplated by the contract's own comments (the doc explicitly warns admins to sweep before rotating), and the payout functions being permissionless means the exploit path requires no special privileges — any address can call `claimProtocol()`/`sweepDonations()` at any time, including watching the mempool for a `setFeeTo` rotation and front-running it with a higher gas price. This is entirely feasible for a single unprivileged trader/attacker to execute.

### Recommendation
Gate `claimProtocol()` and `sweepDonations()` behind `onlyOwner` (or a dedicated operational role), or alternatively have `setFeeTo()` atomically flush `protocolBalance`/donation surplus to the old `feeTo` before updating the recipient, removing the race window entirely.

### Proof of Concept
1. Admin sets `feeTo = A`; over time, buys/sells accrue `protocolBalance` via `Zap` → `FeeVault.accrue`.
2. Key for `A` leaks. Admin prepares a transaction `setFeeTo(B)` to rotate away from `A`.
3. Attacker (or holder of leaked key for `A`) observes the pending `setFeeTo(B)` tx in the mempool and submits `claimProtocol()` (and `sweepDonations()` if there's a surplus) with higher gas priority.
4. The permissionless `claimProtocol()`/`sweepDonations()` calls execute first, per [4](#0-3) , draining `protocolBalance` (and surplus) to the compromised address `A`.
5. `setFeeTo(B)` then executes, but the funds are already gone — the team has lost the entire pending protocol fee balance to the compromised recipient, matching the "Medium Example" scenario from the source report.

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
