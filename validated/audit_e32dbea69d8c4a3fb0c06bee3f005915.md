### Title
`FeeVault.claim()` permanently locks a creator's accrued USDC fees if their address is blacklisted by USDC - (File: `packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claim()` is the only path a token creator can use to withdraw their pooled USDC fee balance, and it always pays out to `msg.sender` with no ability to specify an alternate recipient [1](#0-0) . USDC (the fee-denominated asset accrued from every buy/sell via `Zap`) implements an issuer-controlled blacklist that makes `transfer`/`transferFrom` to a blacklisted address revert unconditionally. If a creator's address is ever added to that blacklist, their entire `creatorBalance[creator]` — which accrues over the token's whole trading lifetime — becomes permanently unclaimable, mirroring the `LM_PC_Staking_v1.unstake()` bug class where funds already deposited/accrued under an address can never be retrieved once that address is blacklisted.

### Finding Description
Fees are accrued to `creatorBalance[creator]` on every buy and sell through `Zap._accrueFee` → `FeeVault.accrue`, keyed permanently by the `creator` address recorded on `Bonding.tokenInfo(token).creator` [2](#0-1) . The only way to withdraw this balance is:

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

There is no `recipient` parameter — `usdc.safeTransfer` always targets `msg.sender`. If Circle blacklists `msg.sender` on USDC (a real, documented mechanism on the production USDC contract), this `safeTransfer` reverts every single time `claim()` is called, because `creatorBalance` is zeroed only inside the same transaction as the transfer (there is no separate "withdraw to internal ledger" and "sweep" step, unlike `sweepDonations`/`claimProtocol`, which pay a fixed, admin-rotatable `feeTo`).

`Bonding.transferCreator(tokenAddress, newCreator)` lets a creator reassign the `creator` role for a token so that *future* fee accruals route to a new address [3](#0-2) , but it does not touch the already-accumulated `creatorBalance[oldCreator]` inside `FeeVault` — that value is keyed by the old address and there is no function to move or reassign an existing balance to a different address. So any fees accrued before the blacklist event remain permanently stuck.

### Impact Explanation
The impact is a permanent freeze of creator funds, matching the "concrete... permanent freezing of trader, creator or LP funds" acceptance criterion. Multi-token creators can lose the entirety of their `lifetimeCreatorEarned` balance not yet claimed as of the blacklist event, with no recovery mechanism on-chain (the protocol owner has no `sweep`/override for `creatorBalance`; only `sweepDonations` and `setFeeTo` exist, neither of which touches `creatorBalance`).

### Likelihood Explanation
Medium likelihood: it requires the specific external condition of a creator's address being blacklisted by USDC's centralized issuer (Circle), which is out of the protocol's control but is a realistic event (sanctions, compliance actions, compromised address flagged, etc.) — the same threat class the original hats-finance report flags. Given `alt.fun`'s fee structure pays creators automatically and indefinitely via a single hardcoded recipient, any creator subject to this real-world event loses access permanently, with no workaround inside the contract.

### Recommendation
Add a `claimTo(address recipient)` variant (or a `recipient` parameter to `claim()`) that lets the caller redirect payout to an alternate, non-blacklisted address, analogous to the hats-finance recommendation for `LM_PC_Staking_v1.unstake()`. Alternatively, allow an owner-gated "rescue" path that lets a creator (or the vault owner, with creator's signed authorization) reassign an existing `creatorBalance` entry to a new address before claiming.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`, and multiple trades occur, accruing USDC to `creatorBalance[C]` in `FeeVault` via `Zap._accrueFee` → `FeeVault.accrue` [4](#0-3) .
2. USDC's issuer blacklists address `C` (e.g., due to an unrelated compliance flag).
3. `C` calls `FeeVault.claim()`. `amount = creatorBalance[C]` is read and zeroed, then `$.usdc.safeTransfer(msg.sender, amount)` is attempted [1](#0-0) ; USDC's `transfer` reverts because `to == C` is blacklisted, and the whole `claim()` transaction reverts (so `creatorBalance[C]` is correctly not lost to a mid-transaction zeroing bug, but is now permanently unclaimable since every future `claim()` call from `C` will revert the same way).
4. `C` calls `Bonding.transferCreator(token, newAddress)` to redirect *future* fees to `newAddress`, but the balance already sitting in `creatorBalance[C]` remains forever locked in `FeeVault`, since no function exists to migrate or claim an existing balance to a different address.

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

**File:** docs/contracts-scope.md (L117-121)
```markdown
- **Accrual:** `Zap` transfers the fee USDC to `FeeVault`, then calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)`. Creator attribution comes from `Bonding.tokenInfo(token).creator` (set at launch, updatable via `transferCreator`).
- **Claims:** `FeeVault.claim()` pays the caller their pooled USDC balance across every token they've launched. `FeeVault.claimProtocol()` is permissionless and pays the configured `feeTo` — anyone can trigger the payout, but funds always go to the admin-set address.
- **Lifetime counters:** `lifetimeCreatorEarned(creator)` / `lifetimeProtocolEarned` never decrement on claim, so the UI can render "total earned / claimed / claimable" consistently.
- **Router swapability:** The vault has an owner-controlled depositor allowlist. A new router is whitelisted, the old router removed, and creator balances are untouched during the transition.
- `transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution.
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
