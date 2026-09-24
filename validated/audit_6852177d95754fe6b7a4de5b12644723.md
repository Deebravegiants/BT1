### Title
Blacklisted creator can permanently lose accrued fees in `FeeVault.claim()` with no alternate-recipient escape hatch - (File: packages/contracts/src/FeeVault.sol)

### Summary
`FeeVault.claim()` pays out a creator's accrued USDC balance by hardcoding `msg.sender` as the transfer recipient, with no way to designate an alternate `to` address. Because the vault's asset is real USDC (a token with a centralized blacklist), a creator who is later blacklisted by Circle cannot ever retrieve their already-accrued `creatorBalance`, mirroring the reported "funder cannot refund because recipient is blocked" bug class.

### Finding Description
`claim()` reads `$.creatorBalance[msg.sender]`, zeroes it, decrements `totalAccruedCreator`, and calls `$.usdc.safeTransfer(msg.sender, amount)`: [1](#0-0) 

The recipient is hardcoded to `msg.sender` — there is no parameter allowing the caller to redirect the payout to a different address. `FeeVault` is initialized with a real `usdc_` token address: [2](#0-1) 

USDC (Circle) enforces an on-chain blacklist that can block `transfer`/`transferFrom` to a flagged address at any time, independent of the vault's own logic. If a creator's address is added to that blacklist after fees have already accrued to `creatorBalance[creator]` (via `Zap._accrueFee` → `FeeVault.accrue`, itself driven by ordinary `Zap.buy`/`Zap.sell` trading activity on that creator's launched token), every future call to `claim()` from that creator will revert inside `safeTransfer`, because USDC's own transfer logic reverts for a blacklisted recipient — regardless of gas or retries. There is no owner/admin function in `FeeVault.sol` to rescue, redirect, or reassign a stuck `creatorBalance`, and `Bonding.transferCreator` (which reassigns *future* fee attribution) does nothing for previously accrued, unclaimed balances already sitting in `creatorBalance[oldCreator]` — the mapping key is fixed to the old, now-blacklisted address.

This is structurally identical to the `BountyCore.refundDeposit` issue: a protocol invariant (funder/creator should always be able to reclaim funds owed to them) is broken because the payout function transfers directly to the stored/caller address with no override, and that address can become permanently blocked by an external token's compliance layer.

### Impact Explanation
Any USDC blacklisting of a creator address (a realistic, non-privileged, externally-triggered event under Circle's control) permanently freezes that creator's entire pooled `creatorBalance` in `FeeVault` — potentially the accumulated 0.25% creator fee share from all of that creator's launched tokens' buy/sell volume. The funds remain accounted for in `totalAccruedCreator` (backing FeeVault's other claims) but are unclaimable forever, since `claim()` has no alternate-recipient path and no owner rescue exists.

### Likelihood Explanation
Likelihood is Medium: it requires an external, out-of-protocol event (Circle blacklisting an address) rather than an on-chain exploit, so it is not attacker-triggerable but is a realistic operational risk given the protocol's exclusive reliance on real USDC for all fee flows (`Zap` fee deduction → `FeeVault.accrue`/`claim`/`claimProtocol`). Once triggered, the loss is deterministic and total for that creator's balance — there is no workaround, retry, or governance-controlled recovery path in the current contract.

### Recommendation
Add a `claimTo(address to)` (or an owner-gated `rescueCreatorBalance(address creator, address to)`) variant to `FeeVault.sol` so a blacklisted creator (or the protocol on their behalf, with appropriate authorization/signature) can redirect their `creatorBalance` payout to a fresh, non-blacklisted address instead of being hard-locked to `msg.sender`.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`; traders `buy`/`sell` it over time, and `Zap._accrueFee` → `FeeVault.accrue` credits `creatorBalance[C]` with real USDC. [3](#0-2) 
2. Circle blacklists address `C` on USDC (independent of alt.fun; e.g., due to unrelated OFAC/compliance action).
3. `C` calls `FeeVault.claim()`. `$.usdc.safeTransfer(msg.sender, amount)` reverts because USDC's transfer implementation blocks transfers to a blacklisted address. [1](#0-0) 
4. `C` has no way to change `msg.sender` for the claim, and no admin function exists to move `creatorBalance[C]` to a new address — the funds are permanently frozen in the vault.

Note: I could not locate an admin "rescue" or "redirect" function anywhere in `FeeVault.sol` within the indexed contents; if such a function exists in a part of the file not covered by the index, this would need to be confirmed via a full read of the file in a Devin session.

### Citations

**File:** packages/contracts/src/FeeVault.sol (L83-92)
```text
    function initialize(
        address usdc_,
        address feeTo_
    ) external initializer {
        if (usdc_ == address(0) || feeTo_ == address(0)) revert ZeroAddress();
        __Ownable_init(msg.sender);
        FeeVaultStorage storage $ = _s();
        $.usdc = IERC20(usdc_);
        $.feeTo = feeTo_;
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
