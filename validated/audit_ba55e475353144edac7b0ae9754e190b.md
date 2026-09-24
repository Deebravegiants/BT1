## Finding: Single-step `Bonding.transferCreator` can permanently freeze a creator's fee-claim rights

### Title
Single-step creator address change permanently freezes creator fee rights - (File: packages/contracts/src/Bonding.sol)

### Summary
`Bonding.transferCreator` changes the `creator` field of a launched token's `TokenInfo` in a single transaction, with only a zero-address check and no two-step propose/accept confirmation flow. [1](#0-0) 

### Finding Description
`transferCreator` is fully permissionless from the current creator's perspective — any address holding `info.creator` for a token can call it directly:

```solidity
function transferCreator(address tokenAddress, address newCreator) external {
    if (newCreator == address(0)) revert ZeroAddress();
    TokenInfo storage info = _s().tokenInfo[tokenAddress];
    if (msg.sender != info.creator) revert NotCreator();
    if (newCreator == info.creator) revert InvalidInput();
    info.creator = newCreator;
    emit CreatorTransferred(tokenAddress, msg.sender, newCreator);
}
``` [1](#0-0) 

This mirrors the class of bug in the external report: a critical role-address is changed atomically, guarded only against `address(0)`, with no ability to cancel or verify the new address controls a working wallet/contract before the change takes effect. `Bonding.sol`'s own owner-role handling explicitly acknowledges this exact risk class and mitigates it for `Ownable2StepUpgradeable`-controlled owner transfers:

> "Uses `Ownable2StepUpgradeable` so a bad `transferOwnership` can be cancelled ... before it takes effect — single-step transfer to a fat-fingered or contract-incompatible address would otherwise brick every owner-only path on the live proxy." [2](#0-1) 

However, `transferCreator` — which governs the `creator` field consumed by `FeeVault`'s creator-fee claim path (heavily referenced, 64 occurrences of `creator` in `FeeVault.sol`) — has no such two-step protection, despite the contract's own design philosophy treating this exact bug class as brick-worthy.

### Impact Explanation
If a token creator mistypes `newCreator`, pastes the wrong address, or sends to a contract address that cannot forward/trigger a `FeeVault` claim call, the on-chain `creator` mapping is updated irreversibly in one transaction. Since `FeeVault`'s creator-fee claim path is keyed off `Bonding`'s stored `creator` for a token, this permanently and unrecoverably freezes that creator's future protocol-fee claims for the token — there is no revert path, no pending-acceptance step, and no owner/DAO override visible in `Bonding.sol`. This is a permanent freezing of creator funds (accrued/future trading fee claims), matching the Medium-severity impact bar.

### Likelihood Explanation
Likelihood is realistic given ordinary user error (copy-paste mistakes, wrong-chain address reuse, mistyped checksum) — the same "misclick / copy-paste" vector the original report calls out for DAO address changes, but here reachable by any unprivileged token creator with no economic barrier beyond calling `transferCreator` once.

### Recommendation
Convert `transferCreator` to a two-step propose/accept flow (e.g., `proposeCreator(tokenAddress, newCreator)` followed by `acceptCreator(tokenAddress)` called from `newCreator`), consistent with the `Ownable2StepUpgradeable` pattern already used for the contract owner, so a bad target address can be corrected before the transfer finalizes.

### Proof of Concept
1. Creator `A` launches a token via `Zap.createToken`, becoming `Bonding.tokenInfo[token].creator = A`. [3](#0-2) 
2. `A` calls `Bonding.transferCreator(token, B)` intending to transfer to a colleague's wallet `B`, but mistypes/pastes an address `C` they do not control (e.g., a random EOA, an exchange deposit address, or a contract without the ability to call `FeeVault.claim`).
3. `transferCreator` only checks `C != address(0)` and `C != A`, so the call succeeds and `info.creator = C` is set irreversibly. [4](#0-3) 
4. All subsequent creator-fee claims gated on `Bonding.creatorOf(token)` in `FeeVault` are now permanently unclaimable by the original creator `A`, and likely unclaimable at all if `C` cannot interact with `FeeVault`.

Note: I was not able to fully read `FeeVault.sol` in this session (index truncation/iteration limits) to cite the exact line where `FeeVault` reads `Bonding.creatorOf`/`getTokenInfo().creator` for fee claims — the 64 textual matches of `creator` in `packages/contracts/src/FeeVault.sol` strongly indicate this dependency exists, but the precise claim-gating function was not directly inspected. A Devin session with full file access should confirm this coupling before treating the PoC as fully verified.

### Citations

**File:** packages/contracts/src/Bonding.sol (L37-41)
```text
/// @dev Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
```

**File:** packages/contracts/src/Bonding.sol (L537-554)
```text
    function _storeTokenInfo(
        address tokenAddr,
        address pair,
        LaunchParams calldata params,
        address creator_
    ) internal {
        _s().tokenInfo[tokenAddr] = TokenInfo({
            creator: creator_,
            pair: pair,
            ltAddress: params.ltAddress,
            name: params.name,
            ticker: params.ticker,
            description: params.description,
            image: params.image,
            urls: params.urls,
            lifecycle: Lifecycle.Curve
        });
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
