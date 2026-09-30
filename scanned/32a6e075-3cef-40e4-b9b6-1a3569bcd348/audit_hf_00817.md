# [M] M-19 | Missing Pause Functionality

## Summary
Severity: Medium
Contest weight: 0.0741
Dataset id: 2553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract PositionManager inherits from PausableUpgradeable but does not implement the onlyOwner functions required to enable this functionality. As a result, the owner is unable to pause/unpause functions that have the whenNotPaused modifier. Additionally, SuperPool contract inherits from Pausable contract, does not use the whenNotPaused or contains the onlyOwner functions.

## Recommendation
To address this issue, it is recommended that pause and unpause functions be added to the PositionManager contract. If SuperPool contract is not meant to have pause functionality, consider removing the inheritance from Pausable.
