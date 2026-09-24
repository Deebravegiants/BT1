### Title
Single-step `transferCreator` admin-style role transfer permanently misdirects future creator fees - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.transferCreator` reassigns a token's `creator` role in a single, unconfirmed step, exactly the bug class Trail of Bits flagged for Folks Finance's `update_admin` methods. Because `FeeVault` attributes all future fee accrual to whatever address `Bonding.tokenInfo(token).creator` currently holds, a creator who fat-fingers the `newCreator` argument (or transfers to an address they don't control, e.g. a contract without a withdrawal path or a burned/typo'd address) permanently and irrevocably redirects all future 0.25% creator fees for that token to an unreachable address, with no propose/accept step to catch or reverse the mistake.

### Finding Description
`transferCreator` performs the role change atomically with no confirmation step: [1](#0-0) 

The only guard is a zero-address check and a `msg.sender == info.creator` check; there is no `pendingCreator` staging value and no requirement that `newCreator` accept the role, unlike this same codebase's own pattern for owner transfers (`Ownable2StepUpgradeable`, explicitly called out in the contract's natspec as protection against "a bad `transferOwnership`... to a fat-fingered... address" bricking owner-only paths): [2](#0-1) 

That protection was deliberately applied to `Ownable2StepUpgradeable` for the protocol owner, but was not extended to `transferCreator`, which changes a role with real, ongoing economic value. `info.creator` is the sole key used to attribute all future fee income for that token: `Zap` reads `Bonding.tokenInfo(token).creator` and forwards it into `FeeVault.accrue`, which credits `creatorBalance[creator]`: [3](#0-2) [4](#0-3) 

Since `creatorBalance` is a simple mapping keyed by the current `info.creator`, once `transferCreator` is called with a wrong address, every subsequent buy/sell fee accrual permanently accumulates under that wrong address with no built-in recovery mechanism — the mistake can only be undone by the new (wrong) address calling `transferCreator` back, which is impossible if that address is uncontrolled, a non-EOA without matching logic, or simply a typo.

### Impact Explanation
This is a direct analog of the reported class: an irrevocable single-step privileged/role-critical state transition with no propose/accept safety net. The impact here is concrete and financial rather than merely administrative: all future creator-fee revenue for the affected token (0.25% of every buy/sell against that token, indefinitely) becomes permanently unclaimable, i.e., permanently frozen, the moment the transaction confirms. Given `Bonding.transferCreator` is explicitly in-scope and reachable by any unprivileged token creator wallet (not a protocol admin), the fund-freezing consequence squarely falls within "permanent freezing of ... creator ... funds."

### Likelihood Explanation
Any of alt.fun's token creators can trigger this at any time by calling `transferCreator` themselves — no special privileges beyond having launched the token are required, and the action is exposed directly through the same interface creators use for legitimate role handoffs (e.g., selling/handing off a launched token's brand). A single mistyped address, paste error, or use of an address the creator does not fully control (multisig not yet deployed, wrong chain's address, etc.) is sufficient, and there is no on-chain feedback or delay to catch it before it takes effect.

### Recommendation
Implement a two-step transfer for the creator role, mirroring the `Ownable2StepUpgradeable` pattern already used elsewhere in this codebase for the owner role:
- Add a `pendingCreator` mapping and a `proposeCreatorTransfer(token, newCreator)` function (callable only by the current `info.creator`) that stages the new address without changing attribution.
- Add an `acceptCreatorTransfer(token)` function that finalizes the transfer, callable only by `msg.sender == pendingCreator[token]`, at which point `info.creator` is updated and `CreatorTransferred` is emitted.
- Optionally allow the current creator to cancel a pending transfer before acceptance.

### Proof of Concept
1. A token creator launches a token via `Zap`/`Bonding` and accrues creator fees normally through trading activity (`FeeVault.accrue` credits `creatorBalance[creator]` on each buy/sell, per `packages/contracts/src/FeeVault.sol:101-123`).
2. The creator calls `bonding.transferCreator(tokenAddress, newCreator)` intending to hand the role to a new wallet they control, but mistypes the address or supplies an address of a contract/EOA they do not actually control:
   `packages/contracts/src/Bonding.sol:738-748` executes `info.creator = newCreator` unconditionally in the same transaction — no staging, no acceptance by `newCreator`.
3. From this point on, every subsequent trade against `tokenAddress` causes `Zap` to call `FeeVault.accrue(token, newCreator, creatorAmount, protocolAmount, isBuy)`, crediting `creatorBalance[newCreator]` (`packages/contracts/src/FeeVault.sol:109-114`).
4. Since the real creator no longer controls `newCreator`, they can never call `FeeVault.claim()` (which pays `creatorBalance[msg.sender]`, `packages/contracts/src/FeeVault.sol:127-135`) to retrieve these funds, and `transferCreator` cannot be called again by the original creator (it requires `msg.sender == info.creator`, which is now `newCreator`). All future creator fees for that token are permanently unclaimable.

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

**File:** docs/contracts-scope.md (L116-121)
```markdown
- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```
