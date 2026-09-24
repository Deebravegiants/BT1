### Title
Creator fee balances in FeeVault become permanently frozen if the creator's address is blacklisted by USDC - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault` accrues each token creator's share of trading fees in `creatorBalance[creator]` and pays it out only via `claim()`, which transfers USDC directly to `msg.sender`. Because USDC (the fee asset used throughout the protocol) supports an issuer-side blacklist, a creator whose address is later blacklisted permanently loses the ability to withdraw their accrued fee balance, and there is no mechanism in `FeeVault` to redirect or rescue that specific balance to another address.

### Finding Description
Fees are pulled by `Zap` in USDC and forwarded to `FeeVault.accrue`, which credits `creatorBalance[creator]` keyed strictly by the creator address stored at launch time [1](#0-0) . The only way to withdraw this balance is:

```solidity
function claim() external nonReentrant returns (uint256 amount) {
    FeeVaultStorage storage $ = _s();
    amount = $.creatorBalance[msg.sender];
    if (amount == 0) revert NothingToClaim();
    $.creatorBalance[msg.sender] = 0;
    $.totalAccruedCreator -= amount;
    $.usdc.safeTransfer(msg.sender, amount);
    emit CreatorFeesClaimed(msg.sender, amount);
}
``` [2](#0-1) 

`claim()` unconditionally sends the USDC to `msg.sender` — there is no parameter to specify an alternate recipient, and no owner-only rescue/reassignment function for a specific creator's `creatorBalance` entry exists anywhere in the contract; the only admin levers are `addDepositor`, `removeDepositor`, and `setFeeTo` (all unrelated to creator balances) [3](#0-2) .

`Bonding.transferCreator` exists to reassign the *creator* role on a launched token going forward, but it only updates `tokenInfo[token].creator`, which controls attribution of *future* accruals in `Zap._accrueFee` / `FeeVault.accrue`. It does not — and cannot — move a *already-accrued* `creatorBalance[oldCreator]` entry in FeeVault to the new creator address, since that mapping is keyed by the old address and only `claim()` (gated to `msg.sender`) can zero it out. If `oldCreator` is a USDC-blacklisted address, `usdc.safeTransfer(oldCreator, amount)` inside `claim()` will revert every time it is attempted (real USDC's `transfer`/`transferFrom` revert for blacklisted addresses), so that specific balance can never be extracted — not by the creator, not by anyone else, and not even by rotating `transferCreator` for the token.

This is the direct on-chain analog of the referenced LooksRare/YoloV2 issue: a participant (here, the token creator) who ends up on the USDC blacklist cannot claim their pooled USDC rewards, and the protocol has no alternate-recipient or rescue path for that specific balance, leaving it stranded in the vault forever.

### Impact Explanation
`creatorBalance[creator]` for a blacklisted creator becomes permanently unclaimable USDC, meaning:
- Real trader/creator funds are frozen indefinitely with no recovery path (`claim()` will revert forever for that address).
- The stranded balance still counts inside `totalAccruedCreator`, so it permanently consumes headroom in the underfund check in `accrue()` [4](#0-3) , effectively locking that USDC out of the vault's normal accounting while producing no economic benefit to anyone (not sweepable via `sweepDonations()`, since that function only sweeps *unbacked* surplus, not backed accruals) [5](#0-4) .

This is a Medium-severity permanent freezing of creator funds, matching the "permanent freezing of trader/creator/LP funds" criterion.

### Likelihood Explanation
Any token creator is an ordinary, unprivileged address chosen at `launch()` time; USDC blacklisting of any given address (sanctions, exchange-driven blacklisting, compliance action, etc.) is entirely outside the protocol's control and can happen to any creator address at any time after fees have already accrued. No attacker action against the protocol is required — this is a standard external-token risk that the contract fails to defensively handle, exactly as flagged in the reference report for a winner's reward payout.

### Recommendation
Add a mechanism to redirect a specific creator's frozen `creatorBalance` to a new recipient, e.g.:
- A `claimTo(address recipient)` function usable by `msg.sender` to redirect their own claim to an arbitrary address (defends against `msg.sender` itself being blacklisted, since the creator can still initiate the call — only the transfer's `to` address is checked by USDC's blacklist).
- Alternatively, allow `Bonding.transferCreator` (or a dedicated `FeeVault` admin/owner function) to migrate an outstanding `creatorBalance[oldCreator]` to the new creator address as part of the creator-transfer flow, so control of stuck balances can be recovered.

### Proof of Concept
1. Creator `C` launches a token via `Bonding.launch` / `Zap.createToken`, and repeated buys/sells on the curve accrue USDC fees into `FeeVault.creatorBalance(C)` via `Zap._accrueFee` → `FeeVault.accrue` [6](#0-5) .
2. USDC's issuer blacklists address `C` (external to the protocol, not requiring any protocol interaction).
3. `C` calls `FeeVault.claim()`. The internal `$.usdc.safeTransfer(msg.sender, amount)` call reverts because USDC's `transfer` function reverts for a blacklisted recipient [2](#0-1) .
4. No other function in `FeeVault` or `Bonding` can move or reroute `creatorBalance(C)`; `transferCreator` only changes future attribution, leaving the already-accrued balance permanently locked under the blacklisted key.

### Citations

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

**File:** packages/contracts/src/FeeVault.sol (L151-160)
```text
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
