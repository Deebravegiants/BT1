## Title
Blacklisted creator address permanently loses accrued protocol fees in FeeVault - (File: `packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claim()` always pays a creator's accrued balance to `msg.sender`, and that balance is permanently keyed to whatever address was the token's `creator` at the time each buy/sell fee was accrued. There is no admin or user-controlled path to reassign an already-accrued `creatorBalance` to a different address. If USDC (Circle) or a future stablecoin reserve asset places that creator's address on its blacklist, `claim()`'s internal `$.usdc.safeTransfer(msg.sender, amount)` reverts unconditionally and forever, permanently freezing that creator's earned fees inside the vault with no recovery mechanism — the same root-cause pattern as the referenced Teller `repayLoanFull()` issue, where an unconditional transfer to a blacklistable, non-substitutable address bricks the only withdrawal path.

### Finding Description
Every buy/sell routed through `Zap` accrues creator fees into `FeeVault` keyed by the token's *current* creator address at trade time: [1](#0-0) 

`FeeVault.accrue` stores the amount under `creatorBalance[creator]`: [2](#0-1) 

The only way to retrieve that balance is `claim()`, which transfers strictly to `msg.sender` — i.e., the address the balance is keyed under — with no alternate recipient parameter and no admin override: [3](#0-2) 

Contrast this with `claimProtocol()`, which pays out to the *mutable* `feeTo` address that the owner can rotate via `setFeeTo` if it ever becomes unusable: [4](#0-3) [5](#0-4) 

No equivalent remediation exists for `creatorBalance`. `Bonding.transferCreator` only changes the *forward-looking* creator recorded on the token (used by `Zap._accrueFee` for *future* accruals via `bonding_.creatorOf(tokenAddress)`); it does not, and cannot, move funds already sitting in `FeeVault.creatorBalance[oldCreator]`: [6](#0-5) 

If the creator address is ever placed on the USDC blacklist (e.g., sanctions, compromised address flagged by Circle, or any future reserve stablecoin with a blacklist feature), every subsequent `claim()` call from that address reverts inside `SafeERC20`'s underlying `transfer`, and the balance can never be extracted — by the creator, by the protocol owner, or by anyone else. `transferCreator` cannot help retroactively because it only redirects new accruals, leaving the already-accrued `creatorBalance[blacklistedCreator]` stranded, still counted in `totalAccruedCreator`, permanently occupying vault liquidity.

### Impact Explanation
This is a permanent freezing of creator funds inside `FeeVault` — funds that were legitimately earned via `Zap.buy`/`Zap.sell` fee accrual become unrecoverable the moment the associated address is blacklisted, with no owner-level or protocol-level rescue path, unlike the mutable `feeTo` protocol-fee recipient. This satisfies the "permanent freezing of ... creator ... funds" impact class.

### Likelihood Explanation
Reachable by any unprivileged trader/creator flow: a creator merely needs to launch a token via `Zap.createToken`, accrue fees through normal trading (any `Zap.buy`/`Zap.sell` on their token triggers `_accrueFee`), and then be added to the USDC blacklist — an event entirely outside the protocol's control that Circle has exercised historically. No attacker action against the protocol is even required; the bug is purely a missing remediation path.

### Recommendation
Add either:
1. An owner-controlled (or creator-signed) function to reassign an address's `creatorBalance` to a new address, mirroring `setFeeTo`'s mutability for the protocol share, or
2. A `claimTo(address to)` variant that lets the caller specify a receiving address other than `msg.sender`, while still authenticating via the caller's own balance mapping key.

### Proof of Concept
1. Creator `C` launches `TokenX` via `Zap.createToken`, becoming `Bonding.tokenInfo[TokenX].creator`.
2. Traders execute several `Zap.buy(TokenX, ...)` / `Zap.sell(TokenX, ...)` calls; each call routes through `_accrueFee` → `FeeVault.accrue(TokenX, C, creatorShare, protocolShare, isBuy)`, incrementing `creatorBalance[C]`.
3. Circle blacklists address `C` on USDC (independent real-world event).
4. `C` calls `FeeVault.claim()`. `amount = creatorBalance[C] > 0` so the zero-balance guard passes, `creatorBalance[C]` is zeroed, then `$.usdc.safeTransfer(C, amount)` reverts because `C` is blacklisted — the whole transaction reverts (state changes rolled back), so `C` permanently cannot withdraw.
5. `C` calls `Bonding.transferCreator(TokenX, newAddress)` to try to route future fees elsewhere — this succeeds for new trades, but the pre-existing `creatorBalance[C]` in `FeeVault` remains keyed to blacklisted `C` and is unreachable through any function in `FeeVault` or `Bonding`, forever.

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

**File:** packages/contracts/src/FeeVault.sol (L185-193)
```text
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
