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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Mento-0x2a1b9b1f6fa7c2e73815a7dff0e1688767382694/issues/12_
