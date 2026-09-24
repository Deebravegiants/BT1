### Title
Creator fees in `FeeVault` become permanently unclaimable if the creator's address is blacklisted by USDC - (File: `packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claim()` pays out the caller's entire pooled creator balance to `msg.sender` with no way to specify an alternate receiver [1](#0-0) . USDC (Circle) has an on-chain blacklist function that can make `transfer`/`transferFrom` to a specific address revert unconditionally. If a token creator's address is ever added to that blacklist, `claim()` will revert forever, permanently freezing every dollar of creator fees the vault has accrued for that address — across every token that creator has ever launched, since `creatorBalance` is a single pooled mapping keyed by creator address, not per-token.

### Finding Description
`FeeVault.accrue` credits `creatorBalance[creator] += creatorAmount` for every buy/sell fee routed through `Zap` [2](#0-1) . The only way to withdraw this balance is `claim()`:

```solidity
function claim() external nonReentrant returns (uint256 amount) {
    FeeVaultStorage storage $ = _s();
    amount = $.creatorBalance[msg.sender];
    if (amount == 0) revert NothingToClaim();
    $.creatorBalance[msg.sender] = 0;
    $.totalAccruedCreator -= amount;
    $.usdc.safeTransfer(msg.sender, amount);
    emit CreatorFeesClaimed(msg.sender, amount);
}
``` [1](#0-0) 

The recipient is hardcoded to `msg.sender` — the caller has no `receiver` parameter to redirect the payout. This is exactly the same shape as the Maia `redeemDeposit` bug: an address-bound payout with no override, backed by a real-world blacklistable token (USDC). Unlike `claimProtocol()`, whose payout always goes to an admin-controlled `feeTo` that the owner can rotate away from a blacklisted address [3](#0-2) , there is no equivalent escape hatch for creators.

Critically, `Bonding.transferCreator` — the only creator-role migration mechanism — only updates `tokenInfo[token].creator` for **future** fee attribution; it does not touch the already-accrued balance sitting in `FeeVault.creatorBalance[oldCreator]`:
```solidity
function transferCreator(address tokenAddress, address newCreator) external {
    ...
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
``` [4](#0-3) 

So a blacklisted creator cannot use `transferCreator` to rescue funds already sitting in `FeeVault` under their old address — that balance is orphaned. Because `creatorBalance` is pooled across all tokens a creator has launched (per the project's own documentation: "`FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched" [5](#0-4) ), a single blacklisting event freezes fee revenue from every token that creator has ever created, not just one.

### Impact Explanation
Once a creator's address is blacklisted by USDC:
- `claim()` reverts on every attempt (USDC's `transfer` to the blacklisted address always reverts).
- `creatorBalance[creator]` is permanently non-zero but permanently unclaimable — the USDC is locked inside `FeeVault` forever, with no recovery function, no admin override, and no way for the creator to redirect the payout.
- This affects the pooled fee revenue from every token launched by that address, which can be a non-trivial and ever-growing sum given `lifetimeCreatorEarned` never decrements and new accruals keep landing on the same blacklisted key via `accrue`.

This satisfies the "permanent freezing of trader/creator funds" bar for Medium severity.

### Likelihood Explanation
USDC blacklisting is a documented, real, and non-hypothetical capability of the Circle-issued token this protocol uses as its fee currency (`$.usdc` in `Zap`/`FeeVault`). Unlike the underlying LT (BounceTech), which is out of scope for this analysis, USDC's blacklist behavior is a known operational risk that many prior audits/contests have flagged for exactly this pattern (hardcoded payout recipient + blacklistable payment token). The trigger requires no protocol bug beyond the missing receiver parameter — any creator whose address is later sanctioned/blacklisted (a real-world event outside the protocol's control) hits this permanently.

### Recommendation
Add a `claim(address receiver)` variant (or a pull-based / two-step withdrawal, or an owner-gated `rescueCreatorBalance(address creator, address to)` migration path) so a creator (or, in emergency, the protocol owner acting on the creator's behalf with appropriate authorization) can redirect an already-accrued `creatorBalance` to an unblacklisted address instead of it being permanently stuck. At minimum, mirror the `claimProtocol`/`feeTo` pattern by allowing `transferCreator` (or a dedicated function) to also migrate the outstanding `FeeVault.creatorBalance[oldCreator]` to the new creator address.

### Proof of Concept
1. `owner.addDepositor(zap)`; `Zap` accrues fees for `creator` across tokens A, B, C via `_accrueFee` → `FeeVault.accrue`, so `creatorBalance[creator]` grows to a meaningful sum [6](#0-5) .
2. Circle (external, outside protocol control) adds `creator` to USDC's blacklist.
3. `creator` calls `FeeVault.claim()`. `$.usdc.safeTransfer(msg.sender, amount)` reverts because USDC's `transfer` blocks transfers to a blacklisted address [7](#0-6) .
4. `creator` calls `Bonding.transferCreator(tokenA, newAddress)` for each token they launched — this only redirects **future** accruals; `FeeVault.creatorBalance[creator]` (the already-accrued sum) is untouched and remains keyed to the blacklisted address [4](#0-3) .
5. `creatorBalance[creator]` is now permanently unclaimable; the USDC sits in `FeeVault` indefinitely with no recovery path.

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

**File:** packages/contracts/src/FeeVault.sol (L137-145)
```text
    function claimProtocol() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        amount = $.protocolBalance;
        if (amount == 0) revert NothingToClaim();
        $.protocolBalance = 0;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit ProtocolFeesClaimed(feeTo_, amount);
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

**File:** docs/contracts-scope.md (L118-118)
```markdown
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
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
