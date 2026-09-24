## Analysis Result

Alt.fun's `Ownable2StepUpgradeable` usage on `Bonding` and `FeeVault` already defends against the exact "lost owner/dao" bug class described in the report — both contracts explicitly note this in their natspec. [1](#0-0) [2](#0-1) 

However, `Bonding.transferCreator` is a genuine single-step privileged-role transfer reachable by an ordinary, unprivileged wallet (the token creator), and it has no confirmation step.

### Title
Single-step `Bonding.transferCreator` permanently locks a token's future creator fee stream on a fat-fingered address - (File: packages/contracts/src/Bonding.sol)

### Summary
`transferCreator(tokenAddress, newCreator)` reassigns the `creator` role for a launched token in one transaction, gated only by `msg.sender == info.creator` and a non-zero-address check. Unlike `Bonding`'s and `FeeVault`'s own owner transfer (which uses `Ownable2StepUpgradeable` specifically to avoid this class of bug), there is no pending/accept two-step flow for the creator role.

### Finding Description
```solidity
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
``` [3](#0-2) 

`info.creator` is the sole source of truth for fee attribution: `Zap` reads `Bonding.tokenInfo(token).creator` and forwards it to `FeeVault.accrue`, which credits `creatorBalance[creator]` for every future buy/sell of that token. [4](#0-3) [5](#0-4) 

`FeeVault.claim()` pays out strictly to `msg.sender`'s own `creatorBalance` entry — there is no admin recovery, no owner override, and no way to re-attribute or reclaim balances credited to a wrong `creator` address. [6](#0-5) 

Because `transferCreator` only checks `newCreator != address(0)` and `newCreator != info.creator`, a single fat-fingered call (typo'd address, wrong checksum, an unowned/inaccessible contract, etc.) permanently and irreversibly reroutes 0.25% of every future buy/sell fee on that token to an address the creator cannot control — with zero on-chain way to undo it, exactly the "incorrect address provided → role forever lost" scenario described in the source report for `dao`.

### Impact Explanation
This is a permanent freeze/loss of the token creator's future fee income (0.25% of every buy/sell in USDC, accruing for the token's entire post-launch lifetime, including post-graduation trading through the HyperSwap pair) with no recovery path — funds sent to `FeeVault` on the creator's behalf become permanently unclaimable by the actual creator once misdirected.

### Likelihood Explanation
Likelihood is low-to-medium: it requires the creator to make a mistake when calling `transferCreator` (e.g., copy-paste error, wrong checksum, or transferring to a contract address that has no way to call `FeeVault.claim()`). This is a plausible, self-inflicted but realistic user error, identical in kind to the audited `dao` issue, and there is no guard rail (no pending/accept step, no timelock, no way to cancel) to catch it before it becomes permanent.

### Recommendation
Implement a two-step transfer for the `creator` role on `Bonding`, mirroring the `Ownable2StepUpgradeable` pattern already used for the contract's `owner`: add a `pendingCreator` mapping set by the current creator via `transferCreator`, and require the new address to call an `acceptCreator(tokenAddress)` function to finalize the change before `info.creator` is updated and fee attribution shifts.

### Proof of Concept
1. Creator `C` launches a token via `Bonding`/`Zap`, and it begins accruing creator fees in `FeeVault.creatorBalance[C]` on every buy/sell. [5](#0-4) 
2. `C` calls `bonding.transferCreator(tokenAddress, X)` where `X` is a mistyped address or a contract with no withdrawal function. [3](#0-2) 
3. All subsequent buys/sells on `tokenAddress` route their 0.25% creator fee into `creatorBalance[X]` via `FeeVault.accrue`. [5](#0-4) 
4. `C` has no way to reverse the transfer (no `NotCreator` check protects them since they were the one who called it, and `X` cannot call `transferCreator` back since `msg.sender != info.creator` unless `X` controls the address); if `X` is inaccessible, all past and future accrued creator fees for that token are permanently unclaimable. [6](#0-5)

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

**File:** packages/contracts/src/FeeVault.sol (L17-21)
```text
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
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

**File:** docs/contracts-scope.md (L116-121)
```markdown
- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```
