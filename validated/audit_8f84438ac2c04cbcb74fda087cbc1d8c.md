### Title
Direct LP-token donation to `LPLock` is permanently stranded — no rescue mechanism exists - ([File: packages/contracts/src/LPLock.sol])

### Summary
`LPLock` has no withdrawal, sweep, or rescue function for LP tokens (or any ERC20) that end up in the contract outside of a `recordLock` call. Any LP token or other ERC20 sent directly to `LPLock` via a plain `transfer` — whether by a mistaken user, a malicious pre-seed griefer, or any third party — is permanently and unconditionally locked with no code path to recover it, mirroring the reported "lack of recovery mechanism for stuck assets" bug class (originally about stuck Ether, here about stuck LP/ERC20 tokens).

### Finding Description
`LPLock.recordLock` only records a `LockInfo` for the caller-supplied `(token, lpPair, amount)` when the caller is an allow-listed `isLocker` (i.e. `Bonding`), and only checks that the contract's balance of `lpPair` is `>= amount`: [1](#0-0) 

There is no function anywhere in the contract to transfer any ERC20 balance back out — `recordLock` never moves tokens out, `addLocker` only manages the allowlist, and the only other externally callable state-mutating function is `_authorizeUpgrade` (owner-gated UUPS upgrade): [2](#0-1) 

This is explicitly acknowledged in the codebase's own comments as a permanent-loss condition. `Bonding.sol`'s hostile-pre-seed handling notes that any LP tokens that end up routed to `LPLock` outside the single intended `recordLock` call are permanently stuck because "LPLock has no rescue path in v1": [3](#0-2) 

Since `LockInfo.lockedAt` is a one-shot sentinel (`if ($.locks[token].lockedAt != 0) revert AlreadyLocked();`), any given token can only be locked once, so extra LP balance sent to `LPLock` for a token that has already been locked (e.g. a well-meaning user re-sending LP, or an attacker donating LP tokens for a not-yet-graduated token, or literally any unrelated ERC20 sent by mistake) can never be attributed to a lock, never withdrawn, and never swept — unlike `FeeVault`, which has a dedicated `sweepDonations()` function precisely to handle stray/donated balances: [4](#0-3) 

An unprivileged trader or unrelated wallet can trivially reach this: any address can call `IERC20(lpToken).transfer(address(lpLock), amount)` on the graduated pair's LP token (or on any other ERC20) at any time — no privileged role, no upgrade, and no off-chain action is required.

### Impact Explanation
Any LP tokens or ERC20 balance sent directly to `LPLock` outside the intended `Bonding.finalizeGraduation → recordLock` flow is permanently frozen with no owner-level or permissionless recovery path — a straightforward and irreversible loss of funds for whoever sends them. Given `LPLock` is UUPS-upgradeable, a fix requires a full contract upgrade rather than a normal maintenance call, meaning stuck value could sit frozen for an extended period even after being identified. This satisfies "permanent freezing of trader, creator or LP funds" under the validation criteria.

### Likelihood Explanation
Medium likelihood. This requires either user error (sending LP tokens to the wrong/lock address, easy to do since `LPLock` holds real, valuable HyperSwap V2 LP tokens post-graduation) or deliberate low-cost griefing (donating dust LP or unrelated ERC20 to grief the contract's balance/analytics). No special privileges, timing, or contract interactions are required — a single `transfer` call from any EOA suffices.

### Recommendation
Add an owner-gated (or otherwise appropriately restricted) rescue function to `LPLock` that can sweep any ERC20 balance not already accounted for by an existing `LockInfo.amount`, analogous to `FeeVault.sweepDonations()`. For example, track cumulative locked amount per LP token and allow the owner to withdraw `balanceOf(lpToken) - lockedAmount[lpToken]`, ensuring genuinely locked LP tokens can never be swept while stray/donated tokens can be recovered.

### Proof of Concept
1. `Bonding.finalizeGraduation` graduates `TokenA`, calling `LPLock.recordLock(TokenA, pairA, amountA)` — this is the only intended interaction.
2. Any unrelated address (attacker or well-meaning user) calls `IERC20(pairA).transfer(address(lpLock), extraAmount)`, directly increasing `LPLock`'s LP balance beyond the recorded `amountA`.
3. Because `locks[TokenA].lockedAt != 0`, `recordLock` can never be called again for `TokenA` — `AlreadyLocked()` always reverts.
4. `LPLock` exposes no `withdraw`/`sweep`/`rescue` function reachable by anyone (owner or otherwise) for the excess LP balance.
5. `extraAmount` of LP tokens is permanently and irrecoverably stuck in `LPLock`, confirmed by the codebase's own natspec: "anything that lands there is permanently stuck." [5](#0-4)

### Citations

**File:** packages/contracts/src/LPLock.sol (L69-85)
```text
    /// @notice Record an LP lock. LP tokens must already sit at this address.
    function recordLock(
        address token,
        address lpPair,
        uint256 amount
    ) external {
        LPLockStorage storage $ = _s();
        if (!$.isLocker[msg.sender]) revert NotAuthorized();
        if (lpPair == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        // `lockedAt` is the one-shot sentinel: it is always set to a non-zero
        // timestamp on the first lock, so the guard holds for any `amount`.
        if ($.locks[token].lockedAt != 0) revert AlreadyLocked();
        if (IERC20(lpPair).balanceOf(address(this)) < amount) revert InsufficientLPBalance();
        $.locks[token] = LockInfo({lpPair: lpPair, amount: amount, lockedAt: block.timestamp});
        emit LPLocked(token, lpPair, amount);
    }
```

**File:** packages/contracts/src/LPLock.sol (L87-125)
```text
    /// @notice Authorise a new `recordLock` caller. Add-only by design — see
    ///         the natspec on `LPLockStorage.isLocker` for why there's no
    ///         `removeLocker`.
    function addLocker(
        address locker
    ) external onlyOwner {
        if (locker == address(0)) revert ZeroAddress();
        LPLockStorage storage $ = _s();
        if ($.isLocker[locker]) revert LockerAlreadyAdded();
        $.isLocker[locker] = true;
        emit LockerAdded(locker);
    }

    /// @notice Mirrors the auto-generated getter for the pre-ERC-7201 public
    ///         `locks` mapping so the external ABI is unchanged.
    function locks(
        address token
    ) external view returns (address lpPair, uint256 amount, uint256 lockedAt) {
        LockInfo storage info = _s().locks[token];
        return (info.lpPair, info.amount, info.lockedAt);
    }

    function isLocker(
        address account
    ) external view returns (bool) {
        return _s().isLocker[account];
    }

    function getLock(
        address token
    ) external view returns (address lpPair, uint256 amount, uint256 lockedAt) {
        LockInfo storage info = _s().locks[token];
        return (info.lpPair, info.amount, info.lockedAt);
    }

    function _authorizeUpgrade(
        address
    ) internal override onlyOwner {}
}
```

**File:** packages/contracts/src/Bonding.sol (L1141-1154)
```text
    ///           at the curve-close ratio and any dust becomes reserves with
    ///           no LP claim.
    ///        2. **Pure-donation pre-seed.** Attacker `transfer`'d to the
    ///           pair without `mint` (balance > 0, reserves == 0).
    ///           `pair.skim(address(this))` pulls the donation into
    ///           `Bonding`; path then collapses to (1). Donated TOKEN is
    ///           burned alongside the empty-pair mint; donated LT is
    ///           handled by `finalizeGraduation`'s post-bookend
    ///           `_sweepLTToOwner` (which uses `protectedLT` snapshotted
    ///           BEFORE skim, so the donation is correctly classified as
    ///           rebalance residue rather than concurrent-graduation
    ///           escrow). NEVER routed to `LPLock` — `LPLock` has no
    ///           rescue path in v1, so anything that lands there is
    ///           permanently stuck.
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
