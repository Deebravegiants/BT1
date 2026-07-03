### Title
`RSETH` ERC20 Transfers Not Blocked When Contract Is Paused - (File: contracts/RSETH.sol)

### Summary

`RSETH` inherits from `ERC20Upgradeable` and `PausableUpgradeable` separately, but never applies `whenNotPaused` to the `_transfer` hook. As a result, any rsETH holder can freely call the standard ERC20 `transfer()` and `transferFrom()` functions even when the contract is paused, bypassing the emergency stop mechanism entirely.

### Finding Description

`RSETH` is declared as:

```solidity
contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
``` [1](#0-0) 

It imports `PausableUpgradeable` directly from the security module, not `ERC20PausableUpgradeable`:

```solidity
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
``` [2](#0-1) 

`PausableUpgradeable` only provides the `whenNotPaused` modifier — it does **not** automatically hook into ERC20 transfer paths. The contract correctly guards `mint()` and `burnFrom()`: [3](#0-2) 

However, the `_transfer` override — which is the internal function called by the public `transfer()` and `transferFrom()` — has **no** `whenNotPaused` guard:

```solidity
function _transfer(address from, address to, uint256 amount) internal override {
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);
}
``` [4](#0-3) 

The correct fix would be to use `ERC20PausableUpgradeable`, which overrides `_beforeTokenTransfer` to enforce `!paused()` on all transfer paths (transfer, mint, burn): [5](#0-4) 

### Impact Explanation

When the PAUSER_ROLE triggers `pause()` — typically in response to a security incident such as a compromised minter, oracle manipulation, or active exploit — the intent is to halt all rsETH token movement. Because `_transfer` lacks `whenNotPaused`, any rsETH holder can still call `transfer()` or `transferFrom()` freely. This means:

- An attacker who has already obtained rsETH (e.g., via a compromised minter before the pause) can move tokens to fresh addresses, defeating fund-freezing efforts.
- The `blockUserTransfers` / `recoverFrozenFunds` emergency recovery flow is undermined: a blocked user cannot be stopped from transferring if the contract is paused but the transfer path is open.

**Impact: Medium — Temporary freezing of funds.** The pause is supposed to temporarily freeze all token operations; it fails to do so for the primary transfer path.

### Likelihood Explanation

The pause mechanism exists precisely for emergencies. Any rsETH holder — no privilege required — can call the standard ERC20 `transfer()` or `transferFrom()` at any time, including during a pause. The entry path is direct and requires no special setup.

### Recommendation

Replace the separate `PausableUpgradeable` inheritance with `ERC20PausableUpgradeable`, which automatically enforces the paused state on all token transfer paths via `_beforeTokenTransfer`:

```diff
-import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
+import { ERC20PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PausableUpgradeable.sol";

-contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
+contract RSETH is Initializable, LRTConfigRoleChecker, ERC20PausableUpgradeable {
```

Alternatively, add `whenNotPaused` directly to the `_transfer` override:

```diff
-function _transfer(address from, address to, uint256 amount) internal override {
+function _transfer(address from, address to, uint256 amount) internal override whenNotPaused {
```

### Proof of Concept

1. Deploy `RSETH` and mint tokens to `alice`.
2. PAUSER_ROLE calls `pause()` — `RSETH.paused()` returns `true`.
3. `alice` calls `rsETH.transfer(bob, amount)`.
4. The call succeeds: `alice`'s balance decreases and `bob`'s increases, despite the contract being paused.
5. Calling `mint()` or `burnFrom()` during the same paused state correctly reverts, confirming the asymmetry.

The root cause is that `ERC20Upgradeable.transfer()` → `_transfer()` never reaches any `whenNotPaused` check, because `PausableUpgradeable` provides only the modifier and does not hook into the ERC20 transfer pipeline. [6](#0-5)

### Citations

**File:** contracts/RSETH.sol (L8-8)
```text
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
```

**File:** contracts/RSETH.sol (L13-13)
```text
contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
```

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

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/extensions/ERC20PausableUpgradeable.sol (L37-41)
```text
    function _beforeTokenTransfer(address from, address to, uint256 amount) internal virtual override {
        super._beforeTokenTransfer(from, to, amount);

        require(!paused(), "ERC20Pausable: token transfer while paused");
    }
```
