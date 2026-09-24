### Title
`Bonding.transferCreator()` allows creator role to be transferred to an address that can never call `FeeVault.claim()`, permanently freezing future creator fees - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding.transferCreator()` lets the current creator repoint `TokenInfo.creator` to any address with only a zero-address and self-transfer check. There is no validation that the new address is actually capable of calling `FeeVault.claim()` (e.g. it is not a contract without a forwarding function, not the `Bonding`/`Zap`/`FeeVault`/`Pair` contract itself, etc.). Since `FeeVault.claim()` pays out strictly to `msg.sender`, once `creator` is set to such an address, every future `FeeAccrued` credit for that token accumulates in `FeeVault.creatorBalance[newCreator]` with no way for anyone to ever retrieve it — a permanent freeze of creator fee funds, directly analogous to the ODSafeManager `transferCollateral()` finding where funds could be routed to an address lacking the structure required to make use of them.

### Finding Description
`transferCreator` only guards against the zero address and a no-op transfer: [1](#0-0) 

That new `creator` value is the sole key used for future fee attribution: `Zap` reads `Bonding.tokenInfo(token).creator` and calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)` on every trade, per the documented fee-accrual flow. [2](#0-1) 

`FeeVault.accrue()` credits the balance to that exact `creator` address, and the *only* withdrawal path, `claim()`, pays strictly to `msg.sender` — there is no owner-mediated rescue or alternate claim-by-address path for creator balances: [3](#0-2) 

If `newCreator` is set to any address that can never itself originate a transaction calling `FeeVault.claim()` — a contract with no such forwarding function (including `Bonding`, `Zap`, `FeeVault`, `Pair`, or a `Token`/LT contract), a precompile-style address, or any other unrecoverable address — every subsequent `creatorAmount` accrued for that token becomes permanently unclaimable. Nothing in `Bonding`, `Zap`, or `FeeVault` allows the owner or anyone else to redirect or rescue an individual creator's `creatorBalance`; only `msg.sender == creator` can call `claim()`.

This mirrors the external report's root cause exactly: a state-mutating function (`transferCollateral()` there, `transferCreator()` here) accepts an arbitrary destination address without verifying that the destination is a "managed" entity capable of using the transferred value (a `SAFEHandler` there, an address able to call `claim()` here), breaking the implicit invariant that the role/asset owner can always retrieve what is attributed to them.

### Impact Explanation
Impact is a permanent freeze of creator trading fees (0.25% of every buy/sell on that token, for the token's entire remaining lifetime, both pre- and post-graduation per the documented fee schedule). Once misdirected, the funds are unrecoverable through any function in `Bonding.sol` or `FeeVault.sol` — there is no admin sweep for a specific creator's `creatorBalance`, only `sweepDonations()` which only handles unbacked `usdc.balanceOf` excess, not backed creator balances. This qualifies as "permanent freezing of ... creator ... funds" per the stated impact criteria.

### Likelihood Explanation
`transferCreator` is a normal, unprivileged, permissionless-to-the-creator function reachable directly by any token creator — no special conditions are required beyond owning the `creator` role for a launched token. A creator can trigger this by mistake (fat-fingering an address, or passing a contract address that has no `claim()`-forwarding capability, e.g. mistakenly passing the `Bonding`, `Zap`, `FeeVault`, or a `Pair`/LT address) or be socially engineered into doing so. There is no simulation/warning at the contract level, and the function performs no code-existence or capability check on `newCreator`.

### Recommendation
Add validation in `transferCreator` mirroring the sponsor-accepted fix in the original report: reject destinations that are known-unusable, at minimum:
- Disallow `newCreator` equal to `address(this)` (`Bonding`), the configured `Zap`/router addresses, `FeeVault`, the token's own `Pair`, or the token/LT addresses themselves.
- Consider requiring a two-step "propose + accept" pattern (similar to `Ownable2StepUpgradeable` already used elsewhere in the codebase) so the new creator must actively call `acceptCreator()` from an address capable of transacting, proving it can eventually call `FeeVault.claim()`, before `TokenInfo.creator` is updated.

### Proof of Concept
1. Creator launches a token via `Zap.createToken`, becoming `Bonding.tokenInfo(token).creator`.
2. Fees accrue normally via trades: `FeeVault.creatorBalance[creator]` grows as `Zap` calls `FeeVault.accrue(...)`.
3. Creator calls `bonding.transferCreator(tokenAddress, address(feeVault))` (or any other contract with no function that calls `FeeVault.claim()`), which succeeds — only the zero-address and self-transfer checks exist:
   `Bonding.sol:738-748`
4. All subsequent trades on `tokenAddress` continue to accrue creator fees to `FeeVault.creatorBalance[address(feeVault)]` (or whichever unusable address was set).
5. No entity can ever call `FeeVault.claim()` as `address(feeVault)` (or the other unusable address) to retrieve these funds — they are permanently locked in the vault, unreachable by `claim()`, `claimProtocol()`, or `sweepDonations()` (the latter only sweeps *unbacked* excess balance, not backed creator balances).

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
