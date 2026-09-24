### Title
Creator fee balances permanently frozen in FeeVault when the claiming address is blacklisted by USDC, with no rescue path even after `transferCreator` - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` pays a creator's entire pooled USDC balance directly to `msg.sender` with a single unconditional `safeTransfer`. If a creator's address is ever blacklisted by USDC (e.g. compliance action, since real USDC enforces an issuer-side blacklist), every future `claim()` call for that address reverts permanently, and there is no alternate withdrawal path — mirroring the JUSDBank `liquidate()` bug class where a hard-coded USDC-only payout to a potentially blacklisted address bricks the flow with no fallback.

### Finding Description
`claim()` reads `creatorBalance[msg.sender]`, zeroes it, and transfers the USDC straight to `msg.sender`: [1](#0-0) 

This is the only exit for accrued creator fees. `Bonding.transferCreator` lets a creator redirect **future** fee attribution to a new address: [2](#0-1) 

but it only mutates `TokenInfo.creator` on `Bonding` — it never touches `FeeVault`'s `creatorBalance` mapping, which is keyed by the *old* creator address, not by token: [3](#0-2) 

So any USDC already pooled under the old address in `creatorBalance` stays keyed to that address forever. There is no admin/rescue function that can redirect or sweep an already-backed `creatorBalance` entry — `sweepDonations()` only sweeps the *unbacked* surplus above `totalAccruedCreator + protocolBalance`, explicitly leaving backed balances untouched: [4](#0-3) 

The admin-only levers (`addDepositor`, `removeDepositor`, `setFeeTo`) have no way to reach `creatorBalance[creator]` for a different address either: [5](#0-4) 

Exactly like the JUSDBank finding, the root cause is: a payout that must land on a specific, user-influenced/user-assigned address, paid in a single blacklist-capable asset (USDC), with no alternate claim path if that transfer permanently reverts.

### Impact Explanation
Once a creator's claiming address is blacklisted by the USDC issuer, their entire accrued `creatorBalance` (0.25% of every buy/sell on their token(s), which can accumulate to a large sum for a popular token) becomes permanently unclaimable. `transferCreator` cannot rescue it because it only redirects *future* accrual, not the existing pooled balance tied to the old address. This is a permanent freezing of creator funds inside `FeeVault`, satisfying the accepted impact class.

### Likelihood Explanation
No attacker action on-chain is required beyond normal usage — the creator address just needs to become subject to USDC's issuer-controlled blacklist at any point after fees have accrued (a realistic real-world event for any USDC holder, and the same precondition the original report relies on). Because `claim()` is the sole withdrawal path and is a single unconditional `safeTransfer` to `msg.sender`, the failure mode is deterministic and unrecoverable once triggered.

### Recommendation
Decouple the payout recipient from the accrual key: add a `claimTo(address recipient)` (with appropriate authorization, e.g. still gated on the caller being the address holding the balance, or allow the caller to nominate a destination) so a creator can redirect payout on a per-claim basis, or add an owner-gated migration function that can move a stuck `creatorBalance[oldCreator]` to a new address once verified off-chain, similar in spirit to `transferCreator` but covering already-accrued balances, not just future accrual.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L36-44)
```text
        mapping(address creator => uint256) creatorBalance;
        uint256 protocolBalance;
        /// @notice Lifetime gross creator USDC accrued (never decreases).
        mapping(address creator => uint256) lifetimeCreatorEarned;
        uint256 lifetimeProtocolEarned;
        /// @notice Running sum of unclaimed creator balances. Lets `accrue`
        ///         do its underfund check in O(1) without iterating the
        ///         creator mapping.
        uint256 totalAccruedCreator;
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

**File:** packages/contracts/src/FeeVault.sol (L162-193)
```text
    // ─── Admin ───────────────────────────────────────────────────────────

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
