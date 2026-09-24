This confirms a solid analog: `LPLock.sol` explicitly has "No withdraw in v1" (line 9), and `Bonding.sol`'s natspec states the LP-seeding regime routes donation pre-seeds to `address(this)` rather than `lpLock` specifically "because donated LT can be swept... `LPLock` has no rescue path in v1, so anything that lands there is permanently stuck." [1](#0-0) [2](#0-1) 

This is directly analogous to the reported bug class: an unprivileged actor can send tokens to a contract with no withdrawal path, permanently freezing funds — same root cause as the original report's "no withdraw function" concern, but reachable via a direct ERC20 transfer to `LPLock` rather than via `fundPool`.

### Title
Direct ERC20 transfer to `LPLock` before or after graduation permanently locks tokens/LT with no rescue path - (File: packages/contracts/src/LPLock.sol)

### Summary
`LPLock` is a bare recipient contract with no `withdraw`, `sweep`, or `rescue` function of any kind — its own natspec states "No withdraw in v1." Any unprivileged wallet can send `Token` or LT ERC20 tokens directly to the `LPLock` contract address via a plain `transfer` call at any time (before graduation, during graduation, or after), and those tokens are permanently unrecoverable, since neither `recordLock` nor any other function in `LPLock` moves tokens out.

### Finding Description
`LPLock.sol` holds only two owner-gated write paths — `initialize` and `addLocker` — plus the locker-gated `recordLock`, none of which transfer tokens out of the contract. [3](#0-2)  The contract's own contract-level natspec states plainly: "Locks LP tokens from graduated tokens. No withdraw in v1." [1](#0-0) 

`Bonding.sol`'s own graduation-seeding design explicitly treats `LPLock` as a black hole for anything beyond the exact `pair.mint` LP tokens it expects: pre-seed donations are deliberately routed to `address(this)` (i.e. `Bonding`, not `LPLock`) specifically because, in the author's own words, "`LPLock` has no rescue path in v1, so anything that lands there is permanently stuck." [2](#0-1)  This confirms the project's own risk model: `LPLock` is a known one-way sink.

Any unprivileged wallet holding the launched `Token`, the LT reserve asset, or any other ERC20 can call `IERC20.transfer(lpLockAddress, amount)` at any time — there is no gate on inbound transfers, since ERC20 `transfer` is fully permissionless and does not go through `Bonding`, `Zap`, or any allowlist. Once tokens land at the `LPLock` address, they are permanently frozen: `recordLock` only checks `IERC20(lpPair).balanceOf(address(this)) >= amount` and never sweeps unrelated ERC20 balances, and no other function exists to move any token out. This applies even to the legitimate LP tokens locked via `recordLock` itself — `LPLock` was explicitly designed with no exit path in v1 — but it also applies to any accidental or malicious stray donation of `Token`/LT sent directly to that address, e.g. by a trader mistakenly targeting the wrong address, or by a griefer wanting to permanently burn value that could otherwise have been rescued.

### Impact Explanation
Any ERC20 balance (launched `Token`, the LT reserve asset, or the graduated LP token itself) sent to `LPLock` is permanently and irrecoverably frozen, since there is no withdraw/rescue/sweep function in the contract at any privilege level, including the owner. This constitutes permanent freezing of funds reachable by a fully unprivileged transaction (a plain ERC20 `transfer`), matching the "permanent freezing of trader, creator, or LP funds" impact bar. Because `LPLock` is a UUPS-upgradeable proxy, in principle a future owner upgrade could add a rescue function, but as deployed in v1 the funds are stuck with no on-chain recovery.

### Likelihood Explanation
Likelihood is high for accidental loss (a trader or bot mis-targeting the `LPLock` address, e.g. from a copy-paste of the wrong contract address for the launched token or LT) and moderate for intentional griefing (an attacker with no other motive than burning value, e.g. to grief the protocol's or a specific launch's accounted reserves, since some accounting paths — like `Bonding`'s pre-seed sweep — explicitly avoid sending to `LPLock` for this exact reason, implying the team is aware the risk is real and reachable).

### Recommendation
Add an owner-gated (or timelocked) `rescueToken(address token, address to, uint256 amount)` function to `LPLock` that excludes the locked LP pair token for a given `token` entry (to preserve the lock invariant), or alternatively excludes only the exact locked `amount` of the pair token per `LockInfo`, while allowing recovery of any other unrelated ERC20 balance (including any surplus of the pair token itself beyond `LockInfo.amount`). This closes the "anything that lands there is permanently stuck" gap that the project's own documentation already identifies as a known risk.

### Proof of Concept
1. Deploy/observe the live `LPLock` proxy address (public, e.g. from `Bonding`'s `lpLock()` getter or on-chain events).
2. From any unprivileged wallet holding `Token` (any launched token) or LT, call `IERC20(token).transfer(lpLockAddress, amount)`.
3. Confirm the transfer succeeds — `LPLock` has no `receive`/`fallback` restriction and imposes no gate on inbound ERC20 transfers.
4. Attempt to recover the funds: enumerate `LPLock`'s external functions (`initialize`, `recordLock`, `addLocker`, `locks`, `isLocker`, `getLock`, `upgradeToAndCall`) — none transfer ERC20 balances out of the contract except the `_authorizeUpgrade`-gated proxy upgrade path, which requires the owner to ship an entirely new implementation.
5. The transferred `amount` is permanently stuck at the `LPLock` address unless/until the owner performs a UUPS upgrade adding a rescue function — which does not exist in the currently deployed v1 implementation.

### Citations

**File:** packages/contracts/src/LPLock.sol (L8-10)
```text
/// @title LPLock
/// @notice Locks LP tokens from graduated tokens. No withdraw in v1.
/// @dev UUPS-upgradeable to support v2 `migrateLT` functionality.
```

**File:** packages/contracts/src/LPLock.sol (L69-98)
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
```

**File:** packages/contracts/src/Bonding.sol (L1143-1154)
```text
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
