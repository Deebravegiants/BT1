### Title
Inconsistent Pause Enforcement in RSETH — `_transfer` Lacks `whenNotPaused` Modifier - (File: contracts/RSETH.sol)

### Summary
The `RSETH` token contract enforces `whenNotPaused` on `mint` and `burnFrom`, but the overridden `_transfer` function — which backs the public `transfer` and `transferFrom` ERC-20 entry points — carries no such guard. Any rsETH holder can freely move tokens while the contract is paused, undermining the emergency freeze.

### Finding Description
`RSETH.sol` inherits `PausableUpgradeable` and applies `whenNotPaused` to the two privileged write paths:

```solidity
// contracts/RSETH.sol line 229-240
function mint(address to, uint256 amount)
    external
    onlyRole(LRTConstants.MINTER_ROLE)
    whenNotPaused          // ← guarded
    checkDailyMintLimit(amount)
{ ... }

// line 245-248
function burnFrom(address account, uint256 amount)
    external
    onlyRole(LRTConstants.BURNER_ROLE)
    whenNotPaused          // ← guarded
{ ... }
```

The internal `_transfer` override, however, only enforces the per-address block list:

```solidity
// contracts/RSETH.sol line 287-291
function _transfer(address from, address to, uint256 amount) internal override {
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);   // no whenNotPaused
}
```

Because the standard OpenZeppelin `transfer` and `transferFrom` functions delegate to `_transfer`, any rsETH holder can invoke them regardless of the contract's paused state. [1](#0-0) [2](#0-1) 

### Impact Explanation
When the RSETH contract is paused — typically triggered by the `PAUSER_ROLE` in response to an oracle anomaly, an exploit, or a price-drop circuit-breaker in `LRTOracle._updateRsETHPrice` — the intended effect is a complete freeze of all token activity. Minting and burning are correctly blocked, but the unrestricted `_transfer` path allows holders to:

- Move rsETH between wallets, defeating any attempt to quarantine compromised addresses via `blockUserTransfers` (since a blocked address can receive tokens from an unblocked one, or vice-versa, through a third party).
- Circumvent the freeze window that the protocol relies on to assess and remediate an incident before further token movement occurs.

The contract fails to deliver its promised invariant — that a paused state halts all token operations — without causing direct value destruction. This maps to **Low: Contract fails to deliver promised returns, but doesn't lose value**. [3](#0-2) [4](#0-3) 

### Likelihood Explanation
The entry path is the standard ERC-20 `transfer` / `transferFrom` interface, callable by any rsETH holder with zero privilege. No special role, no front-running, no external dependency is required. The only precondition is that the contract is paused, which is precisely the scenario where the guard matters most.

### Recommendation
Add `whenNotPaused` to the `_transfer` override so that all token movement — not just minting and burning — is halted during an emergency pause:

```solidity
function _transfer(address from, address to, uint256 amount)
    internal
    override
    whenNotPaused          // add this
{
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);
}
```

### Proof of Concept
1. `PAUSER_ROLE` calls `RSETH.pause()` — contract enters paused state.
2. Any rsETH holder calls `rsETH.transfer(recipient, amount)` — succeeds because `_transfer` has no `whenNotPaused` guard.
3. Simultaneously, `rsETH.mint(...)` and `rsETH.burnFrom(...)` revert with `EnforcedPause` — demonstrating the inconsistency.
4. The holder can continue moving tokens freely throughout the pause window, defeating the intended freeze. [5](#0-4) [2](#0-1)

### Citations

**File:** contracts/RSETH.sol (L183-191)
```text
    /// @dev Triggers stopped state. Contract must not be paused.
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }

    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```

**File:** contracts/RSETH.sol (L229-248)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }

    /// @notice Burns rsETH when called by an authorized caller
    /// @param account the account to burn from
    /// @param amount the amount of rsETH to burn
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```
