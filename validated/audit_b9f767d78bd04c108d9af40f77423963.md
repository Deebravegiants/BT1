## Title
Token creator fee balances in `FeeVault` become permanently unclaimable if the creator's address is blacklisted by USDC - (File: `packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claim()` always pays out to `msg.sender` directly, and `Bonding.transferCreator()` only redirects *future* fee attribution — it never migrates a creator's already-accrued `creatorBalance` in `FeeVault`. If a creator's address is ever added to USDC's blacklist (for any of the many non-exploit-dependent reasons cited in the referenced report: sanctions, law-enforcement requests, or being the unwitting recipient of tainted funds), every `USDC.transfer` to that address reverts, and the creator's accrued fee balance is permanently stuck with no on-chain recovery path.

### Finding Description
Fees accrue to a creator address that is fully attacker/creator-controlled: `Zap._accrueFee` looks up the attribution via `bonding_.creatorOf(tokenAddress)` and calls `feeVault.accrue(token, creator, creatorShare, protocolShare, isBuy)` [1](#0-0) , which increments `creatorBalance[creator]` in `FeeVault` [2](#0-1) .

The only exit for that balance is `claim()`, which unconditionally sends USDC straight to `msg.sender`: [3](#0-2) 

`Bonding.transferCreator()` lets the current creator hand off the *role* to a new address, but it only updates `TokenInfo.creator` for future attribution — it does not touch, migrate, or in any way reference the existing `FeeVault.creatorBalance[oldCreator]` mapping entry: [4](#0-3) 

`FeeVault` has no admin rescue, redirect, or reassignment function for a specific creator's balance — the only owner-gated functions are `addDepositor`, `removeDepositor`, and `setFeeTo` [5](#0-4) . `claimProtocol()` and `sweepDonations()` only move the separate `protocolBalance` / surplus-donation pool to the admin-set `feeTo`, and cannot touch `creatorBalance` [6](#0-5) .

So once a creator address is blacklisted by USDC:
1. Every future `claim()` call from that address reverts (USDC blacklist reverts on transfer to a blacklisted recipient).
2. There is no way for the creator (or anyone) to redirect the already-accrued `creatorBalance[creator]` to a fresh address — `transferCreator` is prospective-only.
3. The USDC sitting in `FeeVault` backing that balance is permanently unreachable, exactly the "permanent freezing" pattern flagged in the referenced Sentiment V2 report, mapped here onto alt.fun's own fee-claim surface instead of a liquidation-transfer surface.

### Impact Explanation
This is a direct, permanent loss of the creator's own accrued protocol fees (potentially unbounded, growing with every buy/sell of that creator's token at 0.25% per trade) with zero recovery mechanism anywhere in the contract set. This matches the "permanent freezing of ... creator ... funds" impact class.

### Likelihood Explanation
Low-likelihood but non-zero and outside the creator's control, exactly like the original finding: USDC blacklisting is driven by Circle's compliance/AML process and can target any externally-derived address for reasons unrelated to on-chain exploitation (sanctions list matches, being the recipient of tainted transfers, law-enforcement requests, etc.), not only malicious behavior by the creator themselves. Because a creator's fee stream can run indefinitely and there is no redirect path, the funds-at-risk grow the longer the creator continues earning before (or after) being listed.

### Recommendation
Decouple the payout destination from the accrual key: add an owner- or creator-initiated mechanism to reassign/migrate an already-accrued `creatorBalance` to a new address (e.g., a `migrateCreatorBalance(oldCreator, newCreator)` gated by a signature from `oldCreator` or a timelocked admin path), or let `claim()` accept an explicit `to` parameter validated against a creator-signed permission, so a creator who anticipates or discovers blacklisting can redirect their own already-earned balance before/after the fact.

### Proof of Concept
1. Creator launches a token via `Bonding.launch`, trades occur through `Zap.buy`/`Zap.sell`, and `_accrueFee` steadily increases `FeeVault.creatorBalance[creator]` [1](#0-0) .
2. Creator's address gets added to USDC's blacklist (simulated in tests the same way the repo's own `forge-std` `StdCheats` test helpers mock USDC blacklisting) [7](#0-6) .
3. Creator calls `FeeVault.claim()`; the internal `$.usdc.safeTransfer(msg.sender, amount)` reverts because USDC refuses to transfer to a blacklisted address [3](#0-2) .
4. Creator calls `Bonding.transferCreator(tokenAddress, newAddress)` to redirect future fees — this succeeds and updates `TokenInfo.creator`, but `FeeVault.creatorBalance[oldCreator]` is untouched [4](#0-3) .
5. The new address calling `claim()` receives only newly accrued fees (attributed post-transfer); the pre-existing balance keyed to the blacklisted old address remains permanently stuck in `FeeVault` with no function anywhere in the contract able to move it out.

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

**File:** packages/contracts/src/FeeVault.sol (L101-123)
```text
    function accrue(
        address token,
        address creator,
        uint256 creatorAmount,
        uint256 protocolAmount,
        bool isBuy
    ) external onlyDepositor {
        FeeVaultStorage storage $ = _s();
        if (creatorAmount > 0) {
            if (creator == address(0)) revert ZeroAddress();
            $.creatorBalance[creator] += creatorAmount;
            $.totalAccruedCreator += creatorAmount;
            $.lifetimeCreatorEarned[creator] += creatorAmount;
        }
        if (protocolAmount > 0) {
            $.protocolBalance += protocolAmount;
            $.lifetimeProtocolEarned += protocolAmount;
        }
        if ($.usdc.balanceOf(address(this)) < $.totalAccruedCreator + $.protocolBalance) {
            revert UnderfundedAccrual();
        }
        emit FeeAccrued(token, creator, creatorAmount, protocolAmount, isBuy);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L127-135)
```text
    function claim() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.creatorBalance[msg.sender];
        if (amount == 0) revert NothingToClaim();
        $.creatorBalance[msg.sender] = 0;
        $.totalAccruedCreator -= amount;
        $.usdc.safeTransfer(msg.sender, amount);
        emit CreatorFeesClaimed(msg.sender, amount);
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

**File:** packages/contracts/src/FeeVault.sol (L164-193)
```text
    function addDepositor(
        address depositor
    ) external onlyOwner {
        if (depositor == address(0)) revert ZeroAddress();
        if (!_s().depositors.add(depositor)) revert DepositorAlreadyAdded();
        emit DepositorAdded(depositor);
    }

    function removeDepositor(
        address depositor
    ) external onlyOwner {
        if (!_s().depositors.remove(depositor)) revert DepositorNotFound();
        emit DepositorRemoved(depositor);
    }

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

**File:** packages/contracts/src/Bonding.sol (L738-748)
```text
    function transferCreator(
        address tokenAddress,
        address newCreator
    ) external {
        if (newCreator == address(0)) revert ZeroAddress();
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (msg.sender != info.creator) revert NotCreator();
        if (newCreator == info.creator) revert InvalidInput();
        info.creator = newCreator;
        emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
    }
```

**File:** packages/contracts/lib/forge-std/test/StdCheats.t.sol (L489-499)
```text
    function test_RevertIf_AssumeNoBlacklisted_USDC() external {
        // We deploy a mock version so we can properly test the revert.
        StdCheatsMock stdCheatsMock = new StdCheatsMock();
        vm.expectRevert();
        stdCheatsMock.exposedAssumeNotBlacklisted(address(USDC), USDC_BLACKLISTED_USER);
    }

    function testFuzz_AssumeNotBlacklisted_USDC(address addr) external view {
        assumeNotBlacklisted(address(USDC), addr);
        assertFalse(USDCLike(USDC).isBlacklisted(addr));
    }
```
