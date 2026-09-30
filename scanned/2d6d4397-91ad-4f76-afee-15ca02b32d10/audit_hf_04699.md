# [M] Users are unable to collect their yield if tranche

## Summary
Severity: Medium
Contest weight: 0.5750
Dataset id: 22470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users are unable to collect their yield if Tranche is paused, resulting in a loss of assets for the victims. Thus, any finding showing that the owner/admin can steal a user's funds, cause loss of funds or harm to the users, or cause the user's fund to be struck is valid in Q: Is the admin/owner of the protocol/contracts TRUSTED or RESTRICTED? RESTRICTED The admin of the protocol has the ability to pause the Tranche contract, and no one except for the admin can unpause it. If a malicious admin paused the Tranche contract, the users will not be able to collect their yield earned, leading to a loss of assets for them. e.sol#L605 File: Tranche.sol
```solidity
603:
/// @notice Pause issue, collect and updateUnclaimedYield
604:
/// @dev only callable by management
605:
function pause() external onlyManagement {
606:
    _pause();
607:
}
608:
609:
/// @notice Unpause issue, collect and updateUnclaimedYield
610:
/// @dev only callable by management
611:
function unpause() external onlyManagement {
612:
    _unpause();
613:
}
```
The following shows that the collect function can only be executed when the system is not paused. e.sol#L399 File: Tranche.sol
```solidity
399:
function collect() public nonReentrant whenNotPaused returns (uint256) {
400:
    uint256 _lscale = lscales[msg.sender];
401:
    uint256 accruedInTarget = unclaimedYields[msg.sender];
```
Users are unable to collect their yield if Tranche is paused, resulting in a loss of assets for the victims.

## Recommendation
Consider allowing the users to collect yield even when the system is paused.
