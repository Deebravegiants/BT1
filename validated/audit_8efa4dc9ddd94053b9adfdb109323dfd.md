### Title
`transferCreator` performs an unconfirmed, single-step creator-address change that can permanently misdirect a token's future fee earnings - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.transferCreator` reassigns the `creator` field of a launched token's `TokenInfo` in a single transaction with no acceptance step from the new address, unlike every privileged-role transfer in the same codebase (`Bonding`, `Zap`, `LPLock`, `FeeVault` owners all use `Ownable2StepUpgradeable`) which explicitly guards against exactly this class of fat-finger risk.

### Finding Description
`transferCreator` is called directly by the token's current `creator` and writes `newCreator` into storage immediately: [1](#0-0) 

There is no `pendingCreator` / confirmation step analogous to the `Ownable2StepUpgradeable` pattern the same contract's authors deliberately adopted for the owner role, as documented in the contract's own header comment: [2](#0-1) 

and verified by a dedicated regression suite covering exactly this footgun for `Bonding`, `Zap`, `LPLock`, and `FeeVault`: [3](#0-2) 

`info.creator` is the sole attribution key used by `FeeVault` for all future creator-fee accrual (`Zap` reads `Bonding.tokenInfo(token).creator` and forwards it into `FeeVault.accrue`): [4](#0-3) 

A single mistyped, unreachable (e.g. exchange deposit address that doesn't forward, precompile-adjacent address, or simple copy-paste error), or otherwise wrong `newCreator` argument passed to `transferCreator` immediately and irrevocably severs the true creator from `transferCreator` itself (only `info.creator` can call it again) and from all `FeeVault.claim()` proceeds accrued from that point on, with zero opportunity to cancel or correct the change.

### Impact Explanation
Every buy/sell on the token accrues 0.25% creator fee in USDC to `FeeVault`, attributed to whatever address sits in `info.creator`. Once `transferCreator` is called with a wrong address, that address becomes both the sole future fee recipient and the only party who can call `transferCreator` again to fix it — if that address is uncontrolled or unreachable, all future creator fees for that token are permanently and unrecoverably locked away from the legitimate creator. This is a direct freezing-of-creator-funds impact matching the Medium severity of the referenced report (wrong admin/treasury address locking funds), just scoped to the creator-fee-attribution role rather than protocol ownership.

### Likelihood Explanation
Likelihood is non-trivial: `transferCreator` is a plain, permissionless-to-the-creator, single-argument address-setter with no additional validation beyond non-zero and non-identical checks, making a fat-finger or copy-paste mistake plausible, especially since creators may call it directly (e.g. via block explorer) without frontend safeguards. The codebase's own authors clearly recognized this exact class of risk is real enough to justify a two-step pattern for owner transfers elsewhere, but did not apply the same protection here.

### Recommendation
Add a two-step confirmation to `transferCreator`, mirroring the `Ownable2StepUpgradeable` pattern already used elsewhere in the contract: store the proposed address in a `pendingCreator[tokenAddress]` mapping and require the new address to call an `acceptCreator(tokenAddress)` function before `info.creator` is updated, emitting `CreatorTransferred` only on acceptance.

### Proof of Concept
1. Creator `C` launches a token via `Bonding.launch`, becoming `tokenInfo[token].creator == C`.
2. `C` calls `bonding.transferCreator(token, X)` where `X` is a mistyped or unreachable address (see `test_transferCreator`, which shows the call succeeds unconditionally as long as `msg.sender == info.creator`): [5](#0-4) 
3. `info.creator` is now `X`; every subsequent buy/sell accrues creator fees to `X` in `FeeVault`.
4. `C` can no longer call `transferCreator` (reverts with `NotCreator`, per `test_transferCreator_onlyCreator`) and has no path to recover attribution or the underlying claimable USDC balance building up under `X` in `FeeVault`.

### Citations

**File:** packages/contracts/src/Bonding.sol (L37-41)
```text
/// @dev Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
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

**File:** docs/contracts-scope.md (L117-121)
```markdown
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```

**File:** packages/contracts/test/Bonding.t.sol (L604-611)
```text
    function test_transferCreator() public {
        (address tokenAddr,) = _launchToken();

        vm.prank(creator);
        bonding.transferCreator(tokenAddr, trader);

        assertEq(bonding.getTokenInfo(tokenAddr).creator, trader);
    }
```
