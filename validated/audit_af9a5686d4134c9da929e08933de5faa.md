## Answer

The strongest reachable analog to this bug class in alt.fun is in `FeeVault.claim()`.

### Title
Creator fees can be permanently frozen because `FeeVault.claim()` always pays a fixed, non-redirectable recipient (`msg.sender`) — ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` transfers a creator's entire accrued USDC balance to `msg.sender` with no ability to specify an alternate recipient [1](#0-0) . Because USDC (the fee asset accrued into the vault) is a blacklistable, compliance-controlled stablecoin, and because the accrued balance is permanently keyed to the address that earned it, a creator whose own address is ever frozen/blacklisted by the USDC issuer has no way to move or redirect that balance to a working address — mirroring the original report's pattern of a fixed, cached recipient that cannot be updated by the affected party.

### Finding Description
`accrue()` credits `creatorBalance[creator]` for the address recorded as `Bonding.tokenInfo(token).creator` at fee-accrual time [2](#0-1) . The only way to withdraw that balance is `claim()`, which reads `creatorBalance[msg.sender]` and unconditionally `safeTransfer`s it back to `msg.sender` — the same address the balance is keyed on [1](#0-0) . There is no `claimTo(address to)` variant and no admin/creator-driven balance-migration path.

`Bonding.transferCreator()` only reassigns the `creator` field used for *future* fee attribution inside `Bonding.tokenInfo` — it does not touch, move, or migrate the *already-accrued* `creatorBalance[oldCreator]` sitting in `FeeVault`, which stays permanently keyed to the old address [3](#0-2) . Since `FeeVault` uses `SafeERC20.safeTransfer` on real USDC, any transfer to an address the USDC issuer has blacklisted reverts unconditionally — deterministically, on every call, forever, since `msg.sender` in `claim()` IS the frozen address, and it's the only one authorized to claim `creatorBalance[msg.sender]`.

This is the exact "old/fixed recipient with no redirect option" shape from the source report: `withdrawableCollectionTokenId[collection][tokenId] = bull` there is analogous to `creatorBalance[creator]` here — both cache a recipient at accrual/settlement time, and the withdrawal function sends to that cached address with no way for the affected party to redirect.

### Impact Explanation
Any USDC accrued to a creator whose wallet later becomes blacklisted by Circle (or whatever USDC issuer/variant is deployed) is permanently and unrecoverably locked inside `FeeVault` — `claim()` will revert every single time for that creator, and no other address, including the protocol owner, has any privileged path to move or rescue that specific creator's `creatorBalance` entry. This is a direct, unbounded freezing of creator funds (Medium-to-High depending on frequency of blacklisting events, but categorized Medium per the report's own severity and because it requires an external precondition — blacklisting — not directly triggerable by an attacker against an arbitrary victim without the victim's own compliance history).

### Likelihood Explanation
Requires the creator's own address to be blacklisted by the USDC issuer — an event outside the protocol's control but a documented real-world risk for any protocol handling real (Circle-issued) USDC, and the kind of edge case audit reports for USDC-integrated protocols specifically flag. It does not require any malicious action by another party; it's a systemic design gap (fixed self-only recipient with no rescue), same root cause class as the source report.

### Recommendation
Add a way for the credited creator to redirect their own claim, or for the protocol owner to migrate a stuck balance to a new address supplied by the affected creator, mirroring the source report's fix pattern:

```solidity
function claim(address to) external nonReentrant returns (uint256 amount) {
    FeeVaultStorage storage $ = _s();
    amount = $.creatorBalance[msg.sender];
    if (amount == 0) revert NothingToClaim();
    if (to == address(0)) to = msg.sender;
    $.creatorBalance[msg.sender] = 0;
    $.totalAccruedCreator -= amount;
    $.usdc.safeTransfer(to, amount);
    emit CreatorFeesClaimed(msg.sender, to, amount);
}
```

Alternatively, extend `transferCreator` (or add a dedicated migration function) to also move any outstanding `creatorBalance[oldCreator]` in `FeeVault` to `newCreator`, so a blacklisted creator can recover funds via a fresh address.

### Proof of Concept
1. Creator launches a token via `Bonding.launch` (through `Zap.createToken`), accruing fees to `creatorBalance[creator]` over time via ordinary `Zap.buy`/`Zap.sell` traffic and `FeeVault.accrue` [4](#0-3) .
2. `creator`'s address is later added to the USDC issuer's blacklist (an on-chain, permissionless-to-observe, issuer-controlled event unrelated to alt.fun).
3. `creator` calls `FeeVault.claim()`. `$.usdc.safeTransfer(msg.sender, amount)` reverts every time because `msg.sender` is blacklisted [1](#0-0) .
4. `creator` calls `Bonding.transferCreator(token, newAddress)` hoping to redirect — this only updates future attribution in `Bonding`'s `TokenInfo.creator` [3](#0-2) ; the already-accrued `creatorBalance[creator]` in `FeeVault` is untouched and remains keyed to the blacklisted address, permanently unclaimable.

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

**File:** packages/contracts/src/Zap.sol (L473-487)
```text
    /// @dev Split into creator / protocol shares, transfer to `FeeVault`, then
    ///      `accrue`. The vault trusts allowlisted depositors to pass truthful
    ///      amounts (cross-checked against its USDC balance).
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
