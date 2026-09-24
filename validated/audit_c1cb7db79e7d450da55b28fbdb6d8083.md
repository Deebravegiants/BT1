### Title
Single-step, unconfirmed `transferCreator` permanently misdirects future creator fee earnings - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.transferCreator` reassigns a token's fee-attributed creator in a single transaction with no acceptance step from the new address, unlike `FeeVault`'s own `Ownable2StepUpgradeable` pattern which the codebase explicitly adopted to avoid exactly this class of bug.

### Finding Description
`Bonding.transferCreator` lets the current creator of a launched token immediately reassign `TokenInfo.creator` to any nonzero address in one call, with no two-step confirmation: [1](#0-0) 

This `creator` field is the sole source of fee attribution: `Zap` reads `Bonding.tokenInfo(token).creator` and forwards it to `FeeVault.accrue`, which credits `creatorBalance[creator]` for every subsequent buy/sell fee on that token, as documented in `docs/contracts-scope.md`: [2](#0-1) 

`FeeVault.accrue` credits whatever `creator` address it is given, and `claim()` pays out only to `msg.sender`'s own balance: [3](#0-2) [4](#0-3) 

Notably, the protocol's own `FeeVault` explicitly deploys `Ownable2StepUpgradeable` for exactly this reason — the code comment states a "single-step transfer to a fat-fingered or contract-incompatible address would otherwise brick every owner-only path": [5](#0-4) 

Yet `Bonding.transferCreator`, which controls the exact same class of asset (future USDC fee accrual for a live, continuously-traded token), was implemented as a single-step, non-reversible transfer instead of following the `Ownable2Step` pattern the team is already aware of and uses elsewhere in the same package.

### Impact Explanation
Every buy/sell fee accrued after a mistaken or mistyped `transferCreator` call is credited to the wrong address inside `FeeVault.creatorBalance`. Since `claim()` only pays `msg.sender`, any fees credited to a mistyped, unowned, or otherwise inaccessible address are permanently unclaimable — a real, ongoing loss of creator funds for as long as the token keeps trading (curve and post-graduation, since fees are charged "on every buy/sell (curve and post-grad)" per the fee-schedule note above). There is no `acceptCreator`/two-step confirmation to catch or roll back the mistake, and no admin override exists to reassign `TokenInfo.creator` back. This is a permanent freezing of creator fee income, matching the "Accept only concrete theft or permanent freezing of ... creator funds" criterion.

### Likelihood Explanation
`transferCreator` is a normal, permissionless, single-argument call reachable by any token creator (`msg.sender == info.creator` check only) — the exact scenario described in the source report (a rushed or mistyped ownership/role transfer). No special preconditions, MEV, or attacker cooperation are required; a simple address typo or copy-paste error triggers irrecoverable loss of all future fee income for that token.

### Recommendation
Convert `transferCreator` into a two-step handoff mirroring `Ownable2StepUpgradeable`: store a `pendingCreator` on `initiateTransferCreator(tokenAddress, newCreator)`, and only finalize the reassignment when the new address calls `acceptCreator(tokenAddress)` (`msg.sender == pendingCreator`). This preserves the existing permissionless/creator-gated semantics while eliminating the risk of unrecoverable fee misdirection from a fat-fingered address.

### Proof of Concept
1. Creator launches a token via `Bonding.launch`/`Zap.createToken`; `TokenInfo.creator = creator`.
2. Creator calls `bonding.transferCreator(tokenAddress, newCreatorTypo)` where `newCreatorTypo` is a mistyped/inaccessible address (e.g. a typo'd EOA or a contract without a `claim`/withdraw path). The call succeeds unconditionally as long as `newCreatorTypo != address(0)` and `newCreatorTypo != info.creator`: [6](#0-5) 
3. Any subsequent trade on that token (via `Zap.buy`/`Zap.sell`) accrues creator fees to `newCreatorTypo` in `FeeVault.creatorBalance`.
4. Because `FeeVault.claim()` only pays `msg.sender`'s own balance and there is no recovery path in `Bonding`, all such accrued fees are permanently unclaimable by the original creator.

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

**File:** docs/contracts-scope.md (L116-121)
```markdown
- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```

**File:** packages/contracts/src/FeeVault.sol (L16-21)
```text
///      so a buggy depositor can't inflate balances beyond delivered funds.
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
