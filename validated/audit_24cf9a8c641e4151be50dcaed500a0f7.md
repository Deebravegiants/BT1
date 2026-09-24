### Title
Single-step, unvalidated `transferCreator` can permanently freeze a creator's accrued and future USDC fees - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.transferCreator()` lets a token's creator reassign the `creator` attribution that `FeeVault` uses to route USDC fee claims. The transfer is single-step and irrevocable: whatever address is passed becomes the sole address capable of calling `FeeVault.claim()` for that token's `creatorBalance`, with no confirmation step and no protocol-level recovery. This mirrors the external report's `LibACL sysAdmin` class of bug — an unrecoverable transfer of a privilege/role to an address that may not be controlled by anyone, permanently losing that privilege.

### Finding Description
`transferCreator` performs the reassignment directly, in one call, with only zero-address and self-transfer checks: [1](#0-0) 

Once `info.creator` is set to `newCreator`, every future `FeeVault.accrue()` call attributes `creatorAmount` to that new address, and only that address can withdraw via `FeeVault.claim()`: [2](#0-1) [3](#0-2) 

There is no owner override or admin path in `FeeVault` or `Bonding` to reset `info.creator` or redirect a stuck `creatorBalance` — `FeeVault`'s only admin levers are `addDepositor`/`removeDepositor`/`setFeeTo`, none of which touch `creatorBalance`. If `newCreator` is mistyped, a not-yet-deployed CREATE2/contract address, an address whose key is lost, or any address that nobody can sign transactions from, all previously accrued and all future creator fees for that token become permanently unclaimable — this is functionally identical to the "grants to an address owned by no one" scenario from the external report, just applied to the fee-claim role instead of `sysAdmin`.

Notably, the same codebase already recognizes and defends against exactly this class of mistake for contract ownership: `Bonding`, `Zap`, `LPLock`, and `FeeVault` all use `Ownable2StepUpgradeable` specifically so that "a bad `transferOwnership` ... would otherwise brick every owner-only path on the live proxy" is avoided, as documented in-line and tested in `OwnershipTransfer.t.sol`: [4](#0-3) 

`transferCreator` has no equivalent pending/accept step, so the same fat-finger/typo risk the team explicitly engineered against for `owner` is left open for `creator`.

### Impact Explanation
Any creator (a fully unprivileged actor — creator status is acquired simply by calling `Zap.createToken`, a permissionless entrypoint) who calls `transferCreator` with a wrong or uncontrolled address permanently loses the ability to claim their 0.25% creator fee share on all past and future buys/sells of that token, for as long as the token trades (curve and post-graduation). Funds keep accruing into `FeeVault.creatorBalance[newCreator]` and `totalAccruedCreator`, sitting in the vault with no way for anyone to ever withdraw them — a permanent freezing of creator funds.

### Likelihood Explanation
Reachable by ordinary user error: any creator can trigger this in a single transaction with no special privilege, and unlike the owner-transfer paths in the same codebase, there's no two-step confirmation to catch a typo before it's final. Given how common fat-finger errors are (motivating the project's own `Ownable2Step` adoption for the `owner` role), and that `transferCreator` sees no equivalent protection, this is a realistic accidental-loss scenario, and also a viable social-engineering/phishing target (tricking a creator into "upgrading" or "verifying" their creator address to an attacker/uncontrolled address).

### Recommendation
Adopt the same two-step pattern already used for contract ownership elsewhere in the codebase: introduce a `pendingCreator` per token set by the current creator, requiring the new address to call an `acceptCreator(tokenAddress)` before `info.creator` is updated. This lets an honest mistake be caught/cancelled before it becomes irreversible, and guarantees the destination address can actually sign a transaction (proving it's controlled by someone) before fee-claim rights are handed over.

### Proof of Concept
1. `creatorA` calls `Zap.createToken(...)` and becomes `Bonding.tokenInfo[token].creator`.
2. Trading accrues USDC fees into `FeeVault.creatorBalance[creatorA]` via `Zap`'s `accrue()` calls.
3. `creatorA` calls `bonding.transferCreator(token, mistypedOrUncontrolledAddress)`. This succeeds immediately (only zero-address/self checks apply) — see `Bonding.sol:738-748`.
4. All subsequent `FeeVault.accrue()` calls for `token` now credit `creatorBalance[mistypedOrUncontrolledAddress]`.
5. Since nobody controls `mistypedOrUncontrolledAddress`, `FeeVault.claim()` can never be called successfully for that balance — both the pre-existing and all future creator fees for `token` are permanently locked in `FeeVault`, with no admin or owner function able to recover or redirect them.

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
