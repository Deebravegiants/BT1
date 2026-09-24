### Title
Creator role and its accrued FeeVault balance are permanently unrecoverable if the creator key is lost/abandoned, with no owner override - (File: packages/contracts/src/Bonding.sol, packages/contracts/src/FeeVault.sol)

### Summary
The reported UXDCouncilToken bug class is: a privileged right is bound exclusively to `msg.sender == holder`, with no admin/owner escape hatch, so if the rightful holder becomes unavailable (resigns, loses keys) the right is permanently stuck and cannot be reassigned or reclaimed by governance. alt.fun reproduces this exact shape for the token-creator role: `Bonding.transferCreator` can only be invoked by the current `info.creator`, and `FeeVault.claim()` pays out strictly to `msg.sender`'s own `creatorBalance`. Neither `Bonding` nor `FeeVault` exposes any owner-gated path to reassign a token's creator or to redirect/rescue a stranded creator's accrued fee balance.

### Finding Description
`Bonding.transferCreator` is `msg.sender`-gated with no `onlyOwner` fallback: [1](#0-0) 

`FeeVault.claim()` pays out only to the calling address's own tracked balance, with no admin-controlled redirect: [2](#0-1) 

The creator identity is set once at `launch` and can only ever be changed by the current holder calling `transferCreator` themselves; the contract owner has `onlyOwner` powers over `addDepositor`/`removeDepositor`/`setFeeTo` in `FeeVault`, but none over `creatorBalance` reassignment or `Bonding`'s `info.creator` field: [3](#0-2) 

This mirrors the UXDCouncilToken pattern precisely: a right (here, the creator's 0.25%-of-trade fee stream and the ability to reassign the creator role) is permanently and exclusively bound to one address's private key, with the protocol owner powerless to intervene if that key becomes inaccessible or the person "resigns" (stops operating the wallet). Docs confirm creator fee attribution flows exclusively through `Bonding.tokenInfo(token).creator`, "updatable via `transferCreator`" — i.e., updatable only by the current creator, never by the protocol: [4](#0-3) 

### Impact Explanation
If a token creator's key is lost, compromised (private key leaked but attacker doesn't call `transferCreator`), or the creator simply abandons the project, their `creatorBalance` in `FeeVault` keeps accruing (0.25% of every buy/sell on that token forever) but becomes permanently unclaimable — `claim()` can only be called successfully by `msg.sender == creator`, and there is no owner-level sweep/redirect function. This is a permanent freeze of creator funds, matching the "Validate" criterion for permanent freezing of creator funds. Separately, `transferCreator`'s single point of failure means the protocol can never remediate a compromised/abandoned creator address even in an emergency, since only that same address can hand off the role — structurally identical to UXDCouncilToken's `burn()` being callable only by the token holder with no owner override.

### Likelihood Explanation
This requires no attacker action at all — it triggers naturally any time a creator loses their key, stops operating their wallet, or otherwise becomes unavailable after their token has accrued trading volume, which is a normal and expected occurrence for a permissionless token-launch platform. No cooperation from other parties or complex preconditions are needed; the mere passage of time and continued trading against the token is sufficient to accrue an unrecoverable balance.

### Recommendation
Add an owner-gated recovery path, mirroring the report's own suggested fix pattern (adding a privileged parameter + `onlyOwner` modifier instead of relying purely on `msg.sender`):
- In `Bonding`, add an `onlyOwner` function (e.g., `adminTransferCreator(address token, address newCreator)`) usable only in emergencies (stale creator, provable key loss, abuse), separate from the permissionless `transferCreator`.
- In `FeeVault`, add an `onlyOwner` function to move a stranded `creatorBalance[oldCreator]` to a new address once `Bonding`'s creator record has been updated, so accrued-but-unclaimed fees are not permanently frozen.

### Proof of Concept
1. Creator launches a token via `Bonding.launch`, is recorded as `info.creator`, and fees begin accruing to `FeeVault.creatorBalance[creator]` via `Zap` trades calling `FeeVault.accrue`.
2. Creator's private key is lost/abandoned after meaningful trading volume has accrued fees.
3. `FeeVault.claim()` can only pay `msg.sender`'s own balance — [2](#0-1)  — so the accrued `creatorBalance` for that address is now permanently stuck; no other address (including the owner) can call `claim()` on its behalf or redirect the balance.
4. `Bonding.transferCreator` cannot be used to route future fee attribution to a new address either, since it requires `msg.sender == info.creator` — [1](#0-0)  — which the lost key can never satisfy again.
5. Result: an ever-growing, permanently frozen USDC balance in `FeeVault`, with the protocol owner having no on-chain mechanism to remediate it — the same structural flaw as the reported UXDCouncilToken issue.

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

**File:** packages/contracts/src/FeeVault.sol (L162-193)
```text
    // ─── Admin ───────────────────────────────────────────────────────────

    function addDepositor(
        address depositor
    ) external onlyOwner {
        if (depositor == address(0)) revert ZeroAddress();
        if (!_s().depositors.add(depositor)) revert DepositorAlreadyAdded();
        emit DepositorAdded(depositor);
    }

    function removeDepositor(
        address depositor
    ) external onlyOwner {
        if (!_s().depositors.remove(depositor)) revert DepositorNotFound();
        emit DepositorRemoved(depositor);
    }

    /// @notice Set the protocol fee recipient.
    /// @dev Protocol fees are pooled and paid to whoever is `feeTo` at claim
    ///      time, so rotating here redirects the entire outstanding
    ///      `protocolBalance` — and any sweepable donations — to `feeTo_`. Call
    ///      `claimProtocol()` (and `sweepDonations()`) first to settle the
    ///      pending balance to the current recipient before rotating.
    function setFeeTo(
        address feeTo_
    ) external onlyOwner {
        if (feeTo_ == address(0)) revert ZeroAddress();
        FeeVaultStorage storage $ = _s();
        address old = $.feeTo;
        $.feeTo = feeTo_;
        emit FeeToUpdated(old, feeTo_);
    }
```

**File:** docs/contracts-scope.md (L112-121)
```markdown
## Fees & FeeVault

All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state — the vault is where balances live and where creators and the protocol claim.

- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
```
