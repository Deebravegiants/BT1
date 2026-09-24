Based on my investigation, `FeeVault.sol` has no admin rescue or balance-reassignment path for `creatorBalance` — the only exit is `claim()`, which is hardcoded to pay `msg.sender`.This confirms the analog. I have sufficient evidence to finalize the answer.

### Title
FeeVault.claim() cannot send creator fee payouts to an alternate recipient, permanently freezing accrued USDC for a USDC-blocklisted creator - (File: packages/contracts/src/FeeVault.sol)

### Summary
`FeeVault.claim()` is the sole withdrawal path for a token creator's accrued fee balance and it unconditionally transfers to `msg.sender`, with no `_receiver` parameter. Since the vault's asset is USDC — a token with an admin-controlled blocklist — a creator who is (or becomes) blocklisted by Circle can never retrieve their `creatorBalance`, and there is no other function in the protocol capable of redirecting or reassigning an already-accrued balance to a fresh address.

### Finding Description
`claim()` reads `$.creatorBalance[msg.sender]`, zeroes it, decrements `totalAccruedCreator`, and calls `$.usdc.safeTransfer(msg.sender, amount)` [1](#0-0)  — there is no parameter to specify a different recipient. `Bonding.transferCreator(tokenAddress, newCreator)` only updates `TokenInfo.creator` for **future** fee attribution on that specific token going forward [2](#0-1) ; it does not, and cannot, move the `creatorBalance[msg.sender]` mapping entry already accrued in `FeeVault`, because that balance is keyed globally by creator address across every token they've launched, not per-token [3](#0-2) . There is no owner-side rescue, sweep, or reassignment function for `creatorBalance` in `FeeVault.sol` — only `claim()`, `claimProtocol()`, and `sweepDonations()` move USDC out, and none of them accept an arbitrary recipient tied to a creator's stuck balance.

`FeeAccrued`/`accrue()` continuously grows `creatorBalance[creator]` on every buy/sell of every token that creator launched [4](#0-3) , so once a creator address is blocklisted by USDC, all subsequent accrual for that creator (across all their tokens, past and future trades) becomes permanently unclaimable — `claim()` will always revert because the internal `IERC20.transfer` call reverts for a blocklisted `to` address, and `nonReentrant`/`onlyDepositor` gates offer no bypass.

This is the direct analog of the referenced Sherlock finding: `MainVault.withdrawAllowance` lacked a `_receiver` parameter, so a blocked user's `vaultCurrency` (USDC/USDT) withdrawal reverted permanently. `FeeVault.claim()` has the identical shape — hardcoded `msg.sender` recipient, no override — against the same class of blockable stablecoin (USDC).

### Impact Explanation
A blocklisted creator's entire accrued `creatorBalance` — which by design pools fees across every token that creator has ever launched — becomes permanently frozen inside `FeeVault` with no recovery path. This is not merely inconvenient; there is no on-chain mechanism (owner-only or otherwise) to move the already-accrued balance to a new address once blocklisted, meeting the "permanent freezing of creator funds" bar.

### Likelihood Explanation
USDC (and other centralized stablecoins used as `vaultCurrency`/reserve fee asset) actively maintains an address blocklist and has frozen addresses in the past for OFAC compliance, exploit response, and law-enforcement requests. Any creator who is added to this list — for reasons entirely unrelated to alt.fun — loses access to legitimately earned fees with no interaction from alt.fun required to trigger the freeze; it happens purely from the reserve asset's own admin action.

### Recommendation
Add a `_receiver` parameter to `FeeVault.claim()` (and consider the same for `claimProtocol()`/`sweepDonations()` recipients where relevant), allowing the caller to direct payout to an address of their choosing while still gating the balance lookup/zeroing on `msg.sender`:
```solidity
function claim(address receiver) external nonReentrant returns (uint256 amount) {
    FeeVaultStorage storage $ = _s();
    amount = $.creatorBalance[msg.sender];
    if (amount == 0) revert NothingToClaim();
    $.creatorBalance[msg.sender] = 0;
    $.totalAccruedCreator -= amount;
    $.usdc.safeTransfer(receiver, amount);
    emit CreatorFeesClaimed(msg.sender, amount);
}
```

### Proof of Concept
1. Creator launches multiple tokens via `Zap.createToken`; each buy/sell accrues fees to `FeeVault.creatorBalance[creator]` via `Zap._accrueFee` → `FeeVault.accrue` [5](#0-4) .
2. Circle blocklists the creator's address in USDC (unrelated to alt.fun activity).
3. Creator calls `FeeVault.claim()`; `$.usdc.safeTransfer(msg.sender, amount)` reverts because `msg.sender` is blocklisted [1](#0-0) .
4. Creator calls `Bonding.transferCreator(tokenAddress, newAddress)` for each of their tokens to redirect **future** fees, but the already-accrued `creatorBalance[creator]` in `FeeVault` remains under the blocked address and is unreachable, permanently.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L31-45)
```text
    struct FeeVaultStorage {
        IERC20 usdc;
        /// @notice Protocol fee recipient. Receives `claimProtocol()` payout.
        address feeTo;
        EnumerableSet.AddressSet depositors;
        mapping(address creator => uint256) creatorBalance;
        uint256 protocolBalance;
        /// @notice Lifetime gross creator USDC accrued (never decreases).
        mapping(address creator => uint256) lifetimeCreatorEarned;
        uint256 lifetimeProtocolEarned;
        /// @notice Running sum of unclaimed creator balances. Lets `accrue`
        ///         do its underfund check in O(1) without iterating the
        ///         creator mapping.
        uint256 totalAccruedCreator;
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
