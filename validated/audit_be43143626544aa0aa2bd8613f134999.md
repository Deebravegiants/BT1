### Title
Creator Fee Claims Are Permanently Locked If USDC Blacklists The Creator's Address, With No Recipient-Override Or Rescue Path - (`packages/contracts/src/FeeVault.sol`)

### Summary
`FeeVault.claim()` is hard-wired to pay `msg.sender` and offers no way for a creator to redirect the payout to a different, unblocked address. Since the vault's reserve asset is USDC — a centrally-administered stablecoin with an on-chain blacklist that reverts `transfer`/`transferFrom` to sanctioned addresses — a creator address placed on that blacklist permanently loses access to their accrued `creatorBalance`, exactly the "withdraw requires transferring the reserve coin to a fixed recipient with no registration/eligibility check" defect the external report describes.

### Finding Description
`FeeVault.claim()` reads `creatorBalance[msg.sender]` and unconditionally transfers to `msg.sender`: [1](#0-0) 

There is no parameter to specify an alternate recipient, and no owner-side rescue/override function exists anywhere in the contract to redirect or re-attribute a stuck `creatorBalance[creator]` entry — the full contract surface (accrual, claim, claimProtocol, sweepDonations, admin setters) is visible and contains no such escape hatch.

USDC on most deployment chains (per Circle's implementation) enforces a `blacklist` that makes `transfer`/`transferFrom` to a blacklisted address revert. If a creator's wallet is ever blacklisted (sanctions listing, compliance action, or the address simply being flagged upstream for any reason), every future call to `claim()` from that address will revert inside `$.usdc.safeTransfer(msg.sender, amount)` — permanently, since `msg.sender` cannot be changed and `creatorBalance[msg.sender]` is only decremented as part of that same reverting transaction (so the balance is never lost from state, but is also never claimable). This is the precise analog to the reported bug: a withdrawal path that transfers the reserve asset straight to a fixed, unvalidated recipient, with no `is_account_registered`-style eligibility check and no fallback path, causing funds to become permanently locked in the protocol.

Unlike `Zap.sell`, where a failed USDC transfer reverts the entire trade and returns the trader to their pre-trade state, `FeeVault.claim()` has no alternative venue: the creator's accrued fees exist only as a `creatorBalance` entry redeemable through this single function.

### Impact Explanation
Any creator's entire outstanding and all future `creatorBalance` becomes permanently unclaimable the moment their address is blacklisted by the USDC issuer, since `accrue()` keeps crediting `creatorBalance[creator]` from ongoing trading fees on their token(s), and none of it can ever be extracted. This is a real, uncontrolled freezing of creator funds with no protocol-side remedy — `Ownable2StepUpgradeable`'s owner has no function to reassign or forcibly pay out a stuck balance.

### Likelihood Explanation
Reachable without any special privilege — the trigger event (USDC issuer blacklisting an address) is external and outside protocol control, but is a documented, non-hypothetical capability of USDC. Any creator whose fee-earning token remains active is exposed for as long as their address stays blacklisted, and the protocol currently has zero mitigation.

### Recommendation
Add a `claimTo(address recipient)` variant (with appropriate access control tying it to the caller being the creator, e.g. `creatorBalance[msg.sender]` but paid to `recipient`), and/or an owner-gated rescue function that can redirect a specific creator's stranded balance to a caller-specified address after some recovery process. This mirrors the referenced fix pattern of validating the destination and providing an alternate transfer path rather than hard-binding the payout address.

### Proof of Concept
1. Creator `C` launches a token via `Zap.createToken`, accrues fees via ordinary buy/sell activity so `FeeVault.creatorBalance(C) > 0` (per `Zap._accrueFee` → `FeeVault.accrue`).
2. Circle blacklists address `C` on the USDC contract (`isBlacklisted(C) == true`), an action entirely outside the alt.fun protocol.
3. `C` calls `FeeVault.claim()`; `$.usdc.safeTransfer(C, amount)` reverts due to the USDC blacklist check, so the entire `claim()` transaction reverts.
4. `C` has no alternate function to call — `creatorBalance(C)` remains stuck forever, and every future `accrue()` for `C`'s token(s) adds to a balance that can never be withdrawn. [1](#0-0)

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
