Confirmed: `transferCreator` (Bonding.sol:738-748) is unrestricted except for the `msg.sender == info.creator` check — a blacklisted creator can call it to reassign the `creator` role to a fresh address. However, `FeeVault.claim()` still won't help retroactively because `creatorBalance[creator]` is keyed to the *old* address that already accrued the balance, and `transferCreator` only changes `Bonding`'s `tokenInfo.creator` (used for *future* `accrue` attribution) — it does **not** move the already-accrued `FeeVault.creatorBalance[oldCreator]` to the new address. So a blacklisted creator's already-accrued balance is stuck under their own blacklisted key with no recipient override in `claim()`.

### Title
Creator fees permanently frozen in FeeVault if creator address is blacklisted by USDC - (File: packages/contracts/src/FeeVault.sol)

### Summary
`FeeVault.claim()` pays out the caller's accrued USDC balance exclusively to `msg.sender` via `$.usdc.safeTransfer(msg.sender, amount)`, with no ability to specify an alternate recipient. USDC (the vault's fixed accounting asset) is a real-world upgradeable, blacklistable stablecoin. If a token creator's address is ever added to USDC's blacklist, their entire accrued `creatorBalance` becomes permanently unclaimable, mirroring the reported `MainVault.withdrawRewards()` bug class.

### Finding Description
`FeeVault` accrues creator fees per-creator address in `creatorBalance[creator]` via `accrue()` [1](#0-0) , and pays them out strictly to `msg.sender` in `claim()`: [2](#0-1) 

There is no `_receiver`/`_recipient` parameter analogous to `MainVault.deposit(_amount, _receiver)` / `withdraw(_amount, _receiver, _owner)` in the reference report. If the vault's fixed `usdc` token (set once at `initialize` and never rotated) ever blacklists a creator's address — a real, standing capability of canonical USDC (`isBlacklisted`, as codified even in the repo's own `forge-std` fork-test helpers referencing mainnet USDC's blacklist selector `0xfe575a87`) — `usdc.safeTransfer(msg.sender, amount)` inside `claim()` unconditionally reverts for that address for as long as the blacklist entry stands.

The only escape hatch present is `Bonding.transferCreator(tokenAddress, newCreator)`, callable only by the current `info.creator`: [3](#0-2) 
This reassigns *future* `Bonding.tokenInfo(token).creator` attribution used by `Zap`/`accrue()` going forward, but it never touches `FeeVault.creatorBalance[oldCreator]`, `lifetimeCreatorEarned[oldCreator]`, or `totalAccruedCreator` — the already-accrued balance sits keyed to the blacklisted address in `FeeVault`'s own storage, with `claim()` having no path to redirect it. A blacklisted creator therefore cannot self-rescue via `transferCreator` because that call only redirects fees accrued after the transfer, not the funds already pooled under their old, now-unclaimable key.

### Impact Explanation
All USDC fees a creator has accrued up to the point of blacklisting are permanently locked inside `FeeVault`. Since `totalAccruedCreator` still counts this balance as "backed" (per the accrue/underfund/`sweepDonations` accounting), it can never be swept out by `sweepDonations()` either — `sweepDonations` only pays out balance strictly above `totalAccruedCreator + protocolBalance`. This is a permanent, protocol-wide freeze of creator funds with no recovery path, matching the severity of the referenced analog (frozen rewards for any blacklisted user).

### Likelihood Explanation
Reachable by any unprivileged creator address becoming blacklisted by the fixed `usdc` token set at `FeeVault.initialize`. While `alt.fun` doesn't control USDC's blacklist policy, the report's stated bug-class premise — "many core tokens are upgradable...such blacklist possibility can be not in place now, but it's possible to introduce it" — applies directly since `FeeVault`'s reserve asset is exactly USDC, a canonical blacklistable token, and the vault's `claim()` path offers no recipient override or admin rescue mechanism for this scenario.

### Recommendation
Add a `claimTo(address recipient)` variant (or a `_receiver` parameter on `claim()`, gated to `msg.sender == creator`) that lets a creator redirect their pooled `creatorBalance` payout to an alternate, non-blacklisted address, mirroring the `_receiver` pattern already used in the referenced `MainVault.deposit`/`withdraw`. Alternatively, extend `transferCreator` (or add a dedicated `FeeVault` admin/owner rescue function) to also migrate the already-accrued `creatorBalance[oldCreator]` to `newCreator` atomically with the `Bonding` creator-role transfer.

### Proof of Concept
1. `Zap.buy`/`sell` accrue fees for `creator` via `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`, growing `creatorBalance[creator]`.
2. The real-world USDC contract blacklists `creator`'s address (USDC's actual `isBlacklisted` mechanism).
3. `creator` calls `FeeVault.claim()`. `$.usdc.safeTransfer(msg.sender, amount)` reverts because `msg.sender` is blacklisted.
4. `creator` calls `Bonding.transferCreator(tokenAddress, newAddress)` hoping to redirect the claim — this only updates `tokenInfo.creator` for future accruals; `FeeVault.creatorBalance[creator]` (the already-pooled balance) remains keyed to the blacklisted address.
5. `newAddress` calls `FeeVault.claim()` and receives `creatorBalance[newAddress]` (0, or only fees accrued after the transfer) — the pre-existing balance under the blacklisted `creator` key is unreachable forever.

### Citations

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
