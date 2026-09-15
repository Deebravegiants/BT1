# [M] Storage slot management issue in LockingBase contract

## Summary
Severity: Medium
Chain: Smart contract
Component: Mento
Published: 2025-01-17
Source: https://github.com/hats-finance/Mento-0x2a1b9b1f6fa7c2e73815a7dff0e1688767382694/issues/12
Type: hats-finding

## Details
**Github username:** @tpiliposian
  **Twitter username:** tpiliposian
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/tpiliposian)

  **Beneficiary:** 0x975436CA41E5455839Cd79c1D02c4692361DFB25
  **Submission hash (on-chain):** 0x2eaea6669b78fdfc8dca23b06c853f6a063cc45c6318ea7ae5d2eb846bd24c12
  **Severity:** medium
  
  **Description:**
  **Description**\
The `LockingBase.sol` contract implements incorrect storage slot gap calculation that could impact future upgrades. While other contracts in the project that don't use storage slots have a standard 
```solidity
uint256[50] private __gap;
```
this contract uses storage slots but doesn't properly account for them in its gap calculation.

In a recent [upgrade](https://github.com/mento-protocol/mento-core/pull/542/files#diff-d4fdb204f9c4f7cb85fdd426828decd9b4aa4b1e1256cb6190d95857327ec8bf), 3 new storage slots were added for L2 transition functionality, and the gap was reduced from 50 to 47 slots:
```solidity
  // ***************
  // New variables for L2 transition upgrade (3 slots)
  // ***************
  /**
   * @dev L2 transition block number
   */
  uint256 public l2TransitionBlock;
  /**
   * @dev L2 starting point week number
   */
  int256 public l2StartingPointWeek;
  /**
   * @dev Shift amount used after L2 transition to move the start of the epoch to 00-00 UTC Wednesday (approx)
   */
  uint32 public l2EpochShift;
  /**
   * @dev Address of the Mento Labs multisig
   */
  address public mentoLabsMultisig;
  /**
   * @dev Flag to pause locking and governance
   */
  bool public paused;
```

```diff
-     uint256[50] private __gap;
+    uint256[47] private __gap;
```
However, this adjustment doesn't account for the 9 storage slots that were already in use before this addition, resulting in a total of 59 slots instead of the project's standard 50 slots.

**Attack Scenario**\
This miscalculation introduces risks for future upgrades, like a storage collision may cause contracts to malfunction and compromise other functionalities.

**Attachments**

1. **Proof of Concept (PoC) File**
```solidity
// Current implementation
contract LockingBase is OwnableUpgradeable, IVotesUpgradeable {
    // ... existing state variables using 12 slots ...
    
    uint256[47] private __gap;  // Incorrect gap size
    // Total: 59 slots (12 + 47)
}

// Deployment scenario showing the issue:
1. Other contracts: 0 used slots + 50 gap = 50 total slots
2. LockingBase: 12 used slots + 47 gap = 59 total slots
3. Result: Storage layout inconsistency of 9 slots
```

2. **Revised Code File (Optional)**
Check and update the `__gap`s of the contract:

```diff
-     uint256[47] private __gap;
+    uint256[38] private __gap;
      //please double calculate
```
