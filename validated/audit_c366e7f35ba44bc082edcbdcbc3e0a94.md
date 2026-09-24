### Title
`transferCreator` uses a single-step ownership transfer with no destination-address validation, permanently orphaning a token's fee-attribution role - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.transferCreator` lets the current `creator` of a launched token repoint the `creator` field to any new address in a single transaction, guarded only by a zero-address check. Unlike the four owner-controlled contracts (`Bonding`, `Zap`, `LPLock`, `FeeVault`), which were hardened with `Ownable2StepUpgradeable` specifically to avoid this exact bug class (see `packages/contracts/test/OwnershipTransfer.t.sol`), the per-token `creator` role has no such protection. A mistyped, contract-incompatible, or otherwise uncontrolled `newCreator` permanently redirects all future `FeeAccrued` creator-fee attribution for that token to an address nobody can call `FeeVault.claim()` from.

### Finding Description
`transferCreator` performs the role hand-off in one step: [1](#0-0) 

The only checks are `newCreator != address(0)` and `newCreator != info.creator`; there is no acceptance/claim step by the new creator and no way for the caller to verify the destination is a controllable EOA/contract before the role moves. This is the identical bug class from the external report: `Airdrop.setOwner` sets a privileged pointer in a single call guarded only by a zero-address check, with the same consequence — irrecoverable loss of the privileged capability if the destination is wrong.

The consequence here is fee-attribution loss rather than admin loss, because `creator` is read live by `Zap`/`FeeVault` on every trade: [2](#0-1) 

`FeeVault.accrue` credits `creatorBalance[creator]` using whatever `creator` `Bonding.tokenInfo(token).creator` currently reports, and only that exact address can withdraw it via `claim()`: [3](#0-2) 

If `transferCreator` is called with an address the caller does not actually control (typo, wrong chain's address, a non-payable/incompatible contract, a burn-style address that isn't literally `address(0)`), every subsequent buy/sell on that token accrues 0.25% of volume into `creatorBalance[newCreator]`, which is now permanently unclaimable — no `claim()` call can ever originate from that address. The protocol explicitly recognized this exact risk class for the owner roles (hence `Ownable2StepUpgradeable` + `OwnershipTransferTest`) but left `transferCreator` as a bare single-step setter.

### Impact Explanation
Each graduated or actively-traded token accrues creator fees continuously (0.25% of every buy/sell). A bad `transferCreator` call freezes all future creator-fee accrual for that specific token forever inside `FeeVault`, with no recovery path (no owner override, no second-step acceptance, no re-`transferCreator` since the caller no longer controls `info.creator`). This is a permanent freezing of creator funds, scoped per-token but with no cap on how much volume/fees can accumulate against the dead address over the token's lifetime.

### Likelihood Explanation
`transferCreator` is callable by any token creator at any time with no restrictions beyond the zero-address check, and creators are unprivileged, permissionless actors by design (anyone can call `Zap.createToken`). Typos and copy-paste errors on addresses are a common real-world occurrence, and the function provides no safety net (no pending-creator acceptance step, no event-based dry-run) — the class of bug is common enough that the protocol itself already paid to fix it for the owner roles.

### Recommendation
Apply the same `Ownable2StepUpgradeable`-style two-phase pattern already used for `Bonding`/`Zap`/`LPLock`/`FeeVault` ownership to the per-token `creator` role: add a `pendingCreator` mapping set by `transferCreator`, and require the new address to call `acceptCreator(tokenAddress)` before `info.creator` is updated. This preserves permissionlessness while eliminating the single-step footgun.

### Proof of Concept
1. Token creator `C` launches a token via `Zap.createToken`, becoming `Bonding.tokenInfo(token).creator == C`.
2. Trading occurs; `Zap` calls `FeeVault.accrue(token, C, creatorAmount, protocolAmount, isBuy)` on every trade, crediting `creatorBalance[C]`.
3. `C` calls `bonding.transferCreator(token, newCreator)` where `newCreator` is a mistyped address (e.g., missing a hex digit, or a checksum-mismatched paste) that `C` does not control.
4. `Bonding.transferCreator` succeeds because `newCreator != address(0)` and `newCreator != C`; `info.creator` is now the uncontrolled address.
5. All subsequent trades on `token` call `FeeVault.accrue(token, newCreator, ...)`, crediting `creatorBalance[newCreator]`.
6. No account can call `FeeVault.claim()` as `newCreator`; the accruing USDC balance for this token's creator fees is permanently locked in `FeeVault`.

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
