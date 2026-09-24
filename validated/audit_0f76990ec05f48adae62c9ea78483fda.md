This confirms the analog: `Zap._accrueFee` passes `bonding_.creatorOf(tokenAddress)` (the *current* `info.creator`) into `FeeVault.accrue`, which credits `creatorBalance[creator]` keyed by that address [1](#0-0) . `FeeVault.claim()` always pays out to `msg.sender` from `creatorBalance[msg.sender]` [2](#0-1) , and `Bonding.transferCreator` only rewrites `info.creator` for *future* fee attribution — it never touches or migrates the existing `FeeVault.creatorBalance` mapping entry for the old address [3](#0-2) .

### Title
Creator fees permanently frozen in FeeVault if the accrued creator address is blocked by USDC before it claims - ([File: packages/contracts/src/FeeVault.sol, packages/contracts/src/Bonding.sol])

### Summary
`FeeVault` pools creator USDC fees under the creator's address at the time each fee was accrued and pays out only via `claim()`, which unconditionally `safeTransfer`s to `msg.sender`. If that address is ever blocked from receiving USDC (e.g., blacklisted by USDC's admin-controlled blocklist), the balance already sitting under that address becomes permanently unclaimable, and `Bonding.transferCreator` — the only user-facing mechanism to redirect fee flow — does not migrate the stuck balance, only future accrual attribution.

### Finding Description
Every buy/sell fee is split and forwarded to `FeeVault` via `Zap._accrueFee(token, creator, creatorShare, protocolShare, isBuy)`, where `creator` is read live from `Bonding.creatorOf(tokenAddress)` at the moment of the trade [1](#0-0) . `FeeVault.accrue` credits `$.creatorBalance[creator] += creatorAmount`, keyed strictly by that address [4](#0-3) .

The only way to claim this balance is `FeeVault.claim()`, which reads `$.creatorBalance[msg.sender]` and transfers directly to `msg.sender` — there is no parameter to redirect the payout to a different address [2](#0-1) .

`Bonding.transferCreator(tokenAddress, newCreator)` lets the current creator hand off the role at any time (no lifecycle/window restriction, unlike the referenced Gitcoin RFP/QV/Donation strategies where the recipient-change window closes) [3](#0-2) . However, this function only updates `info.creator` on `Bonding`, which changes *future* fee attribution in subsequent `_accrueFee` calls. It performs no call into `FeeVault` and never moves the existing `creatorBalance[oldCreator]` balance to `newCreator`.

Consequently: if a creator's address is added to USDC's blocklist (a documented capability of centralized stablecoins like USDC) at any point after fees have accrued to it, that specific `creatorBalance[oldCreator]` amount is stuck forever. The creator can call `transferCreator` to protect all *future* fees, but the already-accrued balance remains keyed to the blocked address and can never be extracted, since `claim()` always pays `msg.sender` and there is no admin or creator-driven path to reassign or sweep a specific creator's stuck balance to another address.

### Impact Explanation
This is a permanent freezing of creator funds — a Medium/High-severity outcome per the standard "permanent freezing of trader/creator/LP funds" criterion. Any creator whose wallet is later blocked by USDC (regulatory action, compliance flag, sanctions list, etc.) irrecoverably loses all fees accrued under that address before the block took effect, with no on-chain remediation available to the creator, the protocol owner, or anyone else — `FeeVault` has no admin function analogous to `setFeeTo` for creator balances.

### Likelihood Explanation
USDC (the fee-denominated asset referenced throughout `Zap`/`FeeVault`) is a centralized stablecoin with an active, exercised blocklist feature. Any creator can plausibly be blocklisted independent of protocol behavior (e.g., due to unrelated on-chain activity, sanctions exposure, or compliance action), making this reachable without any attacker action — it is a standing risk inherent to using USDC as the fee-claim asset, matching exactly the bug class in the reference report ("recipient's address blocked by token").

### Recommendation
Add a creator-authorized "claim to" or balance-migration path in `FeeVault`, e.g.:
- Extend `claim()` (or add `claimTo(address to)`) restricted to the caller's own accrued balance but allowing an alternate destination address, or
- Have `Bonding.transferCreator` (or a new `FeeVault.migrateBalance(oldCreator, newCreator)` callable only by `oldCreator`) move `creatorBalance[oldCreator]` into `creatorBalance[newCreator]` atomically with the role transfer, so a creator anticipating or reacting to an address block can consolidate funds under a claimable address before/after the block takes effect.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`, then real buyers trade via `Zap.buy`/`Zap.sell`; each trade calls `_accrueFee(token, C, creatorShare, protocolShare, isBuy)` → `FeeVault.accrue` credits `creatorBalance[C] += creatorShare` [1](#0-0) .
2. USDC's issuer blocklists address `C` (out-of-band, independent of the protocol).
3. `C` calls `Bonding.transferCreator(token, D)` to protect future fees — `info.creator` becomes `D`, but `FeeVault.creatorBalance[C]` is untouched [3](#0-2) .
4. `C` (or anyone on `C`'s behalf) calls `FeeVault.claim()` from `C`: `$.usdc.safeTransfer(C, amount)` reverts because USDC's blocklist rejects transfers to `C` [2](#0-1) .
5. `D` cannot claim `C`'s pre-transfer balance either, since `claim()` only reads `creatorBalance[msg.sender]`. The funds are permanently locked in `FeeVault`.

### Citations

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
