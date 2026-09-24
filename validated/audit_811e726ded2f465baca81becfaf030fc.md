### Title
Creator fee balances become permanently frozen for a USDC-blacklisted creator, and `transferCreator` cannot rescue already-accrued funds - (File: packages/contracts/src/FeeVault.sol)

### Summary
`FeeVault.claim()` pays out the caller's entire `creatorBalance[msg.sender]` via a hardcoded `safeTransfer(msg.sender, amount)`, with no way to specify an alternate recipient [1](#0-0) . Since fees are paid in USDC, an ERC20 with real-world blacklisting functionality, a creator address that gets blacklisted by Circle after (or even before) fees accrue can never withdraw that balance. Unlike the referenced Sherlock finding, where a blacklisted collateral depositor could eventually be rescued via liquidation by another address, alt.fun has no equivalent rescue path for already-accrued creator balances.

### Finding Description
Fee attribution in `FeeVault` is keyed strictly by address: `creatorBalance[creator]` accumulates USDC via `accrue()`, called by `Zap` using `Bonding.tokenInfo(token).creator` as the creator key [2](#0-1) . The only way to retrieve that balance is `claim()`, which transfers strictly to `msg.sender`:

```solidity
function claim() external nonReentrant returns (uint256 amount) {
    amount = $.creatorBalance[msg.sender];
    ...
    $.usdc.safeTransfer(msg.sender, amount);
}
``` [1](#0-0) 

`Bonding.transferCreator(tokenAddress, newCreator)` lets a creator hand off future fee attribution for a token to a new address [3](#0-2) , but it only mutates `TokenInfo.creator` in `Bonding` for *future* `accrue()` calls. It does not, and cannot, move the USDC that is already resting in `FeeVault.creatorBalance[oldCreator]`, because that mapping is keyed by the historical creator address at accrual time, not by the current `Bonding.tokenInfo(token).creator`. If `oldCreator` is later blacklisted by USDC, the balance already sitting under that key is unreachable by any transaction: `claim()` always pays to `msg.sender`, and there is no owner or permissionless sweep of a specific creator's `creatorBalance` — `sweepDonations()` only recovers the *surplus* over `totalAccruedCreator + protocolBalance`, not backed per-creator balances [4](#0-3) .

This differs materially, and for the worse, from the audited Surge `Pool.removeCollateral` bug: in Surge, a blacklisted user's collateral could eventually be freed via liquidation by a third party (an imperfect, unfair, but existing recovery path). In alt.fun's `FeeVault`, there is no analogous recovery mechanism whatsoever — accrued creator fees under a blacklisted address are permanently and irrecoverably frozen.

### Impact Explanation
Permanent freezing of creator funds. Any creator whose receiving address becomes blacklisted by USDC (a realistic real-world scenario for a widely used stablecoin) loses all ability to claim their accrued and future-until-transfer creator fee share. Calling `transferCreator` does not help recover the funds already stuck — it only redirects new inflows. This satisfies the "permanent freezing of creator funds" bar from the validation criteria.

### Likelihood Explanation
Any creator's fee-recipient address can become blacklisted independent of any protocol action (USDC/Circle-controlled), and every launched token accrues creator fees automatically on every buy/sell via `Zap`'s 0.25% creator cut [5](#0-4) . No attacker action is required beyond the creator's own address being sanctioned/blacklisted, making this a plausible, not merely theoretical, occurrence for real launches using genuine USDC.

### Recommendation
Add a `claim(address to)` (or `claimTo`) variant, or allow the owner/creator to migrate an existing `creatorBalance` entry to a new address (e.g., a permissionless `reassignCreatorBalance(oldCreator, newCreator)` gated by a signature from `oldCreator`, or extend `transferCreator` to also move the currently accrued `FeeVault.creatorBalance` for that creator/token). At minimum, allow the creator to specify a destination address at claim time so a blacklisted EOA is not a permanent dead end for otherwise-uncontested funds.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`, and trading generates creator fees; `Zap` calls `FeeVault.accrue(token, C, creatorAmount, protocolAmount, isBuy)`, incrementing `creatorBalance[C]`.
2. Circle blacklists `C`'s address on USDC (freezes `transfer`/`transferFrom` involving `C`).
3. `C` calls `Bonding.transferCreator(token, D)` to redirect future attribution to a fresh address `D` — this only updates `Bonding.tokenInfo(token).creator`, leaving `FeeVault.creatorBalance[C]` unchanged [3](#0-2) .
4. `C` calls `FeeVault.claim()`. `amount = creatorBalance[C]` is nonzero, but `$.usdc.safeTransfer(msg.sender, amount)` reverts because USDC blocks transfers to/from a blacklisted address [1](#0-0) .
5. `D` (the new creator) cannot call `claim()` on `C`'s behalf either — `claim()` reads and clears `creatorBalance[msg.sender]` only, so `D`'s call would only affect `creatorBalance[D]`, not `creatorBalance[C]`.
6. `C`'s already-accrued balance in `creatorBalance[C]` is now permanently stuck in `FeeVault` with no owner or permissionless function capable of moving it out.

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

**File:** docs/contracts-scope.md (L116-118)
```markdown
- **Rate:** 0.75% on every buy/sell (curve **and** post-grad), split 0.5% protocol / 0.25% creator.
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
```
