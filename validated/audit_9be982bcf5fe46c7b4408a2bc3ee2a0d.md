### Title
Blocklisted creator can never claim accrued FeeVault USDC fees, and `transferCreator` does not rescue them - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` always pays out to `msg.sender` with no alternate-recipient parameter, exactly mirroring the Cooler `claimRepaid` bug class where a hardcoded recipient prevents a blocklisted address from ever receiving USDC. `Bonding.transferCreator` — the protocol's only recipient-change mechanism — does not migrate the already-accrued `FeeVault.creatorBalance` mapping entry, so it cannot rescue funds already accrued to a blocklisted creator.

### Finding Description
`FeeVault.accrue` credits creator fees into a mapping keyed by the creator address recorded on `Bonding` at the time of the trade: `$.creatorBalance[creator] += creatorAmount` [1](#0-0) .

The only way to withdraw this balance is `claim()`, which reads and zeroes `creatorBalance[msg.sender]` and then calls `usdc.safeTransfer(msg.sender, amount)` — the recipient is hardcoded to the caller with no ability to redirect the payout to a different address: [2](#0-1) 

Fees are paid in USDC — `docs/contracts-scope.md` states fees are "charged by `Zap` in USDC and forwarded into `FeeVault`" [3](#0-2)  — and USDC (Circle) can blocklist an address, causing any `transfer`/`safeTransfer` to or from that address to revert.

`Bonding.transferCreator` is the only mechanism to change fee attribution, but it only updates `TokenInfo.creator` for *future* accruals via `info.creator = newCreator`; it never touches `FeeVault`'s `creatorBalance` mapping for the *old* creator address: [4](#0-3) 

So if a creator's address is added to the USDC blocklist after fees have already accrued in `creatorBalance[oldCreator]`, calling `transferCreator` changes who earns *new* fees but does nothing to unlock the *already-accrued* balance sitting under the blocklisted address. `claim()` can only ever pay out to `msg.sender`, and a blocklisted address cannot receive USDC no matter who calls on its behalf (in fact, only the blocklisted address itself can ever have `creatorBalance[msg.sender] > 0` for its own funds, and `usdc.safeTransfer` to that same blocklisted address will always revert).

### Impact Explanation
Accrued creator USDC fees become permanently and unrecoverably frozen in `FeeVault` once the creator's address is blocklisted by USDC — there is no admin override, no alternate-recipient parameter, and no migration path via `transferCreator` for previously-accrued balances. This is a permanent freezing of creator funds, matching the Medium severity of the analogous Cooler finding.

### Likelihood Explanation
Reaching this state requires no privileged action — any address that becomes a creator (via `Bonding.launch`, permissionless) and later gets blocklisted by Circle (for any external reason, e.g. sanctions/compliance) will have this happen automatically as soon as further fees accrue to it before the blocklisting is known, or even for balances already accrued prior to blocklisting. This is a realistic real-world scenario given USDC is the fee/reserve asset extensively used across `Zap`/`FeeVault`.

### Recommendation
Add a recipient parameter to `claim()` (e.g. `claim(address recipient)`), gated so only `msg.sender`'s own accrued balance can be redirected, mirroring the recommended fix in the referenced Cooler report:
```solidity
function claim(address recipient) external nonReentrant returns (uint256 amount) {
    FeeVaultStorage storage $ = _s();
    amount = $.creatorBalance[msg.sender];
    if (amount == 0) revert NothingToClaim();
    $.creatorBalance[msg.sender] = 0;
    $.totalAccruedCreator -= amount;
    $.usdc.safeTransfer(recipient, amount);
    emit CreatorFeesClaimed(msg.sender, amount);
}
```
Additionally, consider having `Bonding.transferCreator` (or a dedicated `FeeVault` function callable by the old creator) migrate any outstanding `creatorBalance[oldCreator]` to `newCreator` so a creator can proactively move accrued-but-unclaimed funds before/after a blocklisting event.

### Proof of Concept
1. `creatorA` launches a token via `Bonding.launch`/`Zap.createToken`, becoming `TokenInfo.creator`.
2. Trades occur; `Zap` calls `FeeVault.accrue(token, creatorA, creatorAmount, protocolAmount, isBuy)`, incrementing `creatorBalance[creatorA]` per [1](#0-0) .
3. `creatorA` is added to the USDC blocklist (Circle-side, outside protocol control).
4. `creatorA` calls `Bonding.transferCreator(token, creatorB)` to try to redirect future earnings — this only updates `TokenInfo.creator`, per [4](#0-3) ; `creatorBalance[creatorA]` in `FeeVault` is untouched.
5. `creatorA` calls `FeeVault.claim()`; `amount = creatorBalance[creatorA]` is nonzero, so `usdc.safeTransfer(creatorA, amount)` is attempted per [2](#0-1)  and reverts because USDC blocks transfers to a blocklisted address.
6. The accrued balance is now permanently stuck — `creatorA` cannot claim it (transfer always reverts) and no other address can claim it on `creatorA`'s behalf, since `claim()` is hardcoded to `msg.sender`.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L108-114)
```text
        FeeVaultStorage storage $ = _s();
        if (creatorAmount > 0) {
            if (creator == address(0)) revert ZeroAddress();
            $.creatorBalance[creator] += creatorAmount;
            $.totalAccruedCreator += creatorAmount;
            $.lifetimeCreatorEarned[creator] += creatorAmount;
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

**File:** docs/contracts-scope.md (L114-114)
```markdown
All fees are charged by `Zap` in USDC and forwarded into `FeeVault`. The router holds no fee state — the vault is where balances live and where creators and the protocol claim.
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
