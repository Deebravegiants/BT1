### Title
`transferCreator()` is a single-step ownership transfer with no acceptance step, permanently misdirecting future creator fees to an inaccessible address - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.transferCreator()` lets the current creator reassign the `creator` role for a launched token to any non-zero address in a single transaction, with no pending-acceptance step from the new address.

### Finding Description
`transferCreator` performs a direct, one-step write to `info.creator`:

```solidity
function transferCreator(address tokenAddress, address newCreator) external {
    if (newCreator == address(0)) revert ZeroAddress();
    TokenInfo storage info = _s().tokenInfo[tokenAddress];
    if (msg.sender != info.creator) revert NotCreator();
    if (newCreator == info.creator) revert InvalidInput();
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
``` [1](#0-0) 

`info.creator` is the sole source of fee attribution: every trade's `Zap` call reads it fresh from `Bonding.tokenInfo(token).creator` and forwards it into `FeeVault.accrue(token, creator, ...)`, and only that address can later call `FeeVault.claim()` for the accrued balance, as documented in the fee flow: "Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`)" [2](#0-1) .

Unlike the audited `L2ECO.updateTokenRoleAdmin()`, there is a zero-address guard here, but there is still no second-step acceptance from `newCreator`. If the current creator mistypes the address, pastes a checksum-mismatched address, or targets a contract/address they do not actually control the key for, `transferCreator` permanently redirects **all future** fee accrual for that token to that address with no way to recover: only `msg.sender == info.creator` can call `transferCreator` again, and after the mistake, `info.creator` is the inaccessible address, so the original creator can never reclaim the role or the future fee stream.

By contrast, the same contract deliberately uses `Ownable2StepUpgradeable` for the protocol-owner role specifically to avoid this exact class of bug, per its own natspec: "Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a bad `transferOwnership` can be cancelled... single-step transfer to a fat-fingered or contract-incompatible address would otherwise brick every owner-only path" [3](#0-2) . `transferCreator` was not given the same protection despite controlling an ongoing, indefinite revenue stream (creator fee share of every future buy/sell on that token).

### Impact Explanation
Once misdirected, every subsequent trade's 0.25% creator fee share for that token accrues in `FeeVault` under the wrong, uncontrolled address and is permanently unclaimable by the legitimate creator — a permanent freeze/loss of future creator funds for the life of the token (which can trade indefinitely both pre- and post-graduation). There is no admin recovery path exposed for this since `FeeVault` attribution is keyed by whatever address `Bonding` reports at accrual time.

### Likelihood Explanation
This requires only a mistake by the token's own creator (fat-fingered address, wrong checksum, or an address whose key they don't hold) — no attacker action or privileged access is needed, mirroring the self-inflicted nature of the original report. Given creators call this directly from a wallet/UI, transposition or copy-paste errors are a realistic, low-friction failure mode, and the existing tests (`test_transferCreator`, `test_transferCreator_onlyCreator`) only assert successful transfer and the caller check — no test exercises recovery from a bad transfer, confirming no such path exists. [4](#0-3) 

### Recommendation
Convert `transferCreator` into a two-step pattern analogous to `Ownable2StepUpgradeable` already used for the owner role: `proposeCreator(tokenAddress, newCreator)` sets a pending creator, and `acceptCreator(tokenAddress)` (called by `newCreator`) finalizes the change, with an optional `cancelCreatorTransfer` for the current creator.

### Proof of Concept
1. `creator` launches a token via `Zap.createToken`, becoming `Bonding.tokenInfo(token).creator`.
2. `creator` calls `bonding.transferCreator(token, newCreatorTypo)` where `newCreatorTypo` is a mistyped/uncontrolled address (non-zero, so it passes the guard) — this succeeds in one transaction, as shown by `test_transferCreator` [5](#0-4) .
3. Trading continues on the token via `Zap.buy`/`Zap.sell`; each trade's creator fee accrues in `FeeVault` to `newCreatorTypo` per `docs/contracts-scope.md`'s fee-accrual flow [6](#0-5) .
4. The original creator can never call `transferCreator` again (fails `msg.sender != info.creator`), and `newCreatorTypo` cannot call `claim()` since no one holds its key — all future creator fees for that token are permanently stranded in `FeeVault`.

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

**File:** docs/contracts-scope.md (L116-121)
```markdown
- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```

**File:** packages/contracts/test/Bonding.t.sol (L604-619)
```text
    function test_transferCreator() public {
        (address tokenAddr,) = _launchToken();

        vm.prank(creator);
        bonding.transferCreator(tokenAddr, trader);

        assertEq(bonding.getTokenInfo(tokenAddr).creator, trader);
    }

    function test_transferCreator_onlyCreator() public {
        (address tokenAddr,) = _launchToken();

        vm.prank(trader);
        vm.expectRevert(Bonding.NotCreator.selector);
        bonding.transferCreator(tokenAddr, trader);
    }
```
