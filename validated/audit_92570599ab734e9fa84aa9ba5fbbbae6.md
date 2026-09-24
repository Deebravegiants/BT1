### Title
Blacklistable USDC transfer in `FeeVault.claim()` can permanently strand a creator's accrued fee balance - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.creatorBalance[creator]` accrues USDC fees indefinitely and can only ever be paid out via `claim()`, which does a hardcoded `safeTransfer(msg.sender, amount)`. Real-world USDC is centrally blacklistable (Circle can freeze specific addresses). If a token creator's address is later blacklisted by USDC, every future call to `claim()` from that address reverts on the `safeTransfer`, permanently freezing that creator's entire pooled balance with no owner-level rescue path, mirroring the reported "SnailBrook Token blacklist + no emergency withdraw" bug class.

### Finding Description
`FeeVault.accrue` credits `creatorBalance[creator]` with every buy/sell fee split forever (never expires, never redirected) [1](#0-0) . The only exit for that balance is `claim()`, which zeroes the mapping and unconditionally transfers to `msg.sender`: [2](#0-1) 

There is no `claimTo(address recipient)` variant, no owner override, and no emergency-withdraw function anywhere in `FeeVault.sol`. Compare this with `claimProtocol()`, whose recipient (`feeTo`) is admin-rotatable via `setFeeTo` if that address becomes unusable [3](#0-2) ; the creator-side balance has no analogous admin escape hatch. `Bonding.transferCreator` only changes *future* fee attribution for a token — it does not, and cannot, move an already-accrued `creatorBalance[oldCreator]` entry inside `FeeVault`, since `FeeVault` has no concept of "current creator of token X," only a flat per-address ledger that `Zap._accrueFee` writes to using `bonding_.creatorOf(tokenAddress)` at accrual time [4](#0-3) . So once fees have been accrued to a given creator address, that specific address is the only one that can ever claim them.

If the deployed `usdc` token (set once at `initialize` and immutable thereafter) is real USDC, and a creator's address is later added to Circle's blacklist for any unrelated reason (sanctions list, KYC/AML flag, compromised-address freeze, etc.), `IERC20(usdc).transfer(creator, amount)` inside `claim()` will revert forever for that address. The creator's balance is permanently locked in the vault: they cannot call `claim()` (their address is frozen), they cannot ask the owner to redirect it (no such function exists), and `sweepDonations()` only recovers *unbacked* surplus, not backed/accrued balances — it explicitly excludes `totalAccruedCreator` from what it sweeps [5](#0-4) .

### Impact Explanation
This is a permanent freezing-of-funds bug matching the required impact class: legitimate, protocol-earned creator fee revenue becomes unrecoverable and stuck inside `FeeVault` indefinitely, with no owner/multisig rescue mechanism to redirect it to a working address. Unlike a trader who can simply move a launched `Token` balance to a fresh wallet before selling, a creator's *already-accrued FeeVault balance* is bound to a fixed address key in a mapping — there is no way to reassign historical balances to a new claim address, even by the owner.

### Likelihood Explanation
Likelihood is a function of how likely a given creator address becomes blacklisted by the base asset used for fees — moderate/low in general but non-zero over the lifetime of a widely-used permissionless launch platform (any address can become a token creator, and centralized stablecoin issuers have blacklisted addresses in the past for sanctions/exploit reasons). This exactly parallels the acknowledged report's likelihood reasoning (medium severity, accepted as a real but not-everyday risk), and the fix (owner-controlled emergency/rescue path, or a `claimTo`/redirect mechanism) is the same class of remediation recommended in the original report.

### Recommendation
Add an owner-gated (ideally multisig + timelock, per the original report's guidance) rescue function on `FeeVault`, e.g. `emergencyWithdrawCreatorBalance(address creator, address to)` that zeroes `creatorBalance[creator]` and transfers to an owner-specified `to`, decrementing `totalAccruedCreator` symmetrically with `claim()`. Alternatively, add a `claimTo(address to)` entry point so an affected creator (before being blacklisted, or via an owner-assisted flow) can redirect payouts to a working address. Emit an event for transparency, and ensure the underfund invariant (`usdc.balanceOf(this) >= totalAccruedCreator + protocolBalance`) is preserved by any such rescue path.

### Proof of Concept
1. Owner deploys `FeeVault` with real USDC as `usdc_`.
2. `Zap` accrues fees over time via `_accrueFee` → `FeeVault.accrue(token, creator, creatorShare, protocolShare, isBuy)`, growing `creatorBalance[creator]` to a large sum (see `accrue`, [1](#0-0) ).
3. `creator`'s address is later added to Circle's USDC blacklist (external event, out of protocol's control).
4. `creator` calls `FeeVault.claim()`. `amount = creatorBalance[creator]` is read and the mapping zeroed defensively before transfer, but `$.usdc.safeTransfer(msg.sender, amount)` reverts because USDC's `transfer` reverts for a blacklisted recipient — the whole transaction (including the balance-zeroing) reverts, so the balance nominally remains at `amount`, but is now permanently unclaimable by this address.
5. `Bonding.transferCreator(tokenAddress, newCreator)` can be called to redirect **future** fee attribution for that token to `newCreator`, but the historical `creatorBalance[oldCreator]` entry in `FeeVault` is untouched and unreachable by anyone — not `newCreator`, not the owner, not `oldCreator`.
6. No function in `FeeVault.sol` (`claim`, `claimProtocol`, `sweepDonations`, `addDepositor`, `removeDepositor`, `setFeeTo`) can move `creatorBalance[oldCreator]` to any other address. The funds are permanently frozen.

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

**File:** packages/contracts/src/FeeVault.sol (L151-160)
```text
    function sweepDonations() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        uint256 backed = $.totalAccruedCreator + $.protocolBalance;
        uint256 balance = $.usdc.balanceOf(address(this));
        if (balance <= backed) revert NothingToClaim();
        amount = balance - backed;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit DonationsSwept(feeTo_, amount);
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
