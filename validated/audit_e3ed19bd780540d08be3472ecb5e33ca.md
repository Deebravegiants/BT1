## Analysis Result [1](#0-0) 

### Title
Unvalidated `newCreator` in `Bonding.transferCreator` Can Permanently Freeze a Token's Creator Fee Stream - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding.transferCreator` only checks `newCreator != address(0)` and `newCreator != info.creator` before overwriting `info.creator`. It performs no check that `newCreator` is an address capable of ever calling `FeeVault.claim()` again — e.g. it can be set to a known burn address, an unrelated immutable contract, or any contract with no logic/owner able to invoke `claim()`. Since `info.creator` is also the only key used for all future fee attribution and the *only* address authorized to call `transferCreator` again, an unrecoverable `newCreator` permanently locks all past and future creator-fee USDC accrued in `FeeVault` for that token.

### Finding Description
`transferCreator` is a fully permissionless-reachable, creator-self-service function: [1](#0-0) 

The only guards are a zero-address check and a same-address check. There is no `newCreator.code.length == 0`-style EOA gate, no two-step "accept" pattern, and no admin override elsewhere in `Bonding.sol` to reset `info.creator` if it is misconfigured.

Every future `Zap._buyInternal`/`_sellInternal` fee accrual reads `Bonding.creatorOf(tokenAddress)` and calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)` — `creatorAmount` is credited to `creatorBalance[creator]` inside `FeeVault`: [2](#0-1) 

Withdrawal is strictly pull-based and keyed to `msg.sender`: [3](#0-2) 

If `newCreator` is:
- a known burn/black-hole address (e.g. `0x...dEaD`) with no private key, or
- any deployed contract that has no function able to call `FeeVault.claim()` (the overwhelming majority of contracts), or
- a not-yet-deployed `CREATE2`/predicted address that never gets deployed with the right logic,

then no one can ever call `FeeVault.claim()` as that address again, and — critically — no one can call `Bonding.transferCreator` again either, since that function is gated on `msg.sender == info.creator`. The token's entire creator-fee stream (0.25% of every buy/sell, indefinitely) is permanently unclaimable and stuck in `FeeVault`.

Notably, the project already recognizes and defends against exactly this class of bug elsewhere: `FeeVault` deliberately uses `Ownable2StepUpgradeable` instead of one-step ownership transfer specifically "so a bad `transferOwnership` can be cancelled... before it takes effect — single-step transfer to a fat-fingered or contract-incompatible address would otherwise brick every owner-only path" — see the doc comment: [4](#0-3) 

That same rationale was never applied to `transferCreator`, which is the one place in the system that transfers a fee-claim role via a single, unchecked call.

### Impact Explanation
This freezes the creator's fee balance in `FeeVault`, both already-accrued and every future accrual for the life of the token (the token can never re-graduate a new creator, and `creatorFeeBps_` accrual continues to route to the dead `creator` on every subsequent trade). This is a permanent freezing of creator funds, matching the accepted impact class (freezing of creator funds in `FeeVault`). Because trading continues indefinitely (curve and post-graduation), the amount at risk grows without bound and can never be recovered — there is no admin backstop in `Bonding.sol` to reset `tokenInfo[token].creator`.

### Likelihood Explanation
Reaching this state requires only a single permissionless call from the current creator (or a scam/bait UI/contract tricking a creator into "upgrading"/"migrating" their creator role to an attacker-supplied contract address, which is a realistic social-engineering vector given `newCreator` is a raw user-supplied parameter with no safety rail). No privileged role, no protocol misconfiguration, and no external asset behavior is required — it is a single validated transaction away.

### Recommendation
Add a two-step "propose/accept" pattern to `transferCreator`, mirroring the pattern the codebase already uses for `FeeVault`'s `Ownable2StepUpgradeable`: `transferCreator(token, newCreator)` should only set a `pendingCreator`, and a new `acceptCreator(token)` called by `msg.sender == pendingCreator` should finalize the change. This guarantees the new address can actually transact before the old creator's claim rights are revoked, eliminating the possibility of bricking the fee stream via a fat-fingered EOA typo or a malicious/incapable contract address.

### Proof of Concept
1. Creator launches a token via `Zap.createToken`, `Bonding.tokenInfo[token].creator == creator`.
2. Trading accrues fees into `FeeVault.creatorBalance[creator]` via ordinary `Zap.buy`/`Zap.sell` calls.
3. Creator (mistakenly, or lured by a phishing "migrate rewards" contract) calls `Bonding.transferCreator(token, deadOrIncapableContract)`.
4. `transferCreator` succeeds (only zero-address/same-address checks exist): `info.creator = deadOrIncapableContract`.
5. All subsequent `Zap` fee accruals route `creatorAmount` into `FeeVault.creatorBalance[deadOrIncapableContract]`.
6. `FeeVault.claim()` can never be called as `deadOrIncapableContract` (no private key / no matching function), and `Bonding.transferCreator` can never be called again for this token (`msg.sender != info.creator` for anyone else) — the entire creator fee balance for the token is permanently frozen.

### Citations

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

**File:** packages/contracts/src/FeeVault.sol (L12-21)
```text
/// @notice Holds creator + protocol USDC fees from allowlisted depositors (Zaps).
/// @dev Depositors `transfer` USDC then call `accrue` — the vault never pulls
///      via `transferFrom`. Trust is bounded by an O(1) underfund check in
///      `accrue` (vault USDC balance ≥ outstanding creator + protocol claims),
///      so a buggy depositor can't inflate balances beyond delivered funds.
///      Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
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
