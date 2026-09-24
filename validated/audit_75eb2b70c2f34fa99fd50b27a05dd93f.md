## Finding: `Bonding.transferCreator` Lacks 2-Step Confirmation for Creator Address Changes

While the protocol correctly hardened its owner-facing proxies (`Bonding`, `Zap`, `LPLock`, `FeeVault`) with `Ownable2StepUpgradeable` — explicitly to defend against exactly this bug class per the comment in `test/OwnershipTransfer.t.sol` referencing "issue #323" — the same single-step-transfer footgun still exists on the trader/creator-facing `transferCreator` function, which is unprivileged-caller reachable and directly controls FeeVault fee attribution. [1](#0-0) 

### Title
Single-step `transferCreator` permanently freezes creator fee claims on address mis-entry - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding.transferCreator(tokenAddress, newCreator)` performs a one-shot, unconfirmed reassignment of the `creator` role that gates `FeeVault` fee claims, with no acceptance step from the new address, unlike every other privileged-address setter in the same codebase which now uses `Ownable2StepUpgradeable`.

### Finding Description
`transferCreator` only checks that `newCreator != address(0)` and `newCreator != info.creator`, then immediately overwrites `info.creator` and emits `CreatorTransferred`: [1](#0-0) . There is no `pendingCreator` staging value and no `acceptCreator()` step analogous to `acceptOwnership()`. Fee attribution for `FeeVault.claim()` is resolved purely from `Bonding.tokenInfo(token).creator`: [2](#0-1) . Only the current `creator` may call `transferCreator` (`NotCreator` guard), so once a wrong address is mistakenly set, the legitimate original creator has no path to reverse it — the wrong address is now the only one who can call `transferCreator` or `FeeVault.claim()` for that token.

This is the same class of defect flagged in the external report against `TimeLock.changeOwner`: a single, unconfirmed write to a critical address field with no recovery path if the address is wrong. The developers evidently recognized and fixed this pattern for `owner()` on `Bonding`/`Zap`/`LPLock`/`FeeVault` (see the dedicated regression suite in `test/OwnershipTransfer.t.sol`), but the fix was not applied to `transferCreator`, which sits on the same trust boundary (an address that gates future/pooled fund claims) and is reachable by any unprivileged token creator.

### Impact Explanation
If a creator fat-fingers `newCreator` (mistyped address, wrong checksum, address on a different chain, or any address whose private key they don't hold), all future `FeeVault` creator-fee accruals for that token become permanently claimable only by an address nobody controls. Since `FeeVault.claim()` pays `msg.sender` directly from `creatorBalance[msg.sender]` [3](#0-2) , and `accrue` attributes based on `Bonding.tokenInfo(token).creator`, the pooled 0.25% creator-fee stream on every subsequent buy/sell of that token is permanently frozen/lost with no on-chain recovery mechanism. This is a permanent freezing-of-funds impact under a plausible, single-transaction user-error trigger.

### Likelihood Explanation
Any token creator can trigger this with a single, ordinary transaction — `transferCreator` requires no special privilege, only `msg.sender == info.creator`. Given the general prevalence of address-entry errors in the wild (the exact scenario the external report and the protocol's own `OwnershipTransfer.t.sol` regression suite were written to prevent for the owner role), likelihood is realistic though it depends on user error rather than an adversarial exploit.

### Recommendation
Apply the same two-step pattern already used for `owner()` across `Bonding`, `Zap`, `LPLock`, and `FeeVault` to the creator role: stage `newCreator` in a `pendingCreator[token]` mapping on `transferCreator`, and require an `acceptCreator(token)` call from the pending address (mirroring `Ownable2StepUpgradeable.transferOwnership`/`acceptOwnership`) before `info.creator` is actually overwritten.

### Proof of Concept
1. Creator `C` launches a token via `Bonding.launch`, becoming `tokenInfo[token].creator == C`.
2. `C` calls `bonding.transferCreator(token, D)` where `D` is a mistyped/uncontrolled address (test analog: `test_transferCreator` at [4](#0-3)  shows the transfer takes effect immediately and irreversibly with no confirmation step).
3. `tokenInfo[token].creator` is now `D`; every subsequent `Zap.buy`/`Zap.sell` on `token` accrues the creator-fee share to `FeeVault.creatorBalance[D]` via `_accrueFee`/`accrue` [5](#0-4) .
4. `C` has no `onlyCreator`-gated recovery function to reclaim the role (`NotCreator` reverts any call from `C`), and `D` cannot claim since nobody controls it — all past and future creator fees for `token` are permanently stranded in `FeeVault`.

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

**File:** docs/contracts-scope.md (L117-117)
```markdown
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
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

**File:** packages/contracts/test/Bonding.t.sol (L604-611)
```text
    function test_transferCreator() public {
        (address tokenAddr,) = _launchToken();

        vm.prank(creator);
        bonding.transferCreator(tokenAddr, trader);

        assertEq(bonding.getTokenInfo(tokenAddr).creator, trader);
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
