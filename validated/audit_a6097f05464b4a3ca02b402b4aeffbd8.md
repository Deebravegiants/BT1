### Title
Direct ERC-20 donation to `StreamingYieldVault` bypasses the vesting guard, enabling a donation-sandwich share dilution attack - (File: `sdk/packages/core/contracts/vaults/StreamingYieldVault.sol`)

### Summary
`StreamingYieldVault` streams yield linearly to defend against "yield sniping," but that protection is scoped to the `addYield()` / `onTransferReceived()` accounting path only. `totalAssets()` is computed as `balanceOf(this) - _lockedYield()`, where `_lockedYield()` is derived purely from the internally tracked `_vestingAmount`/`_vestingStart` state. A plain ERC-20 `transfer()` of the underlying asset directly to the vault address is never routed through `addYield`/`onTransferReceived`, so it is not tracked as locked/vesting — it instantly and fully counts toward `totalAssets()`, immediately repricing shares for whoever holds them at that moment. This is the exact "donation" primitive from the Arcadia `donateToTranche` finding: any unaccounted, instantaneous top-up to a share-priced pool can be front-run with a deposit and back-run with a withdrawal/redeem.

### Finding Description
`totalAssets()` at [1](#0-0)  is defined as the raw asset balance of the contract minus the not-yet-vested portion of the *tracked* tranche. The only path that marks incoming assets as "locked/vesting" is `_startVesting`, reached via the owner-gated `addYield` at [2](#0-1)  or the owner-gated ERC-1363 `onTransferReceived` hook at [3](#0-2) , both of which require `from == owner()`.

However, the underlying asset can also receive value via a bare ERC-20 `transfer(vault, amount)` call from *any* address (attacker, integrator, keeper mis-wiring, MEV bot, or even the owner sending funds the "wrong way" instead of through `addYield`). A plain `transfer` never invokes `onTransferReceived` and is not gated by `onlyOwner`. Because `_lockedYield()` only "hides" the `_vestingAmount` set by `_startVesting`, any balance increase that didn't go through that function is immediately visible in `totalAssets()` — with no vesting window, no `MIN_WINDOW`, and no deposit-lock protection at all.

Deposits/mints are only blocked while `_isVesting()` is true (i.e., while a *tracked* tranche is streaming), per `maxDeposit`/`maxMint` at [4](#0-3) . Outside of a tracked vesting window (which is most of the time, and always right after `vestedAt()` until the next `addYield`), deposits are wide open (`maxDeposit` returns `type(uint256).max`), and redemptions/withdrawals are unconditionally open per the contract's own documentation. This gives an attacker exactly the sandwich window the Arcadia report describes.

### Impact Explanation
An attacker monitoring the mempool who sees any raw, untracked asset transfer landing on the vault (or who can induce/trigger one, e.g. a misconfigured sweep/reward-distribution bot, a partner contract routing funds the "wrong way", or simply a benign top-up sent via `transfer` instead of `addYield`) can:
1. Front-run with a large `deposit()`/`mint()` while deposits are open (share price still reflects the pre-donation balance).
2. Let the untracked transfer land, instantly and fully repricing shares (no vesting delay applies).
3. Back-run with `redeem()`/`withdraw()` of their full position, capturing a share of the donation proportional to their now-inflated share of `totalSupply()`, diluting the intended recipients (existing LPs) of that value — precisely the "Dilution of Donations" impact from the referenced report, and worse here because it fully bypasses the contract's own anti-sniping design rather than merely evading a soft mitigation.

This is a concrete, unprivileged loss-of-funds vector for legitimate LPs whenever value reaches the vault outside the `addYield` path, and it defeats the security property the contract's NatSpec explicitly claims to provide ("no single block can be sandwiched around a yield event").

### Likelihood Explanation
Likelihood is Medium: it requires (a) some transfer of the underlying asset landing on the vault address without going through `addYield`, and (b) an attacker positioned to sandwich it. Because `StreamingYieldVault` is a generic, reusable primitive shipped in the SDK (`sdk/packages/core/contracts/vaults/`) for arbitrary integrators/owners, the probability of a misrouted transfer (wrong function called, a script using `transfer` instead of `approve`+`addYield`, a paymaster/treasury sweep, or an attacker directly self-funding the donation to profit off other LPs' locked capital) is realistic over the vault's lifetime, and deposits/withdrawals being open outside the tracked vesting window means the sandwich window exists by design every cycle.

### Recommendation
Track internally accounted assets rather than relying on `balanceOf(this)`. Maintain a separate `_totalDeposited`/`_principal` accumulator updated only by `deposit`/`mint`/`withdraw`/`redeem`/`addYield`, and compute `totalAssets()` from that internal accounting (subtracting `_lockedYield()`), ignoring any surplus raw balance from untracked transfers — or, if untracked surplus must be recognized, route it through the same vesting mechanism (e.g., sweep any balance in excess of `_totalDeposited + _vestingAmount` into a **new** tranche via `_startVesting` instead of recognizing it instantly).

### Proof of Concept
1. Owner deploys `StreamingYieldVault` and seeds it normally; the vault is out of its vesting window (`maxDeposit` unbounded).
2. Attacker calls `deposit(largeAmount, attacker)`, receiving shares at the current fair exchange rate.
3. Any account (attacker, a misrouted bot, or a naive integrator) calls `IERC20(asset).transfer(vault, donationAmount)` directly — this never touches `onTransferReceived`/`addYield`/`_startVesting`.
4. `totalAssets()` at [1](#0-0)  immediately reflects `balanceOf(this) + donationAmount` with `_lockedYield()` unchanged (still governed by the unrelated `_vestingAmount`), instantly repricing all outstanding shares upward.
5. Attacker calls `redeem(attackerShares, attacker, attacker)` in the same or next block, withdrawing `largeAmount` plus a proportional slice of `donationAmount` — capital that would otherwise have accrued to whoever held shares before step 2, exactly mirroring the Arcadia `donateToTranche` sandwich.

### Citations

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L94-96)
```text
    function totalAssets() public view override returns (uint256) {
        return IERC20(asset()).balanceOf(address(this)) - _lockedYield();
    }
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L127-139)
```text
    /// @inheritdoc ERC4626
    /// @dev Zero while a tranche is vesting so deposits are closed (and integrators can detect it);
    ///      unbounded otherwise. This is the single lock that keeps new capital from joining
    ///      mid-tranche: `deposit` reverts at its `maxDeposit` check with `ERC4626ExceededMaxDeposit`.
    function maxDeposit(address) public view override returns (uint256) {
        return _isVesting() ? 0 : type(uint256).max;
    }

    /// @inheritdoc ERC4626
    /// @dev Zero while a tranche is vesting so integrators see mints are closed; unbounded otherwise.
    function maxMint(address) public view override returns (uint256) {
        return _isVesting() ? 0 : type(uint256).max;
    }
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L150-161)
```text
    function onTransferReceived(address, address from, uint256 value, bytes calldata)
        external
        override
        returns (bytes4)
    {
        if (msg.sender != asset()) revert CallerNotAsset(msg.sender);
        if (from != owner()) revert OwnableUnauthorizedAccount(from);

        _startVesting(value);

        return IERC1363Receiver.onTransferReceived.selector;
    }
```

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L176-183)
```text
    function addYield(uint256 amount) external onlyOwner {
        // Pull the funds first so `balanceOf` already reflects `amount` before it is marked
        // locked; otherwise `totalAssets` would transiently underflow when a tranche exceeds
        // the current backing (e.g. the very first `addYield` on a near-empty vault).
        IERC20(asset()).safeTransferFrom(msg.sender, address(this), amount);

        _startVesting(amount);
    }
```
