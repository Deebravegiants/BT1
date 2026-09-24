## Analog Finding

### Title
Push-based FeeVault payouts permanently freeze creator/protocol USDC if the recipient is USDC-blacklisted - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` and `FeeVault.claimProtocol()` both use a push pattern — they `safeTransfer` accrued USDC directly to a hardcoded recipient (`msg.sender` for `claim`, the stored `feeTo` for `claimProtocol`) rather than letting the recipient pull funds to an address of their choosing. If that recipient is ever added to USDC's blacklist (a real-world, externally-controlled event outside the protocol's or the user's control — exactly the root cause described in the M-07 report), every future call to that function reverts, and the accrued balance becomes permanently unclaimable on-chain.

### Finding Description
`FeeVault.claim()` pays out the caller's entire `creatorBalance[msg.sender]` by pushing USDC straight to `msg.sender`: [1](#0-0) 

There is no alternate recipient parameter, no pull-based withdrawal, and no way for the creator to redirect the payout to a fresh, unblacklisted address. Fee accrual into `creatorBalance[creator]` happens automatically and permissionlessly any time a trader buys/sells the creator's token via `Zap`: [2](#0-1) 

`Bonding.transferCreator` lets the current creator hand attribution to a new address, but this is a *voluntary* opt-in the creator must trigger themselves — it does not help once the creator's existing balance is already stuck and the same blacklisted address is the only one that has ever been recorded as `creator` for that token (a creator who discovers they are blacklisted can call `transferCreator`, but any balance *already* accrued to the old, blacklisted address is stuck forever since `claim()` cannot re-target the payout).

The same push pattern exists on the protocol side. `claimProtocol()` is permissionless (anyone can call it) but always pays the single stored `feeTo` address: [3](#0-2) 

If `feeTo` becomes USDC-blacklisted, every subsequent `claimProtocol()` call reverts on the `safeTransfer`, and — because `protocolBalance` is a single running pool shared across every launched token — 100% of the protocol's fee revenue across the entire platform accrues but cannot be withdrawn until the owner notices and calls `setFeeTo`. The vault's own doc comment even flags that `setFeeTo` should ideally be preceded by settling the outstanding balance to the *current* recipient — impossible once that recipient is blacklisted: [4](#0-3) 

This is a direct structural analog of the reported bug: a system that always *pushes* funds to a fixed address instead of letting the recipient *pull* them fails permanently — not just temporarily — the moment that fixed address is blacklisted by the underlying USDC contract, exactly the scenario the report calls out for the liquidation flow.

### Impact Explanation
For the creator path: any creator whose wallet is later sanctioned/blacklisted by Circle permanently loses access to their already-accrued creator fee share in `FeeVault`. Because `creatorBalance` is keyed by address with no re-routing mechanism in `claim()`, this is a genuine, non-recoverable-on-chain freezing of creator funds — squarely within the accepted impact class ("permanent freezing of trader, creator or LP funds").

For the protocol path, the blast radius is larger: since `protocolBalance` is a single shared pool across every token launched on the platform, a blacklisted `feeTo` freezes *all* protocol revenue accrued platform-wide until an owner-level `setFeeTo` rotation, which the contract's own comments frame as an exceptional, imperfect remedy (the "settle first" step becomes impossible).

### Likelihood Explanation
Low but non-zero, matching the original report's severity/likelihood split (High impact / Low likelihood): USDC blacklisting is externally controlled (Circle-driven, e.g. sanctions or fraud response) and not something an attacker can trigger at will, but it is a documented real-world risk for any protocol built on a centrally-administered stablecoin, and requires no cooperation or mistake from the alt.fun team — any active creator or the configured `feeTo` could be blacklisted independent of protocol behavior.

### Recommendation
Replace the push-only `claim()`/`claimProtocol()` payouts with a pull-based or redirectable claim: e.g., allow claiming to an explicit `to` address supplied by the caller (with appropriate authorization), or add an owner-gated `rescueCreatorBalance(creator, to)` / emergency re-routing path so a blacklisted recipient's already-accrued balance is not stranded forever. At minimum, decouple `protocolBalance` payout from a single mutable `feeTo` so a blacklist event on one address cannot freeze the entire platform's accrued protocol revenue.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`; ordinary buy/sell traffic accrues USDC into `FeeVault.creatorBalance[C]` via `Zap._accrueFee` → `FeeVault.accrue`.
2. USDC's issuer blacklists address `C` (independent external event).
3. `C` calls `FeeVault.claim()`. `usdc.safeTransfer(C, amount)` reverts because `C` is blacklisted by the USDC token contract.
4. `C`'s entire `creatorBalance[C]` remains stuck; there is no parameterized alternate recipient in `claim()`, so the funds can never be withdrawn on-chain.
5. Analogously, if the owner-configured `feeTo` is blacklisted, every permissionless `claimProtocol()` call reverts identically, freezing the shared `protocolBalance` accrued from every token on the platform until an owner calls `setFeeTo`.

### Citations

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

**File:** packages/contracts/src/FeeVault.sol (L179-193)
```text
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
