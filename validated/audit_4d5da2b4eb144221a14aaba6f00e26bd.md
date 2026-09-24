Based on the codebase, there is a valid analog. `FeeVault.claim()` pays out an internal balance mapping keyed by `address`, with no way to redirect an already-accrued balance to a different address if that address becomes untransferable (e.g., blocklisted by USDC).

### Title
Creator fee balances in `FeeVault` are permanently stranded if the creator address becomes USDC-blocklisted, with no rescue or reassignment path - (File: `packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claim()` transfers a creator's entire pooled USDC balance to `msg.sender` in a single `safeTransfer` call. [1](#0-0)  The recipient of that transfer is hard-coded to `msg.sender` — there is no `claimTo(address)` variant and no owner-level override to reassign a stranded balance. `Bonding.transferCreator` only rewires the `creator` field used by *future* fee accruals; it never touches the FeeVault's already-accrued `creatorBalance[oldCreator]` mapping. [2](#0-1)  If the specific creator address that accrued the balance becomes blocklisted (e.g., Circle-blocklisted USDC address), the balance is permanently unrecoverable — unlike a trader's `Zap.sell`, where the underlying launched Token remains a freely transferable ERC20 the user can move to another wallet before selling.

### Finding Description
All protocol/creator fees are USDC held by `FeeVault`, credited via `accrue()` and paid out via `claim()`/`claimProtocol()`. [3](#0-2)  The storage tracks balance strictly by `address creator`:
```solidity
mapping(address creator => uint256) creatorBalance;
``` [4](#0-3) 

`claim()` is the *only* exit path for that balance, and it always pays `msg.sender`:
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

If USDC blocklists `msg.sender` (the creator address), `safeTransfer` reverts and `claim()` can never succeed for that address. There is no owner-level function in `FeeVault` (`addDepositor`, `removeDepositor`, `setFeeTo`, `sweepDonations`) that can move or redirect a specific creator's `creatorBalance`. [5](#0-4)  `Bonding.transferCreator` is the only creator-identity mechanism in the protocol, but it only updates `info.creator` for *future* `_accrueFee` calls in `Zap`; the FeeVault balance already accrued to the old address is untouched:
```solidity
function transferCreator(address tokenAddress, address newCreator) external {
    if (newCreator == address(0)) revert ZeroAddress();
    TokenInfo storage info = _s().tokenInfo[tokenAddress];
    if (msg.sender != info.creator) revert NotCreator();
    if (newCreator == info.creator) revert InvalidInput();
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
``` [2](#0-1) 

Note also that `transferCreator` can itself never be called by the blocklisted creator to "escape" the situation for a *future* balance change either — the underlying stuck `creatorBalance[oldCreator]` mapping is orthogonal to `info.creator` and has no code path pointing back to it.

This differs from the trader-side `Zap._sellInternal`, where a blocklisted trader's sell reverts atomically (tokens are pulled and USDC paid in the same tx, so a revert unwinds both legs) and the trader retains their freely-transferable ERC20 Token to sell from a different, non-blocklisted wallet. [6](#0-5)  For `FeeVault`, the "funds" are an internal ledger entry with no equivalent transferable representation — once accrued to an address, that specific address is the only key that can ever unlock it.

### Impact Explanation
Any creator whose address is later blocklisted by USDC permanently loses access to all currently and future accrued `creatorBalance` for every token they've launched, with no recovery mechanism anywhere in `FeeVault` or `Bonding`. This is a permanent freeze of creator funds meeting the High bar (concrete, unrecoverable loss of legitimate protocol funds), analogous to the original report's blocklisted-`claim`-recipient freeze.

### Likelihood Explanation
Requires the creator's specific address to be blocklisted by Circle (USDC issuer) — outside the protocol's control, matching the same trust assumption the original Sherlock report relied on. Given USDC blocklisting does happen for sanctioned/compromised addresses in practice, and creators are ordinary EOAs that could be compromised or sanctioned, this is a realistic, non-hypothetical scenario, though it is not attacker-triggerable on demand (same caveat applies to the original finding).

### Recommendation
Add a pull-based or redirectable claim path decoupled from `msg.sender`, e.g.:
- Allow the current `info.creator` (post `transferCreator`) to also sweep any residual `creatorBalance[oldCreator]` still held under a prior creator address for tokens they now control, or
- Add an owner-gated (or creator-signed) `claimTo(address recipient)` / `reassignBalance(address from, address to)` function in `FeeVault` so a blocklisted creator (or the protocol, on their behalf) can redirect stranded USDC to a non-blocklisted address.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`, accrues `creatorBalance[C]` in `FeeVault` through ordinary `buy`/`sell` fee flow (`Zap._accrueFee` → `FeeVault.accrue`).
2. Circle blocklists address `C` in USDC (independent centralized event).
3. `C` calls `FeeVault.claim()`; `$.usdc.safeTransfer(msg.sender, amount)` reverts because `C` is blocklisted. [7](#0-6) 
4. `C` calls `Bonding.transferCreator(tokenAddress, newAddress)` to redirect future fees — this only updates `info.creator`, not `FeeVault.creatorBalance[C]`. [8](#0-7) 
5. `creatorBalance[C]` remains permanently non-zero and unclaimable; no function in `FeeVault` can move it to `newAddress` or any other recipient.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L36-36)
```text
        mapping(address creator => uint256) creatorBalance;
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

**File:** packages/contracts/src/FeeVault.sol (L151-193)
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

    // ─── Admin ───────────────────────────────────────────────────────────

    function addDepositor(
        address depositor
    ) external onlyOwner {
        if (depositor == address(0)) revert ZeroAddress();
        if (!_s().depositors.add(depositor)) revert DepositorAlreadyAdded();
        emit DepositorAdded(depositor);
    }

    function removeDepositor(
        address depositor
    ) external onlyOwner {
        if (!_s().depositors.remove(depositor)) revert DepositorNotFound();
        emit DepositorRemoved(depositor);
    }

    /// @notice Set the protocol fee recipient.
    /// @dev Protocol fees are pooled and paid to whoever is `feeTo` at claim
    ///      time, so rotating here redirects the entire outstanding
    ///      `protocolBalance` — and any sweepable donations — to `feeTo_`. Call
    ///      `claimProtocol()` (and `sweepDonations()`) first to settle the
    ///      pending balance to the current recipient before rotating.
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

**File:** packages/contracts/src/Zap.sol (L438-462)
```text
        IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), tokenAmount);

        uint256 ltReceived = bonding_.isGraduated(tokenAddress)
            ? _sellOnUniswapV2(tokenAddress, lt, tokenAmount)
            : _sellOnCurve(tokenAddress, tokenAmount);

        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();

        // Intentional v1 tradeoff: sells only use BounceTech's atomic
        // `redeem()` path (no `prepareRedeem` fallback/queue in Zap). If the
        // LT idle-USDC buffer is temporarily depleted, `redeem` reverts and
        // users must retry in smaller chunks after buffer replenishment.
        // Redeem into this zap (not the user) so we can deduct the fee.
        uint256 grossUsdc = IBounceLeveragedToken(lt).redeem(address(this), ltReceived, 0);

        // Symmetric with `_executeBuy`: fee charged on EVERY sell — curve
        // AND post-graduation. The `isGraduated` branch above selects the
        // venue, not the fee policy. See `_executeBuy` for the rationale.
        uint256 fee = Math.mulDiv(grossUsdc, $.sellFeeBps, BPS_DENOM, Math.Rounding.Ceil);
        usdcOut = grossUsdc - fee;

        if (usdcOut < minUsdcOut) revert SlippageExceeded();

        $.usdc.safeTransfer(msg.sender, usdcOut);
```
