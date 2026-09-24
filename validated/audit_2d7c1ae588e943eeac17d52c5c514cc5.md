### Title
Single-step `transferCreator` in Bonding.sol can permanently strand creator fee earnings to an unreachable address - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.transferCreator` reassigns a token's `creator` role in a single, non-reversible step with only a zero-address check. If the current creator provides a typo'd, inaccessible, or otherwise uncontrolled address as `newCreator`, all future creator-fee accrual for that token is redirected to that address in `FeeVault`, and the mistake cannot be corrected because the ability to call `transferCreator` again is now controlled by the very address that can no longer act.

### Finding Description
`transferCreator` only validates that `newCreator != address(0)` and `newCreator != info.creator`, then immediately commits the role change: [1](#0-0) 

```
function transferCreator(address tokenAddress, address newCreator) external {
    if (newCreator == address(0)) revert ZeroAddress();
    TokenInfo storage info = _s().tokenInfo[tokenAddress];
    if (msg.sender != info.creator) revert NotCreator();
    if (newCreator == info.creator) revert InvalidInput();
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
```

This is exactly the single-step role-transfer pattern the external report flags: a zero-address check is present, but there is no verification that the recipient address can actually act on the role (no claim/accept step). `Bonding.tokenInfo(token).creator` is the sole source of creator attribution consumed by the fee-accrual pipeline: `Zap` computes `creatorAmount`/`protocolAmount`, transfers USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)` using this stored creator address (per `docs/contracts-scope.md:117`). `FeeVault.accrue` credits `creatorBalance[creator]` directly and only that address can later call `FeeVault.claim()` to pull it out: [2](#0-1) 

Unlike the contract's own ownership transfer — which the project already hardened with `Ownable2StepUpgradeable` for `Bonding`, `Zap`, `LPLock`, and `FeeVault` precisely to prevent this class of bug (see `packages/contracts/test/OwnershipTransfer.t.sol:13-22`, referencing "issue #323") — `transferCreator` was left as a single-step, unguarded state mutation.

### Impact Explanation
Every buy and sell against the affected token continues to route 0.25% of the 0.75% protocol fee to `FeeVault.creatorBalance[newCreator]` (per the fee split documented in `docs/contracts-scope.md:116`), for the entire remaining lifetime of the token (both on the bonding curve and post-graduation through `Zap`, since fees are charged on every trade regardless of lifecycle). If `newCreator` is a typo'd address, a contract without a fallback for arbitrary calls, or any address the caller does not control, those accrued creator fees become permanently unclaimable — `FeeVault.claim()` can only be invoked successfully by `msg.sender == creatorBalance` key holder, and there is no path to reassign `info.creator` back except calling `transferCreator` again as `msg.sender == info.creator`, which is no longer possible once the role has moved to an inaccessible address. This is a permanent freeze of creator fee funds and a `FeeVault`-side "phantom" balance that will never be withdrawn, matching the report's "brick fees collection" impact class translated onto alt.fun's creator-fee role instead of `OrderBook`'s host role.

### Likelihood Explanation
`transferCreator` is callable by any token's current creator at any time with no delay, confirmation, or address-code/interface check — only a non-zero, non-identical address check. A single fat-fingered call (e.g., wrong checksum, wrong chain's copy-pasted address, or an address for a wallet the creator doesn't actually control) is sufficient to trigger the bug, requiring no cooperation from any other party and no unusual preconditions.

### Recommendation
Convert `transferCreator` into a two-step handoff, mirroring the `Ownable2StepUpgradeable` pattern already used elsewhere in the codebase: have the current creator call a `proposeCreator(token, newCreator)` that stores a pending creator, and require the new address to call `acceptCreator(token)` (`msg.sender == pendingCreator`) before `info.creator` is updated. This guarantees the new address can actually submit transactions before fee attribution moves to it.

### Proof of Concept
1. `creator` launches a token via `Bonding.launch`, becoming `tokenInfo[token].creator`.
2. Trading proceeds via `Zap.buy`/`Zap.sell`; `FeeVault.accrue` credits `creatorBalance[creator]` on each trade.
3. `creator` calls `bonding.transferCreator(token, 0xTypo...)` where `0xTypo...` is a valid non-zero address nobody controls (e.g., an off-by-one digit from the intended new creator, or a burn-style address).
4. `CreatorTransferred` fires; `tokenInfo[token].creator == 0xTypo...`.
5. All subsequent trades continue crediting `FeeVault.creatorBalance[0xTypo...]`.
6. Neither the original `creator` (no longer `info.creator`, so `NotCreator` reverts on any correcting `transferCreator` call) nor anyone else can move the role back or claim the accrued balance — the funds in `FeeVault.creatorBalance[0xTypo...]` are permanently stranded, confirmed by the existing test coverage only asserting the happy-path `test_transferCreator` and the `NotCreator`-gated `test_transferCreator_onlyCreator` (`packages/contracts/test/Bonding.t.sol:604-619`), with no recovery path tested or implemented.

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

**File:** packages/contracts/src/FeeVault.sol (L101-135)
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

    // ─── Claims ──────────────────────────────────────────────────────────

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
