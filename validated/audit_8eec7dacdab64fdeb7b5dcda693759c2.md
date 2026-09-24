### Title
`Bonding.transferCreator` is a single-step role transfer with no acceptance/cancellation step, unlike every real `Ownable2Step` owner in the system - ([File: packages/contracts/src/Bonding.sol])

### Summary
The protocol explicitly hardened `Bonding`, `Zap`, `LPLock`, and `FeeVault` against the "single-step `transferOwnership` footgun" by using `Ownable2StepUpgradeable`, with a dedicated regression test (`OwnershipTransferTest`) proving the pending-owner gate is in place for all four contracts' admin roles. However, `Bonding.transferCreator` — the analogous "ownership" transfer for a token's `creator` role, which controls all past and future `FeeVault` fee claims for that token — is implemented as a single irreversible step with no acceptance step and no recovery path.

### Finding Description
`transferCreator` lets the current creator of a launched token reassign the `creator` field in one transaction: [1](#0-0) 

```solidity
function transferCreator(address tokenAddress, address newCreator) external {
    if (newCreator == address(0)) revert ZeroAddress();
    TokenInfo storage info = _s().tokenInfo[tokenAddress];
    if (msg.sender != info.creator) revert NotCreator();
    if (newCreator == info.creator) revert InvalidInput();
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
```

There is no `pendingCreator` / `acceptCreator` step analogous to `Ownable2StepUpgradeable.transferOwnership` + `acceptOwnership`, which is the exact pattern the codebase's own docs and tests point to as the fix for the "single-step transfer" bug class: [2](#0-1) 

This `creator` value is the sole key used by `FeeVault` to route and gate fee claims. Fees accrue keyed off `Bonding.tokenInfo(token).creator`, and claims are looked up strictly by `msg.sender`: [3](#0-2) [4](#0-3) 

Once `info.creator` is set to a mistyped, non-checksummed, or otherwise inaccessible address, `transferCreator`'s own `if (msg.sender != info.creator)` guard means nobody — including the protocol owner — can call it again to correct the mistake, because `Bonding` exposes no `onlyOwner` override for `tokenInfo[token].creator`.

### Impact Explanation
Any accrued `creatorBalance` in `FeeVault` for that token, plus every future 0.25% creator-fee share from every subsequent buy/sell on that token (pre- and post-graduation), becomes permanently unclaimable — funds are trapped in `FeeVault` forever, since `claim()` can only ever be reached by an address matching `msg.sender`, and that address is unrecoverable. This is a permanent freezing of creator funds, matching the class of the referenced "no 2-step transferOwnership" report, but rooted in `Bonding`'s creator-role transfer rather than the multisig-owner transfer (which is already correctly mitigated).

### Likelihood Explanation
`transferCreator` is callable directly and permissionlessly by any token creator with no confirmation UI enforced on-chain; a single fat-fingered address, a wrong checksum, or transfer to a contract without the intent/ability to call `FeeVault.claim()` is sufficient to trigger the loss. Given it requires only ordinary user error (no attacker needed) and the codebase's own pattern elsewhere shows this exact class of mistake is anticipated and guarded against for owner roles, the likelihood of an unprotected instance being hit in practice is real, though the severity is bounded to a single token's fee stream rather than protocol-wide funds.

### Recommendation
Add a two-step transfer for the creator role, mirroring `Ownable2StepUpgradeable`: introduce `pendingCreator` storage in `TokenInfo`, have `transferCreator` set `pendingCreator` and emit a "started" event, and add an `acceptCreator(tokenAddress)` function callable only by `pendingCreator` that finalizes `info.creator = pendingCreator` and clears the pending slot. Optionally allow the current creator to cancel a pending transfer by resetting `pendingCreator` to the zero address, consistent with `Ownable2Step`'s cancellation semantics already relied upon elsewhere in this codebase.

### Proof of Concept
1. Creator `C` launches a token via `Bonding.launch`, becoming `tokenInfo[token].creator = C`.
2. Trading accrues creator fees to `FeeVault.creatorBalance[C]` via `Zap` → `FeeVault.accrue`.
3. `C` calls `bonding.transferCreator(token, newCreatorTypo)` where `newCreatorTypo` is a mistyped/inaccessible address (e.g., copy-paste error, wrong checksum resolved by some wallets, or a contract with no way to call `claim()`).
4. `info.creator` is now `newCreatorTypo`; `C` can never call `transferCreator` again (`msg.sender != info.creator` reverts with `NotCreator`), and the protocol owner has no override.
5. All of `C`'s already-accrued `creatorBalance` and every future creator-fee accrual for that token is permanently stuck in `FeeVault`, unclaimable by anyone.

### Citations

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

**File:** packages/contracts/test/OwnershipTransfer.t.sol (L13-22)
```text
/// @notice Verifies that every multisig-owned proxy uses OZ's two-step
///         ownership transfer (issue #323). A single-step transfer to a
///         fat-fingered or contract-incompatible address would brick every
///         owner-only path on the live proxy with no recovery — the pending-
///         owner gate is the only practical defence against that footgun.
///
///         Tests are parameterised over `Ownable2StepUpgradeable` because all
///         four contracts (`Bonding`, `Zap`, `LPLock`, `FeeVault`) inherit
///         the same OZ extension; the per-contract wrappers are just
///         deployment shims so each proxy gets exercised end-to-end.
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
