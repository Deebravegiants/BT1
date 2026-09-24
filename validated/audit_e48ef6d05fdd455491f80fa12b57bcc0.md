## Finding [1](#0-0) , [2](#0-1)  confirm the analog exists: `FeeVault.creatorBalance` is a mapping keyed strictly by `creator` address, and the only exit path — `claim()` — always sends the accrued USDC to `msg.sender`, with no way for anyone (including the vault owner) to redirect an already-accrued balance to a different address.

### Title
Blacklisted creator address permanently freezes accrued creator fees in FeeVault - (`packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.accrue()` credits creator fees into `creatorBalance[creator]`, keyed by the `creator` address stored on `Bonding.TokenInfo` at token-launch time. The only way to withdraw this balance is `FeeVault.claim()`, which unconditionally transfers to `msg.sender`. Since alt.fun's fee token is USDC — a blacklistable ERC20 — if a creator's own address is ever added to USDC's blacklist, that creator can never successfully call `claim()` for their own accrued balance, because `usdc.safeTransfer(msg.sender, amount)` will revert on the underlying blacklisted-transfer check.

### Finding Description
`FeeVault.claim()` reads `$.creatorBalance[msg.sender]`, zeroes it, decrements `totalAccruedCreator`, and calls `$.usdc.safeTransfer(msg.sender, amount)`: [1](#0-0) 

Because Solidity reverts roll back all state changes within the same call, a reverting transfer (e.g., USDC blocking a transfer to/from a blacklisted address) leaves `creatorBalance[creator]` intact but permanently unreachable — `msg.sender` in `claim()` is hard-coded to equal the mapping key, so no other address can ever claim on behalf of the blacklisted creator, and there is no admin/rescue/`claimFor` function anywhere in `FeeVault.sol` or `Bonding.sol` to redirect it.

Critically, `Bonding.transferCreator()` does **not** help here: [3](#0-2) 
This only updates `Bonding.TokenInfo.creator` for *future* fee attribution inside `Zap`'s accrual calls — it has zero effect on the USDC balance already sitting in `FeeVault.creatorBalance[oldCreator]`, which remains permanently keyed to the old, now-blacklisted address.

### Impact Explanation
Any USDC amount a creator has accrued in `FeeVault` at the moment their address becomes blacklisted by USDC's issuer is permanently frozen in the contract with no recovery path — matching the "permanent freezing of creator funds" criterion. This is entirely reachable by ordinary, unprivileged activity: any trader's buys/sells on that creator's token accrue fees via `Zap`'s calls to `FeeVault.accrue` [2](#0-1) , building up a `creatorBalance` that the creator cannot later retrieve.

### Likelihood Explanation
USDC blacklisting an address is an external, real-world event outside the protocol's control (used precisely as the archetype scenario in the referenced report), but it is a realistic condition for any creator address over the life of a launched token, and requires no protocol bug or privileged action to trigger the freeze — only the passive combination of "creator already has an unclaimed balance" + "creator's address gets blacklisted."

### Recommendation
Decouple the claim destination from `msg.sender`: allow the creator (or an owner-gated rescue path) to designate an alternate payout address for their already-accrued `creatorBalance`, e.g., a `claimTo(address to)` function gated to `msg.sender == creator`, or let `Bonding.transferCreator` also migrate/merge the corresponding `FeeVault.creatorBalance` entry to the new creator address.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`; multiple traders buy/sell, accruing USDC into `FeeVault.creatorBalance[C]` via `accrue()`.
2. USDC issuer blacklists address `C` (real-world event).
3. `C` calls `FeeVault.claim()`; `usdc.safeTransfer(C, amount)` reverts due to the blacklist, and the whole call reverts — `creatorBalance[C]` is preserved but forever unclaimable since `claim()` always targets `msg.sender == C`.
4. `C` calls `Bonding.transferCreator(token, newAddress)` — this changes only *future* accrual attribution; the existing `creatorBalance[C]` in `FeeVault` is untouched and still requires `msg.sender == C` to claim, which will always fail.

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
