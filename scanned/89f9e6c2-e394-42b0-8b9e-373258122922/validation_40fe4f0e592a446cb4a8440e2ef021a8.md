### Title
`RSETH._transfer` Does Not Enforce Transfer Block on the Spender (`msg.sender`) in `transferFrom` - (File: contracts/RSETH.sol)

### Summary
`RSETH` overrides `_transfer` to enforce a `transfersBlockedUntil` restriction on both `from` and `to`, but never checks `msg.sender` (the spender) when `transferFrom` is used. A blocked spender retains the ability to drain rsETH from any victim who has granted it an allowance, bypassing the intended transfer-block enforcement entirely.

### Finding Description
`RSETH` maintains a `transfersBlockedUntil` mapping that is intended to block all token movement involving a flagged address:

```solidity
/// @dev If > 0, transfers TO or FROM this address are blocked until timestamp (24h block)
mapping(address account => uint256 blockedUntil) public transfersBlockedUntil;
```

The `_transfer` override enforces this on `from` and `to`:

```solidity
function _transfer(address from, address to, uint256 amount) internal override {
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);
}
```

`transferFrom` is inherited unchanged from `ERC20Upgradeable`:

```solidity
function transferFrom(address from, address to, uint256 amount) public virtual override returns (bool) {
    address spender = _msgSender();
    _spendAllowance(from, spender, amount);
    _transfer(from, to, amount);   // only checks `from` and `to`
    return true;
}
```

`msg.sender` (the spender) is never passed to `_enforceNotBlocked`. A blocked spender can therefore call `transferFrom(victim, attacker, amount)` where neither `victim` nor `attacker` is blocked, and the call succeeds.

### Impact Explanation
When the Kelp DAO manager identifies a malicious or compromised contract (e.g., a vulnerable DeFi protocol that holds rsETH approvals from many users) and calls `blockUserTransfers`, the block is placed on that contract's address. However, because `transferFrom` never checks `msg.sender`, the blocked contract can immediately call `transferFrom` to drain rsETH from every victim that has approved it, routing funds to an unblocked attacker address. The transfer-block mechanism — the protocol's primary emergency tool for containing a known-bad actor — is rendered ineffective against spenders.

### Likelihood Explanation
Medium. The scenario requires: (1) a spender address has been identified as malicious and blocked, and (2) that spender holds outstanding approvals from victims. Both conditions are realistic: the `blockUserTransfers` function exists precisely for this emergency scenario, and DeFi integrations routinely hold max-approvals. The attacker's window is the 24-hour block duration, during which victims may not revoke approvals.

### Recommendation
Override `transferFrom` in `RSETH` to also call `_enforceNotBlocked(msg.sender)` before delegating to the parent implementation, mirroring the pattern already applied to `from` and `to` in `_transfer`.

### Proof of Concept
1. Victim calls `rsETH.approve(maliciousContract, type(uint256).max)`.
2. `maliciousContract` is identified as compromised; manager calls `blockUserTransfers([maliciousContract])`.
3. `maliciousContract` calls `rsETH.transferFrom(victim, attacker, victimBalance)`.
4. `ERC20Upgradeable.transferFrom` calls `RSETH._transfer(victim, attacker, victimBalance)`.
5. `_enforceNotBlocked(victim)` — victim is not blocked → passes. [1](#0-0) 
6. `_enforceNotBlocked(attacker)` — attacker is not blocked → passes.
7. `super._transfer` executes; victim's rsETH is transferred to attacker.
8. `maliciousContract` (the blocked spender) is never checked. [1](#0-0) 

The root cause is that `_transfer` only receives `from` and `to` — `msg.sender` is consumed by `ERC20Upgradeable.transferFrom` and never forwarded to the block-enforcement logic. [2](#0-1)

### Citations

**File:** contracts/RSETH.sol (L30-31)
```text
    /// @dev If > 0, transfers TO or FROM this address are blocked until timestamp (24h block)
    mapping(address account => uint256 blockedUntil) public transfersBlockedUntil;
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }
```
