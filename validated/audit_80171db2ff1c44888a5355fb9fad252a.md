### Title
Single-Step `DEFAULT_ADMIN_ROLE` Transfer in `LRTConfig` Can Permanently Lock Protocol Admin Functions - (File: contracts/LRTConfig.sol)

---

### Summary

`LRTConfig` inherits from OpenZeppelin's `AccessControlUpgradeable` (not `AccessControlDefaultAdminRulesUpgradeable`), meaning the `DEFAULT_ADMIN_ROLE` — the root authority for the entire protocol — can be transferred or renounced in a single, unconfirmed step. If the admin accidentally grants the role to an invalid address and revokes their own, or simply calls `renounceRole`, the entire protocol loses its admin functionality permanently with no recovery path.

---

### Finding Description

`LRTConfig` is the central authority contract for the LRT-rsETH protocol. Every other core contract (`LRTDepositPool`, `LRTOracle`, `LRTWithdrawalManager`, `LRTUnstakingVault`, `NodeDelegator`, etc.) derives all role checks from `lrtConfig` via `LRTConfigRoleChecker`. [1](#0-0) 

`LRTConfig` uses plain `AccessControlUpgradeable`: [2](#0-1) 

This means `DEFAULT_ADMIN_ROLE` management is single-step:
- `grantRole(DEFAULT_ADMIN_ROLE, newAdmin)` — immediately effective, no confirmation required
- `revokeRole(DEFAULT_ADMIN_ROLE, oldAdmin)` — immediately effective
- `renounceRole(DEFAULT_ADMIN_ROLE, self)` — immediately effective

There is no pending-admin pattern, no two-step confirmation, and no delay. A typo in the new admin address, or an accidental `renounceRole` call, permanently removes admin control from the protocol.

All role checks in every consumer contract flow through `lrtConfig`: [3](#0-2) [4](#0-3) 

---

### Impact Explanation

Loss of `DEFAULT_ADMIN_ROLE` in `LRTConfig` permanently disables all `onlyLRTAdmin`-gated functions across the entire protocol, including:

- `unpause()` in `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTUnstakingVault` — if the protocol is paused (by `PAUSER_ROLE`) and admin role is lost, **funds are permanently frozen** with no recovery path.
- `setContract`, `setToken`, `setRSETH`, `updateAssetStrategy` in `LRTConfig` — protocol configuration becomes immutable and unrecoverable.
- `addNodeDelegatorContractToQueue` / `removeManyNodeDelegatorContractsFromQueue` in `LRTDepositPool`. [5](#0-4) 

**Impact: Medium — Permanent freezing of admin-controlled functions; escalates to Critical (permanent freezing of funds) if combined with a paused state.**

---

### Likelihood Explanation

Likelihood is low. The scenario requires the current admin to make an operational mistake: granting `DEFAULT_ADMIN_ROLE` to a wrong/uncontrolled address and revoking their own, or calling `renounceRole` directly. This is the same class of human error the original report describes for `transferOwnership`. No external attacker can trigger this path.

---

### Recommendation

Replace `AccessControlUpgradeable` with `AccessControlDefaultAdminRulesUpgradeable` in `LRTConfig`. This enforces a mandatory two-step, time-delayed transfer of `DEFAULT_ADMIN_ROLE`:

```solidity
// Before
contract LRTConfig is ILRTConfig, AccessControlUpgradeable { ... }

// After
contract LRTConfig is ILRTConfig, AccessControlDefaultAdminRulesUpgradeable { ... }
```

`AccessControlDefaultAdminRulesUpgradeable` requires the new admin to explicitly call `acceptDefaultAdminTransfer()` after a configurable delay, preventing accidental permanent lockout. [6](#0-5) 

---

### Proof of Concept

1. Current admin of `LRTConfig` calls:
   ```solidity
   lrtConfig.grantRole(DEFAULT_ADMIN_ROLE, 0xDeAdBeEf...); // typo/wrong address
   lrtConfig.revokeRole(DEFAULT_ADMIN_ROLE, adminAddress);  // revokes own role
   ```
   OR simply:
   ```solidity
   lrtConfig.renounceRole(DEFAULT_ADMIN_ROLE, adminAddress);
   ```
2. `DEFAULT_ADMIN_ROLE` is now held by an uncontrolled address (or no one).
3. Any call to `onlyLRTAdmin`-gated functions across `LRTDepositPool`, `LRTWithdrawalManager`, `LRTUnstakingVault`, `NodeDelegator`, and `LRTConfig` itself reverts permanently.
4. If `PAUSER_ROLE` holder subsequently calls `pauseAll()` on `LRTConfig`, all user deposits and withdrawals are frozen with no admin able to call `unpause()`. [7](#0-6) [3](#0-2)

### Citations

**File:** contracts/LRTConfig.sol (L10-19)
```text
import { AccessControlUpgradeable } from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";

interface IPausable {
    function pause() external;
    function paused() external view returns (bool);
}

/// @title LRTConfig - LRT Config Contract
/// @notice Handles LRT configuration
contract LRTConfig is ILRTConfig, AccessControlUpgradeable {
```

**File:** contracts/LRTConfig.sol (L49-62)
```text
    function initialize(address admin, address stETH, address ethX, address rsETH_) external initializer {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(rsETH_);

        __AccessControl_init();
        _setToken(LRTConstants.ST_ETH_TOKEN, stETH);
        _setToken(LRTConstants.ETHX_TOKEN, ethX);
        _addNewSupportedAsset(stETH, 100_000 ether);
        _addNewSupportedAsset(ethX, 100_000 ether);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);

        rsETH = rsETH_;
    }
```

**File:** contracts/LRTConfig.sol (L237-251)
```text
    function setContract(bytes32 contractKey, address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setContract(contractKey, contractAddress);
    }

    /// @dev private function to set a contract
    /// @param key Contract key
    /// @param val Contract address
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
```

**File:** contracts/LRTConfig.sol (L261-285)
```text
    /// @dev Pauses all pausable contracts within the protocol (no-op for already paused contracts).
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L12-13)
```text
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig;
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L58-63)
```text
    modifier onlyLRTAdmin() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigAdmin();
        }
        _;
    }
```
