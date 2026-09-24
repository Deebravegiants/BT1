Confirmed: `creatorBalance` is keyed strictly by `address creator` in `FeeVault.sol`, and `claim()` always pays `msg.sender` with no way to specify an alternate recipient.I already have sufficient detail from the earlier read of `FeeVault.sol:127-135` (the `claim()` function). I have what I need to finalize the analog analysis.

### Title
Creator fee balances are permanently frozen if the creator address gets blacklisted by USDC, with no way to redirect the claim - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` pays out the caller's pooled creator USDC balance to `msg.sender` only, with no parameter to specify an alternate recipient. Because creator fee balances are accrued and stored keyed strictly by `address creator` in `creatorBalance[creator]`, if that specific address is ever blacklisted by USDC (a realistic scenario since USDC is a centrally-blacklistable token and this is exactly the class of bug described in the source report), the already-accrued balance for that address becomes permanently unclaimable — `safeTransfer(msg.sender, amount)` inside `claim()` will revert every time it's attempted, since USDC blocks transfers to blacklisted addresses.

### Finding Description
`FeeVault.accrue()` credits `$.creatorBalance[creator] += creatorAmount` where `creator` is `Bonding.tokenInfo(token).creator` at the time each buy/sell fee is charged [1](#0-0) . The only withdrawal path is `claim()`:
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
``` [2](#0-1) 

There is no way to claim on behalf of another address or to redirect the transfer destination. `Bonding.transferCreator()` only reassigns *future* fee attribution — it changes `info.creator` on `Bonding`'s `TokenInfo` going forward, so subsequent `accrue()` calls credit the new address — but it does not, and cannot, move USDC that has *already* accrued under the old (now-blacklisted) address in `FeeVault.creatorBalance[oldCreator]`:
```solidity
function transferCreator(address tokenAddress, address newCreator) external {
    if (newCreator == address(0)) revert ZeroAddress();
    TokenInfo storage info = _s().tokenInfo[tokenAddress];
    if (msg.sender != info.creator) revert NotCreator();
    if (newCreator == info.creator) revert InvalidInput();
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
``` [3](#0-2) 

Since `creatorBalance` is keyed purely by address with no owner-assist or self-service migration function, and `claim()` hardcodes the recipient to `msg.sender`, any USDC accrued prior to a blacklist event is stuck: the blacklisted address can never successfully call `usdc.safeTransfer(msg.sender, amount)` for itself, and no other account (not even `newCreator` after a `transferCreator` call) can claim that specific pre-existing balance since it's keyed to the old address, not the token.

### Impact Explanation
This is a permanent freeze of legitimately earned creator fee funds — the same class of impact as the source report (frozen collateral). The frozen amount is bounded by the creator's accrued 0.25% fee share for their tokens' trading volume up to the blacklist event, which for popular tokens can be a material and permanently unrecoverable sum for that creator, satisfying Medium severity.

### Likelihood Explanation
Reaching this state requires no privileged action from within alt.fun — any creator (an unprivileged actor who calls `Zap.createToken`) accrues fees automatically as their token trades. The only external dependency is USDC's admin blacklisting the creator's address for reasons entirely outside the protocol's control (e.g. OFAC sanctions, exchange-linked compliance actions). This mirrors exactly the low-but-nonzero-probability scenario the original report also rates as Medium.

### Recommendation
Add a way for a creator to redirect their claim, e.g. an explicit `claimTo(address to)` function that transfers `creatorBalance[msg.sender]` to a caller-specified `to` address, or add a permissioned/self-service migration function that moves an existing `creatorBalance[oldCreator]` entry to a new address (distinct from `transferCreator`'s forward-looking attribution change), so a blacklisted creator is not permanently locked out of already-earned funds.

### Proof of Concept
1. Creator C launches a token via `Bonding`/`Zap.createToken`, becomes `info.creator` for that token.
2. Trading occurs; `Zap` charges 0.75% fees and calls `FeeVault.accrue(token, C, creatorAmount, protocolAmount, isBuy)`, accumulating `creatorBalance[C]`.
3. USDC's centralized admin blacklists address `C` (independent of alt.fun).
4. C calls `Bonding.transferCreator(tokenAddress, newAddr)` to redirect *future* fee attribution — this succeeds and updates `info.creator`, but does not touch the existing `FeeVault.creatorBalance[C]` balance.
5. C (or anyone) calls `FeeVault.claim()` from `C`; `amount = creatorBalance[C]` is nonzero, but `usdc.safeTransfer(C, amount)` reverts because USDC blocks transfers to the blacklisted `C`.
6. `newAddr` cannot claim it either, since `claim()` only reads `creatorBalance[msg.sender]`, and the pre-existing balance is keyed to `C`, not `newAddr`.
7. The already-accrued USDC is now permanently stuck in `FeeVault` with no code path to release it to `C` or anyone else. [2](#0-1) [1](#0-0) [3](#0-2)

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
