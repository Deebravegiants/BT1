### Title
Creator (and protocol) USDC fees permanently frozen in `FeeVault` if the claiming address is blacklisted by USDC - ([File: packages/contracts/src/FeeVault.sol])

### Summary
`FeeVault.claim()` and `FeeVault.claimProtocol()` hard-code the payout recipient to `msg.sender` / the stored `feeTo` address, with no way for the caller to redirect the transfer to a different address. Since the fee asset is USDC — a blacklist-capable token (the exact asset named in the original report) — a creator (or `feeTo`) whose address gets blacklisted by Circle can never retrieve their pooled `creatorBalance`, permanently freezing those funds inside the vault.

### Finding Description
`FeeVault.claim()` reads `creatorBalance[msg.sender]`, zeroes it, and unconditionally calls `usdc.safeTransfer(msg.sender, amount)`: [1](#0-0) 

There is no `recipient` parameter and no alternate withdrawal path. `Bonding.transferCreator(tokenAddress, newCreator)` only reassigns *future* fee attribution for a given token going forward — it does not move the already-accrued balance sitting in `creatorBalance[oldCreator]` in `FeeVault`, since that mapping is keyed by the address that was the creator at the time `accrue()` was called, per the documented behavior "`transferCreator(tokenAddress, newCreator)` (on `Bonding`) — transfers role and future fee attribution": [2](#0-1) 

Because `FeeVault` fees are exclusively USDC (`accrue`/`claim` operate on the `usdc` field set at initialization), and USDC is a widely-used ERC20 with an on-chain blacklist controlled by Circle, if a creator's wallet is ever added to that blacklist, `usdc.safeTransfer(msg.sender, amount)` inside `claim()` will always revert (blacklisted addresses cannot receive USDC transfers), and the creator has no way to specify an alternate recipient. The `creatorBalance[creator]` entry, and the corresponding backing USDC actually held by the vault, become permanently unreachable — there is no admin sweep, no recipient override, and no alternate exit path for that specific creator's accrued balance.

`claimProtocol()` has the analogous structural issue (payout hard-coded to `feeTo`), but that address is owner-controlled and rotatable via `setFeeTo`, so the protocol side is mitigated by admin action; the creator side has no equivalent remediation, matching the unprivileged-actor freeze described in the original report.

### Impact Explanation
This is a permanent freezing of creator funds (Medium severity, matching the referenced report), since:
- Fees keep accruing to the blacklisted creator's `creatorBalance` on every buy/sell of tokens they created (`Zap._accrueFee` → `FeeVault.accrue`), growing the frozen balance over time.
- The backing USDC is real, vault-held USDC (per the `accrue` underfund invariant), so it is not just an accounting entry — actual funds are stuck.
- No governance/owner function exists to redirect or force-claim a specific creator's balance to a new address.

### Likelihood Explanation
Likelihood is realistic but not certain: it requires the creator's own wallet address to be added to USDC's blacklist (a real, documented occurrence for USDC/USDT-style tokens, as cited in the original report). This is outside the protocol's control and can happen to any creator address for reasons unrelated to alt.fun (e.g., unrelated OFAC/compliance action, prior involvement in flagged activity).

### Recommendation
Add a `recipient` parameter to `FeeVault.claim()` (and optionally to `claimProtocol`), so `msg.sender` can direct the payout to a different address:
```solidity
function claim(address recipient) external nonReentrant returns (uint256 amount) {
    ...
    $.usdc.safeTransfer(recipient, amount);
    emit CreatorFeesClaimed(msg.sender, recipient, amount);
}
```
Alternatively, add an owner-gated `rescueCreatorBalance(address creator, address to)` path usable only when `claim()` from `creator` demonstrably reverts, to unstick funds without giving up the permissionless design elsewhere in the vault.

### Proof of Concept
1. `depositor` (allowlisted `Zap`) calls `FeeVault.accrue(token, creator, creatorAmount, protocolAmount, isBuy)` repeatedly as `creator`'s token is traded, growing `creatorBalance[creator]`, per [3](#0-2) .
2. Circle (USDC issuer) blacklists `creator`'s address for reasons unrelated to alt.fun.
3. `creator` calls `FeeVault.claim()`. `usdc.safeTransfer(msg.sender, amount)` reverts because USDC blocks transfers to a blacklisted address, per [1](#0-0) .
4. `creator` has no way to designate a different recipient — `claim()` takes no address argument — so `creatorBalance[creator]` and its backing USDC remain permanently locked in `FeeVault`, even though `transferCreator` can redirect *future* fees, it cannot rescue the already-accrued, now-stuck balance.

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
